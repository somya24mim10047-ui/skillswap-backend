from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    bio = models.TextField(blank=True)

    profile_picture = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    location = models.CharField(
        max_length=100,
        blank=True
    )

    education = models.CharField(
        max_length=200,
        blank=True
    )

    profession = models.CharField(
        max_length=200,
        blank=True
    )

    linkedin = models.URLField(blank=True)

    github = models.URLField(blank=True)

    EXPERIENCE_CHOICES = [
        ("Beginner", "Beginner"),
        ("Intermediate", "Intermediate"),
        ("Expert", "Expert"),
    ]

    experience = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        default="Beginner"
    )

    def __str__(self):
        return self.user.username


class Skill(models.Model):

    SKILL_TYPES = [
        ("HAVE", "Have"),
        ("WANT", "Want"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="skills"
    )

    name = models.CharField(max_length=100)

    description = models.TextField(blank=True)

    skill_type = models.CharField(
        max_length=10,
        choices=SKILL_TYPES,
        default="HAVE",
    )

    def __str__(self):
        return f"{self.name} ({self.skill_type})"
    
class Connection(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]

    sender = models.ForeignKey(
        User,
        related_name="sent_connections",
        on_delete=models.CASCADE
    )

    receiver = models.ForeignKey(
        User,
        related_name="received_connections",
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("sender", "receiver")

    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username} ({self.status})"
class Message(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )

    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="received_messages"
    )

    content = models.TextField()

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}"