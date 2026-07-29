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
        fields = ["id", "name", "description"]


# PROFILE
class ProfileSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(source="user.skills", many=True, read_only=True)

    class Meta:
        model = Profile
        fields = ["id", "user", "bio", "skills"]
        read_only_fields = ["id", "user", "skills"]

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