from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from accounts.models import CustomUser
from mypage.models import UserProfile
from django.db import connection
from datetime import datetime
from django.db import transaction

class RegisterSerializer(serializers.ModelSerializer):
    """
    User registration serializer.
    Handles the creation of new user accounts with validation.
    """
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    
    # Define additional fields
    gender = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    age_group = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    nickname = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    selected_tags = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'password2', 
                  'gender', 'age_group', 'nickname', 'selected_tags')

    def validate(self, attrs):
        """
        Validate user registration data.
        Ensures passwords match and meet Django's password requirements.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        try:
            validate_password(attrs['password'])
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
            
        return attrs

    def create(self, validated_data):
        """
        Create a new user with validated data.
        Handles password setting and proper cleanup of additional fields.
        """
        password = validated_data.pop('password')
        password2 = validated_data.pop('password2', None)  # Remove password2 field if it exists
        
        try:
            # Process with transaction to maintain consistency
            with transaction.atomic():
                # 1. Create user (password not yet set)
                user = CustomUser.objects.create(**validated_data)
                
                # 2. Clean up existing UserProfile related to user
                try:
                    UserProfile.objects.filter(user_id=user.id).delete()
                except Exception:
                    pass
                
                # 3. Create UserProfile directly (no signals)
                # If nickname info exists, copy it to UserProfile
                profile_data = {'user': user}
                if hasattr(user, 'nickname') and user.nickname:
                    profile_data['nickname'] = user.nickname
                
                profile = UserProfile.objects.create(**profile_data)
                
                # 4. Set password and final save
                user.set_password(password)
                
                # This save triggers signals, but we handle them in the signal handler (already UserProfile exists)
                user.save(update_fields=['password'])
            
            return user
            
        except IntegrityError as e:
            error_msg = str(e)
            if 'username' in error_msg.lower():
                raise serializers.ValidationError({"username": "Username already in use."})
            elif 'email' in error_msg.lower():
                raise serializers.ValidationError({"email": "Email already registered."})
            raise serializers.ValidationError({"error": str(e)})

class UserProfileDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for providing detailed user profile information.
    Used for public profile viewing.
    """
    username = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    introduction = serializers.CharField(source='bio', read_only=True)
    profile_image = serializers.SerializerMethodField()
    date_joined = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = ('username', 'gender', 'age', 'introduction', 'profile_image', 'date_joined')
        
    def get_username(self, obj):
        return obj.user.username
        
    def get_gender(self, obj):
        if obj.user.gender:
            return obj.user.get_gender_display()
        return None
        
    def get_age(self, obj):
        if obj.user.age_group:
            return obj.user.get_age_group_display()
        return None
    
    def get_profile_image(self, obj):
        if obj.profile_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
            return obj.profile_image.url
        return None
        
    def get_date_joined(self, obj):
        return obj.user.date_joined
