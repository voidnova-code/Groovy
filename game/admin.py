from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.urls import path
from django.shortcuts import render
from django.utils.html import format_html

from .models import GameRoom, GameMove


class GameRoomAdmin(admin.ModelAdmin):
    list_display = ('code', 'player_x', 'player_o', 'status', 'get_winner', 'is_draw', 'created_at')
    list_filter = ('status', 'is_draw', 'created_at')
    search_fields = ('code', 'player_x__username', 'player_o__username')
    readonly_fields = ('code', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 20

    def get_winner(self, obj):
        if obj.winner:
            return obj.winner.username
        return '-'
    get_winner.short_description = 'Winner'

    fieldsets = (
        ('Room Info', {
            'fields': ('code', 'status', 'created_at', 'updated_at')
        }),
        ('Players', {
            'fields': ('player_x', 'player_o')
        }),
        ('Game Result', {
            'fields': ('winner', 'is_draw')
        }),
        ('Game State', {
            'fields': ('current_turn', 'board_state')
        }),
    )


class GameMoveAdmin(admin.ModelAdmin):
    list_display = ('room', 'player', 'position', 'symbol', 'move_number', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('room__code', 'player__username')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 20


# Register models
admin.site.register(GameRoom, GameRoomAdmin)
admin.site.register(GameMove, GameMoveAdmin)

# Customize admin header
admin.site.site_header = 'GROOVY Tic Tac Toe Admin'
admin.site.site_title = 'GROOVY Admin'
admin.site.index_title = 'Dashboard'