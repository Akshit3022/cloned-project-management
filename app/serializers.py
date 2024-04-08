from rest_framework import serializers
from app.models import *
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from app.utils import Util

class RegiterSerializer(serializers.ModelSerializer):
    confirmPass = serializers.CharField()
    class Meta:
        model = CustomUser
        fields = ('email', 'name', 'password', 'confirmPass', 'userType', 'is_active')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'}
            },
        }

    def validate(self, data):
        password = data.get('password')
        confirmPass = data.get('confirmPass')

        if password!= confirmPass:
            raise serializers.ValidationError({'DOES NOT MATCH': 'Password and confirmPass does not match'})
        return data
    
    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)
    

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = CustomUser
        fields = ('email', 'password')


class CustomUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'name')


class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    changePass = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    class meta:
        fields = ('password', 'changePass')

    def validate(self, data):
        password = data.get('password')
        changePass = data.get('changePass')
        user = self.context.get('user')
        if password!= changePass:
            raise serializers.ValidationError({'DOES NOT MATCH': 'Password and changePass does not match'})
        user.set_password(changePass)
        user.save()
        return data
    
class SendResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        fields = ('email')

    def validate(self, data):
        email = data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email=email)
            user_id = urlsafe_base64_encode(force_bytes(user.id))
            print("Encoded id", user_id)
            token = PasswordResetTokenGenerator().make_token(user)
            print("password reset token", token)
            link = 'http://localhost:3000/api/reset/'+user_id+'/'+token
            print("password reset link", link)
            body = 'Click following link to reset password ' + link
            data =  {'subject':'Reset Your Password', 'body':body, 'to_email':user.email}
            Util.send_email(data)
            return data
        else:
            raise serializers.ValidationError({'INVALID EMAIL': 'Eamil does not exists'})
        

class CustomUserResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    resetPass = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    class meta:
        fields = ('password', 'resetPass')

    def validate(self, data):
        try:
            password = data.get('password')
            resetPass = data.get('resetPass')
            user_id = self.context.get('user_id')
            token = self.context.get('token')   
            if password!= resetPass:
                raise serializers.ValidationError({'DOES NOT MATCH': 'Password and resetpass does not match'})
            id = smart_str(urlsafe_base64_decode(user_id))
            user = CustomUser.objects.get(id=id) 
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError({'INVALID TOKEN': 'Token is invalid'})
            user.set_password(resetPass)
            user.save()
            return data
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError({'INVALID TOKEN': 'Token is invalid'})
            
class ProjectCRUDSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        # exclude = ('projectStartDate', )
