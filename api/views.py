from django.contrib.auth.models import User

from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.utils.ai_matcher import calculate_similarity

from .models import Profile, Skill, Connection, Message
from .serializers import (
    ProfileSerializer,
    SkillSerializer,
    ConnectionSerializer,
    MessageSerializer,
)


# ---------------- REGISTER ----------------

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        Profile.objects.create(user=user)

        return Response(
            {"message": "User registered successfully"},
            status=status.HTTP_201_CREATED,
        )


# ---------------- LOGIN ----------------

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        print("Username:", username)
        print("Password:", password)

        user = authenticate(
            username=username,
            password=password
        )

        print("Authenticated User:", user)

        if user is None:
            return Response(
                {"error": "Invalid Username or Password"},
                status=status.HTTP_400_BAD_REQUEST
            )

        token, created = Token.objects.get_or_create(user=user)

        return Response({
            "token": token.key,
            "user_id": user.id,
            "username": user.username
        })


# ---------------- PROFILE ----------------

class ProfileView(generics.RetrieveUpdateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        profile, created = Profile.objects.get_or_create(
            user=self.request.user
        )
        return profile


# ---------------- SKILLS ----------------

class SkillCreateView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = SkillSerializer

    def get_queryset(self):
        return Skill.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        skill_name = serializer.validated_data["name"]

        if Skill.objects.filter(
            user=self.request.user,
            name__iexact=skill_name,
        ).exists():
            raise ValidationError(
                {"error": "Skill already exists."}
            )

        serializer.save(user=self.request.user)


# ---------------- AI MATCHING ----------------

class SkillMatchView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        current_user = request.user

        current_skills = Skill.objects.filter(user=current_user)

        current_skill_text = " ".join(
            f"{skill.name} {skill.description or ''}"
            for skill in current_skills
        )

        matches = []

        users = User.objects.exclude(id=current_user.id)

        for user in users:

            user_skills = Skill.objects.filter(user=user)

            skill_text = " ".join(
                f"{skill.name} {skill.description or ''}"
                for skill in user_skills
            )

            if not skill_text:
                continue

            score = calculate_similarity(
                current_skill_text,
                skill_text
            )

            matches.append({
                "username": user.username,
                "similarity": round(score * 100, 2),
                "skills": [
                    {
                        "name": skill.name,
                        "description": skill.description,
                    }
                    for skill in user_skills
                ],
            })

        matches.sort(
            key=lambda x: x["similarity"],
            reverse=True,
        )

        return Response(matches)


# ---------------- SEND CONNECTION ----------------

class SendConnectionRequestView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        username = request.data.get("username")

        try:
            receiver = User.objects.get(username=username)

        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=404
            )

        if receiver == request.user:
            return Response(
                {"error": "Cannot connect to yourself"},
                status=400
            )

        if Connection.objects.filter(
            sender=request.user,
            receiver=receiver
        ).exists():
            return Response(
                {"error": "Request already sent"}
            )

        Connection.objects.create(
            sender=request.user,
            receiver=receiver,
            status="pending"
        )

        return Response({
            "message": "Connection Request Sent"
        })


# ---------------- INCOMING REQUESTS ----------------

class IncomingRequestsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        requests = Connection.objects.filter(
            receiver=request.user,
            status="pending"
        )

        serializer = ConnectionSerializer(
    requests,
    many=True,
    context={"request": request}
)

        return Response(serializer.data)


# ---------------- ACCEPT REQUEST ----------------

class AcceptRequestView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        try:
            connection = Connection.objects.get(
                id=pk,
                receiver=request.user
            )

        except Connection.DoesNotExist:
            return Response(
                {"error": "Request not found"},
                status=404
            )

        connection.status = "accepted"
        connection.save()

        return Response({
            "message": "Connection Accepted"
        })


# ---------------- REJECT REQUEST ----------------

class RejectRequestView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        try:
            connection = Connection.objects.get(
                id=pk,
                receiver=request.user
            )

        except Connection.DoesNotExist:
            return Response(
                {"error": "Request not found"},
                status=404
            )

        connection.status = "rejected"
        connection.save()

        return Response({
            "message": "Connection Rejected"
        })


# ---------------- MY CONNECTIONS ----------------

class ConnectionsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):

        sent = Connection.objects.filter(
            sender=request.user,
            status="accepted"
        )

        received = Connection.objects.filter(
            receiver=request.user,
            status="accepted"
        )

        connections = list(sent) + list(received)

        serializer = ConnectionSerializer(
            connections,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)
class SendMessageView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        username = request.data.get("username")
        content = request.data.get("content")

        if not content:
            return Response(
                {"error": "Message cannot be empty"},
                status=400
            )

        try:
            receiver = User.objects.get(username=username)

        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=404
            )

        Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content
        )

        return Response({
            "message": "Message Sent"
        })
class ConversationView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, username):

        try:
            other_user = User.objects.get(username=username)

        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=404
            )

        messages = Message.objects.filter(
            sender__in=[request.user, other_user],
            receiver__in=[request.user, other_user]
        ).order_by("timestamp")

        serializer = MessageSerializer(messages, many=True)

        return Response(serializer.data)