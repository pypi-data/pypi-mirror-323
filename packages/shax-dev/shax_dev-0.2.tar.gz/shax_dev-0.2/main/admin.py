from django.contrib import admin
from django.db import models
from unfold.admin import ModelAdmin
from django.apps import apps
from django.contrib.admin.sites import AlreadyRegistered
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group


admin.site.unregister(User)
admin.site.unregister(Group)

app_models = apps.get_models()
print(app_models)
exclude_models = ['Session', 'ContentType', 'Permission', 'Site','Group','User','LogEntry']

# Ilovadagi barcha modellarni olish
app_models = apps.get_models()

# Har bir modelni admin panelga qo'shish
for model in app_models:
    if model.__name__ not in exclude_models:
        try:
            admin.site.register(model)
        except AlreadyRegistered:
            pass