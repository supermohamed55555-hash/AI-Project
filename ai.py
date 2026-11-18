"""
ai.py
Artificial Intelligence engine for XO (Tic-Tac-Toe).
Implements Minimax and Alpha-Beta Pruning with node counting,
time measurement, and difficulty levels (Easy, Medium, Hard).
"""

import math
import random
import time
from typing import Optional, Tuple
from game_logic import AI, EMPTY, HUMAN, WINNING_COMBINATIONS, Board


class XOAI:
    """AI engine managing search algorithms, node counting, and heuristics."""

    def __init__(self):
        self.nodes_visited = 0

    def evaluate_board(self, board: Board, depth: int) -> int:
        """
        Heuristic evaluation function.
        Used at terminal states or when search hits the depth limit (e.g. Medium level).
        Positive score favors AI ('O'), negative score favors Human ('X').
        """
        winner, _ = board.check_winner()
        if winner == AI:
            return 100 - depth
        elif winner == HUMAN:
            return -100 + depth
        elif board.is_full():
            return 0

        # Non-terminal heuristic evaluation (for depth-limited search)
        score = 0

        # Position weights (center is most valuable, then corners)
        cell_weights = {
            4: 3,        # Center
            0: 1, 2: 1, 6: 1, 8: 1,  # Corners
            1: 0, 3: 0, 5: 0, 7: 0   # Edges
        }

        for idx, weight in cell_weights.items():
            if board.cells[idx] == AI:
                score += weight
            elif board.cells[idx] == HUMAN:
                score -= weight

        # Evaluate potential lines
        for a, b, c in WINNING_COMBINATIONS:
            line = [board.cells[a], board.cells[b], board.cells[c]]
            ai_count = line.count(AI)
            human_count = line.count(HUMAN)
            empty_count = line.count(EMPTY)

            # Two marks and one empty (potential winning threat)
            if ai_count == 2 and empty_count == 1:
                score += 10
            elif human_count == 2 and empty_count == 1:
                score -= 10
            # One mark and two empty
            elif ai_count == 1 and empty_count == 2:
                score += 2
            elif human_count == 1 and empty_count == 2:
                score -= 2

        return score

    # -------------------------------------------------------------------------
    # 1. Standard Minimax Algorithm
    # -------------------------------------------------------------------------
    def minimax(self, board: Board, depth: int, max_depth: int, is_maximizing: bool) -> int:
        """
        Standard Minimax algorithm without pruning.
        Explores all branches up to max_depth.
        """
        self.nodes_visited += 1

        # Check terminal state or reached depth limit
        if board.is_terminal() or depth >= max_depth:
            return self.evaluate_board(board, depth)

        if is_maximizing:
            max_eval = -math.inf
            for move in board.get_legal_moves():
                board.make_move(move, AI)
                evaluation = self.minimax(board, depth + 1, max_depth, False)
                board.undo_move(move)
                max_eval = max(max_eval, evaluation)
            return max_eval
        else:
            min_eval = math.inf
            for move in board.get_legal_moves():
                board.make_move(move, HUMAN)
                evaluation = self.minimax(board, depth + 1, max_depth, True)
                board.undo_move(move)
                min_eval = min(min_eval, evaluation)
            return min_eval

    # -------------------------------------------------------------------------
    # 2. Alpha-Beta Pruning Algorithm
    # -------------------------------------------------------------------------
    def alpha_beta(
        self,
        board: Board,
        depth: int,
        max_depth: int,
        alpha: float,
        beta: float,
        is_maximizing: bool
    ) -> int:
        """
        Minimax algorithm with Alpha-Beta Pruning.
        Prunes branches that cannot affect the final decision.
        """
        self.nodes_visited += 1

        # Check terminal state or reached depth limit
        if board.is_terminal() or depth >= max_depth:
            return self.evaluate_board(board, depth)

        if is_maximizing:
            max_eval = -math.inf
            for move in board.get_legal_moves():
                board.make_move(move, AI)
                evaluation = self.alpha_beta(board, depth + 1, max_depth, alpha, beta, False)
                board.undo_move(move)
                max_eval = max(max_eval, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break  # Beta cut-off / pruning
            return max_eval
        else:
            min_eval = math.inf
            for move in board.get_legal_moves():
                board.make_move(move, HUMAN)
                evaluation = self.alpha_beta(board, depth + 1, max_depth, alpha, beta, True)
                board.undo_move(move)
                min_eval = min(min_eval, evaluation)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break  # Alpha cut-off / pruning
            return min_eval

    # -------------------------------------------------------------------------
    # Move Selection Entry Point
    # -------------------------------------------------------------------------
    def get_best_move(
        self,
        board: Board,
        algorithm: str = "Alpha-Beta",
        level: str = "Hard"
    ) -> Tuple[Optional[int], int, float]:
        """
        Computes the best move for AI based on selected algorithm and difficulty level.
        Returns:
            (best_move_index, nodes_visited, time_taken_ms)
        """
        legal_moves = board.get_legal_moves()
        if not legal_moves:
            return None, 0, 0.0

        # Start timing
        start_time = time.perf_counter()
        self.nodes_visited = 0

        # Level 1: Easy (random move)
        if level == "Easy":
            self.nodes_visited = 1
            chosen_move = random.choice(legal_moves)
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return chosen_move, self.nodes_visited, round(elapsed_ms, 2)

        # Set search depth limit based on level
        # Medium = depth limit 2 (as specified in project requirements)
        # Hard = full search (depth limit 9)
        max_depth = 2 if level == "Medium" else 9

        best_move = legal_moves[0]
        best_val = -math.inf
        alpha = -math.inf
        beta = math.inf

        use_alpha_beta = (algorithm == "Alpha-Beta")

        for move in legal_moves:
            board.make_move(move, AI)

            if use_alpha_beta:
                move_val = self.alpha_beta(
                    board, depth=1, max_depth=max_depth,
                    alpha=alpha, beta=beta, is_maximizing=False
                )
                board.undo_move(move)
                if move_val > best_val:
                    best_val = move_val
                    best_move = move
                alpha = max(alpha, best_val)
            else:
                move_val = self.minimax(
                    board, depth=1, max_depth=max_depth, is_maximizing=False
                )
                board.undo_move(move)
                if move_val > best_val:
                    best_val = move_val
                    best_move = move

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        return best_move, self.nodes_visited, round(elapsed_ms, 2)
