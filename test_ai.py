"""
test_ai.py
Automated test and benchmark script comparing Minimax vs Alpha-Beta Pruning.
Generates verification data and comparison metrics for the project report.
"""

from game_logic import Board, HUMAN, AI
from ai import XOAI


def run_benchmark():
    ai = XOAI()

    test_boards = [
        # Scenario 1: Empty board (initial move)
        ("Empty Board (Move 1)", Board()),

        # Scenario 2: Human made first move in center
        ("Center Occupied by X", Board([
            ' ', ' ', ' ',
            ' ', 'X', ' ',
            ' ', ' ', ' '
        ])),

        # Scenario 3: Human threat to win
        ("Human Threat (X has 2 in row)", Board([
            'X', 'X', ' ',
            'O', ' ', ' ',
            ' ', ' ', ' '
        ])),

        # Scenario 4: AI opportunity to win
        ("AI Win Opportunity (O has 2 in col)", Board([
            'O', 'X', ' ',
            'O', 'X', ' ',
            ' ', ' ', ' '
        ])),

        # Scenario 5: Mid-game fork defense
        ("Mid Game (Depth 4)", Board([
            'X', ' ', ' ',
            ' ', 'O', ' ',
            ' ', ' ', 'X'
        ]))
    ]

    print("=" * 80)
    print("XO AI BENCHMARK: MINIMAX vs ALPHA-BETA PRUNING (Hard Level - Full Search)")
    print("=" * 80)
    print(f"{'Scenario':<35} | {'Algo':<12} | {'Move':<5} | {'Nodes':<8} | {'Time (ms)':<9}")
    print("-" * 80)

    for name, board in test_boards:
        # Run Minimax
        move_mini, nodes_mini, time_mini = ai.get_best_move(board.clone(), algorithm="Minimax", level="Hard")

        # Run Alpha-Beta
        move_ab, nodes_ab, time_ab = ai.get_best_move(board.clone(), algorithm="Alpha-Beta", level="Hard")

        print(f"{name:<35} | {'Minimax':<12} | {str(move_mini):<5} | {nodes_mini:<8} | {time_mini:<9.2f}")
        print(f"{'':<35} | {'Alpha-Beta':<12} | {str(move_ab):<5} | {nodes_ab:<8} | {time_ab:<9.2f}")

        # Verification check
        assert move_mini == move_ab, f"Discrepancy detected in {name}: Minimax picked {move_mini}, AB picked {move_ab}"
        reduction = ((nodes_mini - nodes_ab) / nodes_mini) * 100 if nodes_mini > 0 else 0
        print(f"  --> Move Match: PASS (Move={move_ab}) | Pruning Reduction: {reduction:.1f}% fewer nodes visited!\n")

    print("=" * 80)
    print("All verification tests passed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    run_benchmark()
