from django.contrib import admin

from .models import Board, Log, Node

admin.site.register(Board)
admin.site.register(Log)
admin.site.register(Node)

# Register your models here.
