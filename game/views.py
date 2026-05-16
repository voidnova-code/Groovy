from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
import os

from .models import GameRoom, GameMove
from .serializers import (
    UserSerializer,
    GameRoomSerializer,
    MakeMoveSerializer,
    JoinRoomSerializer,
)
from .auth_google import GoogleAuthHandler


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
    if not request.user.is_authenticated:
        return Response({"error": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(["GET"])
def get_razorpay_key(request):
    """Get Razorpay key for frontend"""
    key = os.getenv("RAZORPAY_KEY_ID", "")
    return Response({"key": key})


@api_view(["POST"])
def google_auth_callback(request):
    """
    Handle Google OAuth callback
    Expects: auth_code, redirect_uri, and optional email_to_link for existing users
    """
    auth_code = request.data.get("auth_code")
    redirect_uri = request.data.get("redirect_uri")
    email_to_link = request.data.get("email_to_link")  # For linking to existing account
    
    if not auth_code or not redirect_uri:
        return Response(
            {"error": "Missing auth_code or redirect_uri"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    handler = GoogleAuthHandler()
    user_data, tokens, error = handler.authenticate_with_google(
        auth_code, 
        redirect_uri, 
        email_to_link
    )
    
    if error:
        return Response(
            {"error": error},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    return Response({
        "user": user_data,
        "tokens": tokens
    }, status=status.HTTP_200_OK)


@api_view(["POST"])
def link_google_account(request):
    """
    Link Google account to existing authenticated user
    Expects: auth_code, redirect_uri
    """
    if not request.user.is_authenticated:
        return Response(
            {"error": "Not authenticated"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    auth_code = request.data.get("auth_code")
    redirect_uri = request.data.get("redirect_uri")
    
    if not auth_code or not redirect_uri:
        return Response(
            {"error": "Missing auth_code or redirect_uri"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    handler = GoogleAuthHandler()
    token_data, error = handler.exchange_token(auth_code, redirect_uri)
    
    if error:
        return Response(
            {"error": error},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    access_token = token_data.get('access_token')
    google_info, error = handler.get_user_info(access_token)
    
    if error:
        return Response(
            {"error": error},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    success, message = handler.link_google_to_user(request.user, google_info)
    
    if not success:
        return Response(
            {"error": message},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    return Response({
        "message": message,
        "user": UserSerializer(request.user).data
    }, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_google_auth_config(request):
    """
    Get Google OAuth configuration for frontend
    """
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    if not client_id:
        return Response(
            {"error": "Google OAuth not configured"},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    return Response({
        "client_id": client_id,
        "auth_uri": "https://accounts.google.com/o/oauth2/v2/auth",
        "scopes": ["openid", "email", "profile"]
    }, status=status.HTTP_200_OK)


class GameRoomViewSet(viewsets.ModelViewSet):
    serializer_class = GameRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return GameRoom.objects.select_related('player_x', 'player_o', 'winner').filter(
            player_x=self.request.user
        ) | GameRoom.objects.select_related('player_x', 'player_o', 'winner').filter(player_o=self.request.user)

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
        games = GameRoom.objects.select_related('player_x', 'player_o', 'winner').filter(
            player_x=request.user
        ) | GameRoom.objects.select_related('player_x', 'player_o', 'winner').filter(player_o=request.user)
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

        if room.status not in ["waiting", "playing"]:
            return Response(
                {"error": "Room is not available for joining"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if room.status == "playing":
            return Response(
                {"error": "Game already in progress"},
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
            room = GameRoom.objects.select_related('player_x', 'player_o', 'winner').get(code=room_code)
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

        # Verify user is part of this game and both players are present
        if request.user != room.player_x and request.user != room.player_o:
            return Response(
                {"error": "You are not a player in this game"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not room.player_o:
            return Response(
                {"error": "Game not ready - waiting for opponent"},
                status=status.HTTP_400_BAD_REQUEST
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

        cache.delete(f'game_room_{room_code}')
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

    @action(detail=False, methods=["post"], url_path="auto_reset_game")
    def auto_reset_game(self, request):
        """Auto-reset game for next round with same opponent"""
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

        if request.user != room.player_x and request.user != room.player_o:
            return Response(
                {"error": "You are not in this room"},
                status=status.HTTP_403_FORBIDDEN
            )

        if room.status != "finished":
            return Response(
                {"error": "Game not finished yet"},
                status=status.HTTP_400_BAD_REQUEST
            )

        room.status = "playing"
        room.reset_board()
        room.save()

        cache.delete(f'game_room_{room_code}')
        return Response(GameRoomSerializer(room).data)