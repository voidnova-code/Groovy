from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
import os

from .models import GameRoom, GameMove
from .serializers import (
    UserSerializer,
    GameRoomSerializer,
    MakeMoveSerializer,
    JoinRoomSerializer,
)


@api_view(["POST"])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserSerializer(user).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if not username or not password:
        return Response(
            {"error": "Please provide both username and password"},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.check_password(password):
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken.for_user(user)
    return Response({
        "user": UserSerializer(user).data,
        "tokens": {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
    })


@api_view(["POST"])
def logout(request):
    try:
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({"message": "Successfully logged out"})
    except Exception:
        return Response({"message": "Logged out"})


@api_view(["GET"])
def get_current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(["GET"])
def get_razorpay_key(request):
    """Get Razorpay key for frontend"""
    key = os.getenv("RAZORPAY_KEY_ID", "")
    return Response({"key": key})


class GameRoomViewSet(viewsets.ModelViewSet):
    serializer_class = GameRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GameRoom.objects.filter(
            player_x=self.request.user
        ) | GameRoom.objects.filter(player_o=self.request.user)

    def create(self, request):
        existing_waiting = GameRoom.objects.filter(
            player_x=request.user, status="waiting"
        ).first()
        if existing_waiting:
            return Response(
                GameRoomSerializer(existing_waiting).data,
                status=status.HTTP_200_OK
            )

        room = GameRoom.objects.create(player_x=request.user)
        return Response(
            GameRoomSerializer(room).data,
            status=status.HTTP_201_CREATED
        )

    def list(self, request):
        waiting_rooms = GameRoom.objects.filter(status="waiting").exclude(
            player_x=request.user
        )
        serializer = GameRoomSerializer(waiting_rooms, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def my_games(self, request):
        games = GameRoom.objects.filter(
            player_x=request.user
        ) | GameRoom.objects.filter(player_o=request.user)
        games = games.order_by("-updated_at")
        serializer = GameRoomSerializer(games, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="join")
    def join_room(self, request):
        serializer = JoinRoomSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        room_code = serializer.validated_data["room_code"]
        try:
            room = GameRoom.objects.get(code=room_code)
        except GameRoom.DoesNotExist:
            return Response(
                {"error": "Room not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if room.player_x == request.user:
            return Response(
                {"error": "You cannot join your own room"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if room.player_o and room.player_o != request.user:
            return Response(
                {"error": "Room is full"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if room.status != "waiting":
            return Response(
                {"error": "Room is not available for joining"},
                status=status.HTTP_400_BAD_REQUEST
            )

        room.player_o = request.user
        room.status = "playing"
        room.save()

        return Response(GameRoomSerializer(room).data)

    @action(detail=False, methods=["get"])
    def get_room(self, request):
        room_code = request.query_params.get("code")
        if not room_code:
            return Response(
                {"error": "Room code is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            room = GameRoom.objects.get(code=room_code)
        except GameRoom.DoesNotExist:
            return Response(
                {"error": "Room not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = GameRoomSerializer(room)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="move")
    def make_move(self, request):
        serializer = MakeMoveSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        room_code = serializer.validated_data["room_code"]
        position = serializer.validated_data["position"]

        try:
            room = GameRoom.objects.get(code=room_code)
        except GameRoom.DoesNotExist:
            return Response(
                {"error": "Room not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.user != room.player_x and request.user != room.player_o:
            return Response(
                {"error": "You are not a player in this game"},
                status=status.HTTP_403_FORBIDDEN
            )

        success, message = room.make_move(position, request.user)
        if not success:
            return Response(
                {"error": message},
                status=status.HTTP_400_BAD_REQUEST
            )

        symbol = "X" if request.user == room.player_x else "O"
        move_count = GameMove.objects.filter(room=room).count() + 1
        GameMove.objects.create(
            room=room,
            player=request.user,
            position=position,
            symbol=symbol,
            move_number=move_count
        )

        return Response(GameRoomSerializer(room).data)

    @action(detail=False, methods=["delete"], url_path="delete")
    def delete_room(self, request):
        """Delete a game room - only the creator can delete"""
        room_code = request.query_params.get("code")
        if not room_code:
            return Response(
                {"error": "Room code is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            room = GameRoom.objects.get(code=room_code)
        except GameRoom.DoesNotExist:
            return Response(
                {"error": "Room not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Only the creator (player_x) can delete the room
        if request.user != room.player_x:
            return Response(
                {"error": "You can only delete your own rooms!"},
                status=status.HTTP_403_FORBIDDEN
            )

        room.delete()
        return Response({"message": "Room deleted successfully!"})