from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from .models import ADMIN, CANDIDATE, RECRUITER, Candidate, Recruiter

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_email_verified",
            "is_active",
            "phone",
            "profile_picture",
            "date_joined",
        ]
        read_only_fields = ["id", "is_email_verified", "is_active", "date_joined"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "role",
            "phone",
            "profile_picture",
        ]

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_role(self, value):
        allowed = {CANDIDATE, RECRUITER, ADMIN}
        if value not in allowed:
            raise serializers.ValidationError("Invalid role.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Create role-specific profile
        if user.role == RECRUITER:
            Recruiter.objects.create(user=user)
        elif user.role == CANDIDATE:
            Candidate.objects.create(user=user)

        return user


class RecruiterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recruiter
        fields = ["id", "user", "company_name", "company_website", "company_description"]
        read_only_fields = ["id", "user"]

    def validate(self, attrs):
        user = (
            attrs.get("user")
            or getattr(self.instance, "user", None)
            or getattr(self.context.get("request"), "user", None)
        )
        if not user:
            raise serializers.ValidationError({"user": "User is required."})
        if user.role != RECRUITER:
            raise serializers.ValidationError({"user": "Only recruiter users can have recruiter data."})
        if hasattr(user, "candidate"):
            raise serializers.ValidationError({"user": "This user is already a candidate."})
        return attrs


class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ["id", "user", "resume", "skills", "experience_years"]
        read_only_fields = ["id", "user"]

    def validate(self, attrs):
        user = (
            attrs.get("user")
            or getattr(self.instance, "user", None)
            or getattr(self.context.get("request"), "user", None)
        )
        if not user:
            raise serializers.ValidationError({"user": "User is required."})
        if user.role != CANDIDATE:
            raise serializers.ValidationError({"user": "Only candidate users can have candidate data."})
        if hasattr(user, "recruiter"):
            raise serializers.ValidationError({"user": "This user is already a recruiter."})
        return attrs


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")
        if not user.is_active:
            raise serializers.ValidationError("Account is inactive.")

        attrs["user"] = user
        return attrs
