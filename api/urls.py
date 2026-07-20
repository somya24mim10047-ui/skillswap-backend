from django.urls import path
from .views import (
    LoginView,
    RegisterView,
    ProfileView,
    SkillCreateView,
    SkillMatchView,
    SendConnectionRequestView,
    IncomingRequestsView,
    AcceptRequestView,
    RejectRequestView,
    ConnectionsView,
    SendMessageView,
    ConversationView,
)

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("register/", RegisterView.as_view()),
    path("profile/", ProfileView.as_view()),
    path("skills/", SkillCreateView.as_view()),
    path("match/", SkillMatchView.as_view()),

    path("connect/", SendConnectionRequestView.as_view()),
    path("requests/", IncomingRequestsView.as_view()),
    path("accept/<int:pk>/", AcceptRequestView.as_view()),
    path("reject/<int:pk>/", RejectRequestView.as_view()),
    path("connections/", ConnectionsView.as_view()),
    path("messages/send/", SendMessageView.as_view()),
    path("messages/<str:username>/", ConversationView.as_view()),
]