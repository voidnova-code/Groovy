import random
import string
from django.db import models
from django.contrib.auth.models import User


def default_board_state():
    return ["", "", "", "", "", "", "", "", ""]


class GameRoom(models.Model):
    STATUS_CHOICES = [
        ("waiting", "Waiting for opponent"),
        ("playing", "Game in progress"),
        ("finished", "Game finished"),
    ]

    code = models.CharField(max_length=6, unique=True, editable=False)
    player_x = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="games_as_x"
    )
    player_o = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="games_as_o", null=True, blank=True
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="waiting")
    winner = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="wins"
    )
    is_draw = models.BooleanField(default=False)
    current_turn = models.CharField(max_length=1, default="X")
    board_state = models.JSONField(default=default_board_state)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_unique_code()
        if not self.board_state or len(self.board_state) != 9:
            self.board_state = default_board_state()
        super().save(*args, **kwargs)

    def reset_board(self):
        self.board_state = default_board_state()
        self.current_turn = "X"
        self.winner = None
        self.is_draw = False

    def generate_unique_code(self):
        while True:
            code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not GameRoom.objects.filter(code=code).exists():
                return code

    def check_winner(self):
        winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        for combo in winning_combinations:
            if (self.board_state[combo[0]] and
                self.board_state[combo[0]] == self.board_state[combo[1]] ==
                self.board_state[combo[2]]):
                return combo
        return None

    def check_draw(self):
        return len(self.board_state) == 9 and all(cell != "" for cell in self.board_state)

    def make_move(self, position, player):
        if self.status != "playing":
            return False, "Game is not in progress"

        if position < 0 or position > 8:
            return False, "Invalid position"

        if self.board_state[position] != "":
            return False, "Cell already occupied"

        expected_symbol = "X" if self.current_turn == "X" else "O"
        if (player == self.player_x and expected_symbol != "X") or \
           (player == self.player_o and expected_symbol != "O"):
            return False, "Not your turn"

        self.board_state[position] = self.current_turn

        winner_combo = self.check_winner()
        if winner_combo:
            self.status = "finished"
            self.winner = player
        elif self.check_draw():
            self.status = "finished"
            self.is_draw = True
        else:
            self.current_turn = "O" if self.current_turn == "X" else "X"

        self.save()
        return True, "Move successful"

    def __str__(self):
        return f"Room {self.code} - {self.status}"


class GameMove(models.Model):
    room = models.ForeignKey(GameRoom, on_delete=models.CASCADE, related_name="moves")
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    position = models.IntegerField()
    symbol = models.CharField(max_length=1)
    move_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.username} played {self.symbol} at position {self.position}"