from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from autho.models import Merchant

User = get_user_model()

class MerchantSerializer(serializers.ModelSerializer):
    """ represents  Company/Organization"""

    class Meta:
        model = Merchant
        fields = ['id', 'name', 'description', 'email' ,'address', 'is_active' , 'phone_number']
        read_only_fields = ['id']

class UserCreateSerializer(serializers.ModelSerializer):
    """ Used for creating new users with password validation and role assignment. """
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields =[
            "id",
            "username",
            "email",
            "password",
            "confirm_password",
            'merchant',
            'display_name',
        ]
        read_only_fields = ['id']

    def validate(self,data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("passwords do not match")
        
        validate_password(data['password'])
        return data
    
    def create(self , validated_data):
        password = validated_data.pop('password')
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data) #
        user.set_password(password)
        user.save()
        return user
    
class UserDetailSerializer(serializers.ModelSerializer):
    """ Used for Profile / user Detail API """
    merchant = serializers.PrimaryKeyRelatedField(queryset=Merchant.objects.all(), required=False) # Show merchant ID in user details, but allow it to be null or blank

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "merchant",
            "display_name",
        ]

class UserLoginSerializer(serializers.Serializer):
    """Used for Login Response(not authentication)"""
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)  
    token = serializers.CharField(read_only=True)

    def to_representation(self, instance):
        """ customize the  login response to """
        return {
            "id": instance.id,
            "username": instance.username,
            "email": instance.email,
            "token": self.context.get('token')  # Include the token in the response
        }
    
class UserUpdateSerializer(serializers.ModelSerializer):
    """ Update User Profile"""
    class Meta:
        model = User
        fields = [
            "username" ,
            "email",
            'display_name',
        ]
    
    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.display_name = validated_data.get('display_name', instance.display_name)
        instance.save()
        return instance