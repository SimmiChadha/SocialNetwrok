from rest_framework.decorators import APIView
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .serializers import UserSerializer, LoginUserSerializer


class RegisterUser(APIView):

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    
    
class LoginUser(APIView):
    
    def post(self, request, format=None):
        serializer = LoginUserSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            user = authenticate(email=email, password=password)
            if user:
                token = user.get_tokens
                return Response({'token':token, 'email':user.email, 'id':user.id, 'msg':'Success'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
            
                
