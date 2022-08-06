import random
from django.db import models
from django.urls import reverse
from django.conf import settings


BATTLE_CODE_LENGTH = 16
BATTLE_CODE_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


class Team(models.Model):

    name = models.CharField(max_length=100, unique=True)
    date_creation = models.DateTimeField(auto_now=False, auto_now_add=True)

    class Meta:

        ordering = ["name"]

    def __str__(self):
        return self.name


class Battle(models.Model):

    STATE_REGISTRATION = "I"
    STATE_UPLOADING = "U"
    STATE_VOTING = "V"
    STATE_CLOSED = "C"
    STATE_CHOICES = [
        (STATE_REGISTRATION, "Inscription"),
        (STATE_UPLOADING, "Rendu des photos"),
        (STATE_VOTING, "Vote"),
        (STATE_CLOSED, "Terminé")
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    teams = models.ManyToManyField("Team", blank=True, related_name="battles")
    code = models.CharField(max_length=BATTLE_CODE_LENGTH, null=True, blank=True, unique=True)
    state = models.CharField(max_length=1, choices=STATE_CHOICES, default=STATE_REGISTRATION)
    photo_count = models.PositiveIntegerField(default=3)
    date_creation = models.DateTimeField(auto_now=False, auto_now_add=True)
    date_upload = models.DateTimeField(null=True, blank=True)
    date_vote = models.DateTimeField(null=True, blank=True)
    date_closed = models.DateTimeField(null=True, blank=True)

    class Meta:

        ordering = ["-date_creation"]
    
    def __str__(self):
        return f"[{ self.get_state_display() }] { self.title }"

    def save(self, *args, **kwargs):
        if self.code is None or self.code == "":
            self.code = "".join([random.choice(BATTLE_CODE_CHARS) for _ in range(BATTLE_CODE_LENGTH)])
        return super(Battle, self).save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse("photobattle:view_battle", args=[self.code])
    
    def photos_by_team(self):
        result = { team: [] for team in self.teams.all() }
        for photo in self.photos.all():
            result[photo.team].append(photo)
        return result
    
    def photos_shuffled(self):
        arr = list(self.photos.all())
        random.shuffle(arr)
        return arr

    def photos_ranked(self):
        return self.photos.order_by("-grade")


class Photo(models.Model):
    """Image to be hosted on https://imgbb.com/.
    """

    battle = models.ForeignKey(Battle, on_delete=models.CASCADE, related_name="photos")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="photos")
    date_creation = models.DateTimeField(auto_now=False, auto_now_add=True)
    url = models.URLField()
    url_thumbnail = models.URLField()
    grade = models.FloatField(null=True, blank=True)

    class Meta:

        ordering = ["-date_creation"]

    def __str__(self):
        return f"{ self.battle } - { self.team } - { self.date_creation }"
    
    def grade_scaled(self):
        if self.grade is None:
            return 0
        else:
            return round(self.grade * 5)


class Vote(models.Model):

    battle = models.ForeignKey(Battle, on_delete=models.CASCADE, related_name="votes")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="votes")
    ranking = models.TextField()
    date_creation = models.DateTimeField(auto_now=False, auto_now_add=True)

    class Meta:

        ordering = ["-date_creation"]

    def __str__(self):
        return f"{ self.battle } - { self.team } - { self.date_creation }"


class Result(models.Model):

    battle = models.ForeignKey(Battle, on_delete=models.CASCADE, related_name="results")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="results")
    rank = models.PositiveIntegerField()
    grade = models.FloatField()
    date_creation = models.DateTimeField(auto_now=False, auto_now_add=True)

    class Meta:

        ordering = ["-battle", "rank"]

    def __str__(self):
        return f"{ self.battle } - { self.team } - { self.rank } ({ self.grade })"
