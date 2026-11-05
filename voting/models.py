from django.conf import settings
from django.db import models


class Position(models.Model):
    title = models.CharField(max_length=100)
    is_open = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class Candidate(models.Model):
    position = models.ForeignKey(
        Position, on_delete=models.CASCADE, related_name='candidates'
    )
    name = models.CharField(max_length=100)
    manifesto = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.position})"


class Vote(models.Model):
    voter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['voter', 'position'], name='one_vote_per_position'
            )
        ]