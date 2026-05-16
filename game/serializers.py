from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import EmailValidator
from .models import GameRoom, GameMove


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=True)
    username = serializers.CharField(validators=[UnicodeUsernameValidator()])

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
        read_only_fields = ["id"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        return user


class GameMoveSerializer(serializers.ModelSerializer):
    player_username = serializers.CharField(source="player.username", read_only=True)

    class Meta:
        model = GameMove
        fields = ["id", "player", "player_username", "position", "symbol", "move_number", "created_at"]
        read_only_fields = ["id", "player", "player_username", "symbol", "move_number", "created_at"]


class GameRoomSerializer(serializers.ModelSerializer):
    player_x_username = serializers.CharField(source="player_x.username", read_only=True)
    player_o_username = serializers.CharField(source="player_o.username", read_only=True)
    winner_username = serializers.CharField(source="winner.username", read_only=True)

    class Meta:
        model = GameRoom
        fields = [
            "id", "code", "player_x", "player_x_username",
            "player_o", "player_o_username", "status",
            "winner", "winner_username", "is_draw",
            "current_turn", "board_state", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "code", "player_x", "status", "winner", "is_draw", "board_state", "created_at", "updated_at"]


class MakeMoveSerializer(serializers.Serializer):
    room_code = serializers.CharField(max_length=6)
    position = serializers.IntegerField(min_value=0, max_value=8)


class JoinRoomSerializer(serializers.Serializer):
    room_code = serializers.CharField(max_length=6)