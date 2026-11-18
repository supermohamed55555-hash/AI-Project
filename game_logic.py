"""
game_logic.py
Core game rules and state management for XO (Tic-Tac-Toe).
"""

from typing import List, Optional, Tuple

HUMAN = 'X'
AI = 'O'
EMPTY = ' '

# All possible winning line combinations on a 3x3 board
WINNING_COMBINATIONS = [
    (0, 1, 2),  # Row 0
    (3, 4, 5),  # Row 1
    (6, 7, 8),  # Row 2
    (0, 3, 6),  # Col 0
    (1, 4, 7),  # Col 1
    (2, 5, 8),  # Col 2
    (0, 4, 8),  # Main diagonal
    (2, 4, 6),  # Anti diagonal
]


class Board:
    """Represents a 3x3 Tic-Tac-Toe board."""

    def __init__(self, state: Optional[List[str]] = None):
        if state is None:
            self.cells = [EMPTY] * 9
        else:
            self.cells = list(state)

    def is_empty(self, index: int) -> bool:
        """Check if a specific cell is empty."""
        return self.cells[index] == EMPTY

    def make_move(self, index: int, player: str) -> bool:
        """Place a player's mark on the cell if empty."""
        if 0 <= index < 9 and self.cells[index] == EMPTY:
            self.cells[index] = player
            return True
        return False

    def undo_move(self, index: int) -> None:
        """Undo a move by clearing the cell."""
        if 0 <= index < 9:
            self.cells[index] = EMPTY

    def get_legal_moves(self) -> List[int]:
        """Return a list of empty cell indices (0-8)."""
        return [i for i, cell in enumerate(self.cells) if cell == EMPTY]

    def check_winner(self) -> Tuple[Optional[str], Optional[Tuple[int, int, int]]]:
        """
        Check if there is a winner.
        Returns:
            (winner_mark, winning_trio_indices) if a player has 3 in a row.
            (None, None) if no winner yet.
        """
        for a, b, c in WINNING_COMBINATIONS:
            if self.cells[a] != EMPTY and self.cells[a] == self.cells[b] == self.cells[c]:
                return self.cells[a], (a, b, c)
        return None, None

    def is_full(self) -> bool:
        """Check if all cells are filled."""
        return EMPTY not in self.cells

    def is_draw(self) -> bool:
        """Game is draw if board is full and nobody won."""
        winner, _ = self.check_winner()
        return winner is None and self.is_full()

    def is_terminal(self) -> bool:
        """Game is over if someone won or it is a draw."""
        winner, _ = self.check_winner()
        return winner is not None or self.is_full()

    def clone(self) -> 'Board':
        """Return a deep copy of the board."""
        return Board(self.cells)

    def reset(self) -> None:
        """Reset board to all empty."""
        self.cells = [EMPTY] * 9
