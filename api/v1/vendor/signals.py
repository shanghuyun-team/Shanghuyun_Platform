from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission, Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from wagtail.models import Page, GroupPagePermission
