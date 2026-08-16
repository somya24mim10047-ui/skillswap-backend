from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Skill, Connection, Message


# USER
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


# SKILL
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = [
            "id",
            "name",
            "description",
            "skill_type",
        ]

# PROFILE
class ProfileSerializer(serializers.ModelSerializer):

    have_skills = serializers.SerializerMethodField()
    want_skills = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "bio",
            "location",
            "education",
            "profession",
            "experience",
            "linkedin",
            "github",
            "profile_picture",
            "have_skills",
            "want_skills",
        ]

    def get_have_skills(self, obj):
        skills = Skill.objects.filter(
            user=obj.user,
            skill_type="HAVE"
        )

        return SkillSerializer(skills, many=True).data

    def get_want_skills(self, obj):
        skills = Skill.objects.filter(
            user=obj.user,
            skill_type="WANT"
        )

        return SkillSerializer(skills, many=True).data
    
# CONNECTION
class ConnectionSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Connection
        fields = [
            "id",
            "username",
            "status",
        ]

    def get_username(self, obj):
        request = self.context.get("request")

        if not request:
            return None

        if obj.sender == request.user:
            return obj.receiver.username
        else:
            return obj.sender.username


# MESSAGE
class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(
        source="sender.username",
        read_only=True
    )

    receiver = serializers.CharField(
        source="receiver.username",
        read_only=True
    )

    class Meta:
        model = Message
        fields = [
            "id",
            "sender",
            "receiver",
            "content",
            "timestamp",
        ]