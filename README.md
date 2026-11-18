# XO (Tic-Tac-Toe) AI Project with Minimax & Alpha-Beta Pruning

**Arab Academy for Science, Technology and Maritime Transport (AASTMT)**  
**College of Computing and Information Technology**  
**Course:** Introduction to Artificial Intelligence (CAI3101 & CS366)  
**Submission:** ZIP file containing code + report

---

## 🎮 Features Included
- **Game Engine (`game_logic.py`):**
  - Standard $3 \times 3$ Tic-Tac-Toe rules.
  - Legal move generation, win check, and draw detection.
  - Identification of winning line coordinates to highlight them on the board.
- **AI Engine (`ai.py`):**
  - **Minimax Algorithm:** Recursive search that counts visited nodes.
  - **Alpha-Beta Pruning:** Recursive search with alpha/beta cut-offs visiting significantly fewer nodes while finding the exact same move.
  - **Difficulty Levels:**
    - **Easy:** Random empty cell.
    - **Medium:** Depth limit of 2 with heuristic evaluation function.
    - **Hard:** Full search to the end of the game (unbeatable).
- **GUI Application (`gui.py` & `main.py`):**
  - Built with native `tkinter` (no external dependencies required).
  - Choice of who plays first (Human 'X' or Computer 'O').
  - Choice of Algorithm (Minimax vs Alpha-Beta).
  - Choice of Level (Easy, Medium, Hard).
  - Live AI Telemetry: Last Move Cell, Nodes Visited, and Execution Time in ms.
  - Status updates, winning line highlight, and **New Game** button.
  - Match scoreboard (Human vs AI vs Draws).
- **Automated Verification Benchmark (`test_ai.py`):**
  - Automated comparison script comparing Minimax and Alpha-Beta across different game scenarios.
- **Academic Report (`REPORT.md`):**
  - Full report structured for the 6 team members and grading criteria.

---

## 🚀 How to Run

1. Make sure Python 3.8+ is installed on your computer.
2. Open a terminal or command prompt inside this project folder:
   ```bash
   python main.py
   ```
3. To run the automated algorithm verification benchmark:
   ```bash
   python test_ai.py
   ```

---

## 👥 Team Breakdown (6 Members)
Check `REPORT.md` to customize student names and IDs before submitting the ZIP file.
