from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from .models import ADMIN, CANDIDATE, RECRUITER, Candidate, Recruiter, WorkDetails

User = get_user_model()

class workDetailsSerialiser(serializers.ModelSerializer):
    class Meta:
        model = WorkDetails
        fields = ["id", "company_name", "designation", "start_date", "end_date", "currently_working", "is_active"]
        read_only_fields = ["id"]


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
            "mobile",
            "image",
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
            "mobile",
            "image",
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
        return user


class RecruiterSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='organisation_name', required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Recruiter
        fields = ["id", "company_name"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        user = (
            self.instance
            or getattr(self.context.get("request"), "user", None)
        )
        if not user:
            raise serializers.ValidationError({"detail": "User context is required."})
        if user.role and user.role.code != "RECRUITER":
             raise serializers.ValidationError({"detail": "User does not have Recruiter role."})
        return attrs


class CandidateSerializer(serializers.ModelSerializer):
    work_experience = workDetailsSerialiser(many=True, read_only=True)
    resume = serializers.FileField(source='cv', required=False, allow_null=True)
    experience_years = serializers.IntegerField(source='experience_yrs', required=False, allow_null=True)

    class Meta:
        model = Candidate
        fields = ["id", "resume", "experience_years", "work_experience", "work_details", "bio", "linkedin", "gender", "age", "current_ctc", "expected_ctc"]
        read_only_fields = ["id", "work_experience"]

    def validate(self, attrs):
        user = (
            self.instance
            or getattr(self.context.get("request"), "user", None)
        )
        if not user:
            raise serializers.ValidationError({"detail": "User context is required."})
        # If user is a proxy/User, check the role field
        if user.role and user.role.code != "CANDIDATE":
             raise serializers.ValidationError({"detail": "User does not have Candidate role."})
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
