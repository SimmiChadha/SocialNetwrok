from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

class UserSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only=True)
    
    def create(self, validated_data):
        user = get_user_model().objects.create_user(
            email = validated_data['email'],
            password = validated_data['password'],
            name = validated_data.get('name',""),
        )
        return user
    
    class Meta:
        model = get_user_model()
        fields = ['email','password','name']
        extra_kwargs = {'password':{'write_only':True}}    
        
        
class LoginUserSerializer(serializers.ModelSerializer):
    
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = get_user_model()
        fields = ['email', 'password','id']