from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from user.serializers import CustomUserSchema, CustomUserDetailSchema, CustomUserRequestSchema, LikesSerializer
from user.models import CustomUser
from recipe.models import Recipe

import json
# from django.contrib.sessions.models import Session

def main_page(request):
    return render(request,'index.html')

@csrf_exempt
def set_access(request):
    if request.method == 'POST':
        request.session['access_allowed'] = True
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSchema
    serializer_classes = {
        "list": CustomUserSchema,
        "retrive": CustomUserDetailSchema,
        "create": CustomUserRequestSchema,
        "update": CustomUserRequestSchema,
        "partial_update": CustomUserRequestSchema,
        "destroy": CustomUserRequestSchema,
    }

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.serializer_class)        

    @action(detail=True, methods=['POST', 'DELETE'], url_path='like') # 같은url에 메소드만 다르면 이렇게도 가능 근데 이렇게 않하면 now allowed 에러남.
    def like_create(self, request, **kwargs):
        user_id = kwargs.get('pk')
        recipe_id = request.data['recipe_id']
        user_instance = CustomUser.objects.get(id=user_id)
        recipe_instance = Recipe.objects.get(id=recipe_id)
        
        if request.method == 'POST':
            user_instance.like.add(recipe_instance)
            status_code = 201

        elif request.method == 'DELETE':
            user_instance.like.remove(recipe_instance)
            status_code = 204

        user_instance.save()
        
        data = {"recipe_id":recipe_instance.id}
        json_data = json.dumps(data)
        
        return Response(status=status_code, data=json_data, content_type="application/json")
        
    @action(detail=False, methods=['POST',], url_path='login')
    def login(self, request, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            return Response({'detail': '로그인 성공'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': '인증 실패'}, status=status.HTTP_401_UNAUTHORIZED)


    @action(detail=False, methods=['POST',], url_path='logout')
    def logout(self, request, **kwargs):
        
        # for k,v in request.session.items():
        #     print(f"key:{k}, value:{v}")

        # session_id = request.data['sessionid']
        # sessions = Session.objects.all()

        # 특정 세션 키로 세션 데이터 조회
        # session = Session.objects.get(session_key=session_id)
        # print(f"session:{session.session_key}, session_value:{session.session_data}")

        # (or to be more precise, the connection to the current browser, 
        # as identified by the session id in the browser's cookie for this site).
        # request.session.clear() # 세션데이터만 삭제
        request.session.flush() # clear + 세션관련 db도 삭제

        # 로그아웃 메시지
        return Response({"message": "로그아웃 성공"}, status=status.HTTP_200_OK)


    # 이와 같이 detail=False로 두고 pk를 파라미터로 지정안하는 방식으로도 가능하기는 함. 만약에 함수를 post, delete 두개로 정의하려면
    # @action(detail=False, methods=['DELETE'], url_path='like') # delete는 detail False로 해야함
    # def like_delete(self, request, *kwargs):
    #     user_instance = CustomUser.objects.get(id=request.data['user_id'])
    #     recipe_instance = Recipe.objects.get(id=request.data['recipe_id'])
    #     user_instance.like.remove(recipe_instance)
    #     user_instance.save()

    #     data = {"recipe_id":recipe_instance.id}
    #     json_data = json.dumps(data)

    #     return Response(status=204, data=json_data, content_type="application/json")

# class LikesViewSet(viewsets.ModelViewSet):
#     queryset = Likes.objects.all()
    
#     serializer_class = LikesSerializer
