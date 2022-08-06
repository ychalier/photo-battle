from pyexpat import model
from django.contrib import admin
from . import models

admin.site.register(models.Team)
admin.site.register(models.Battle)
admin.site.register(models.Photo)
admin.site.register(models.Vote)
admin.site.register(models.Result)
