from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from recipe.models import Recipe, Ingredient, RecipeIngredientRelation
from recipe.serializers import RecipeSerializer, IngredientSerializer, RecipeIngredientRelationSerializer
from recipe.service import get_recipe_recommand
from django.shortcuts import render
import json
import pandas as pd
from django.http import JsonResponse

df = pd.read_csv("data/ingre_v2.csv", index_col=False)
ingre_data = df['ingre'].to_list()

def recipe_page(request):
    global ingre_data
    # if 'access_allowed' not in request.session:
    #     return redirect('/')
      
    return render(request, 'recipe_page.html',{'ingre_data': json.dumps(ingre_data)})

class RecipePagination(PageNumberPagination): # PageNumberPagination 상속
    page_size = 20

class RecipeViewSet(viewsets.ModelViewSet):
    
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = RecipePagination

    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated]

    #,커스텀 엔드포인트 작성 함수이름이 자동으로 엔드포인트가 됨 detail=True면 id키 받고 아니면 전체리스트(list)
    # @action(detail=False, methods=["post"],url_path="create_with_prepared_ingredients/(?P<ingre>\d+)")  #커스텀action에 인자 넣고싶을때
    # 이때 d는 숫자형인듯
    # @extend_schema(summary="레시피 넣으면서 재료도 manytomany필드 넣기",parameters=[
    #     OpenApiParameter(
    #         name="recipe_name",
    #         type=OpenApiTypes.ANY,
    #         required=True
    #     ),
    # ]
    #     )
    # @action(detail=False, methods=["post"])  #커스텀action에 인자 넣고싶을때
    #page380에 create,list,retriece,update particail_update 내용이 있음.
    def list(self, request):
        queryset = Recipe.objects.all()
        serializer = RecipeSerializer(queryset, many=True)

        # print(RecipeIngredientRelation.objects.all())
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        book = Recipe.objects.get(pk=pk)
        serializer = RecipeSerializer(book)
        return Response(serializer.data)
    
    def create(self,request):
        serializer = RecipeSerializer(data=request.data)
    
        if serializer.is_valid():
            serializer.save()
        
        return Response(status=201, data=serializer.data)
    
    def update(self, request, pk=None): #put
        
        serializer = RecipeSerializer(data=request.data, partial=False)
        
        if serializer.is_valid(raise_exception=True):
            result = serializer.save()
            result_serializer = RecipeSerializer(instance=result) #serializer는 읽기전용, 수정불가능
            data = dict(result_serializer.data)
            n = len(RecipeIngredientRelation.objects.filter(recipe_id=request.data['id']))
            data['preprocessed_ingredients'] = n
            
        return Response(data=data)

    def destroy(self, request,pk=None):
        
        queryset = Recipe.objects.get(pk=pk)
        result = queryset.delete()
        
        data = {"ingredients": result[1]['recipe.RecipeIngredientRelation'], "recipe":result[1]['recipe.Recipe']}
        
        return Response(status=204, data=data)
    
    @action(detail=False, methods=['POST'])
    def recipe_rec(self, request):

        try:
            parsed_data = json.loads(request.body)  # JSON 데이터 파싱
            ingre = []
            weight = []
            for data in parsed_data:
                ingre.append(data['values'])
                weight.append(data['range'])

            n = 60
            recipe = get_recipe_recommand(ingre, weight, n)
            return Response({'data': recipe}, status=status.HTTP_200_OK)
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]


class RecipeIngredientRelationViewSet(viewsets.ModelViewSet):
    queryset = RecipeIngredientRelation.objects.all()
    serializer_class = RecipeIngredientRelationSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
