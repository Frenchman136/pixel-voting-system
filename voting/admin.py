from django.contrib import admin
from .models import Position, Candidate


class CandidateInline(admin.TabularInline):
    model = Candidate
    extra = 2


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_open')
    inlines = [CandidateInline]