# Board Games with Minimax & Alpha-Beta Pruning: XO (Tic-Tac-Toe)

**Arab Academy for Science, Technology and Maritime Transport (AASTMT)**  
**College of Computing and Information Technology**  
**Course:** Introduction to Artificial Intelligence (CAI3101 & CS366)  
**Lecturers:** Prof. Saleh Haridy, Eng. Yaser Shaban, Eng. Nagham Haiman  

---

## 1. Project Overview & Game Chosen
We selected **Game 1: XO (Tic-Tac-Toe)**.  
The application implements an interactive human-versus-computer board game on a $3 \times 3$ grid. The user plays as **'X'** while the computer AI plays as **'O'**.  

### Game Rules:
- The board consists of 9 cells (indexed $0$ to $8$).
- Players alternate turns placing their mark in an empty cell.
- The first player to align 3 consecutive marks horizontally, vertically, or diagonally wins the game.
- If all 9 cells are filled and neither player has achieved 3 in a row, the outcome is declared a **Draw**.
- When a victory is achieved, the 3 winning cells are visually highlighted.

---

## 2. Program Architecture & Code Structure
The software is engineered with a modular, decoupled architecture adhering to software engineering best practices:

```
AI Project/
│
├── game_logic.py          # Core game state, move mechanics, win/draw condition detection
├── ai.py                  # AI Engine: Minimax, Alpha-Beta Pruning, Heuristic Evaluation
├── gui.py                 # Modern Tkinter Graphical User Interface with telemetry & speech bubble
├── voice_engine.py        # Asynchronous Voice & Trash-Talk Engine (Audio commentary & Sarcasm)
├── camera_controller.py   # Neural Hand & Finger Tracking (MediaPipe Deep Learning Model)
├── hand_landmarker.task   # Google's 21-point 3D Hand Landmarker Neural Network Model
├── main.py                # Application entry point
├── test_ai.py             # Automated test benchmark (validates Minimax vs Alpha-Beta)
├── REPORT.md              # Comprehensive Academic Project Report
└── README.md              # Setup and user guide
```

### Module Responsibilities:
1. **`game_logic.py` (`Board` class):**
   - Pure representation of the $3 \times 3$ board state as a flat array of 9 elements.
   - Provides methods for legal move retrieval (`get_legal_moves()`), making moves, undoing moves, deep cloning, and terminal state verification (`check_winner()`, `is_draw()`, `is_terminal()`).
   - Returns the exact tuple of winning cell indices (e.g. `(0, 4, 8)`) for GUI highlighting.

2. **`ai.py` (`XOAI` class):**
   - Implements both recursive search algorithms with an internal `nodes_visited` telemetry counter.
   - Measures decision latency with microsecond precision (`time.perf_counter()`).
   - Implements difficulty level dispatching (**Easy**, **Medium**, **Hard**).

3. **`gui.py` (`TicTacToeGUI` class):**
   - Built using Python's native `tkinter` library.
   - Card-based layout featuring:
     - Pre-game configuration panel: First Player (`Human` vs `Computer`), Algorithm (`Minimax` vs `Alpha-Beta`), Difficulty (`Easy`, `Medium`, `Hard`).
     - Interactive board with cell index notation ($0$ to $8$) in the corner of each cell.
     - Live AI telemetry panel displaying chosen cell, nodes visited, and execution time in milliseconds.
     - Dynamic turn banner and scoreboard tracking cumulative match records.
     - Instant **"New Game"** reset functionality.

4. **`voice_engine.py` (BONUS: Talking AI with Voice & Trash-Talk):**
   - Uses asynchronous background threading to deliver real-time sarcastic and tactical audio commentary.
   - Features speech bubble updates directly on the interface, reacting to blunders, tactical forks, draws, and victories.

5. **`camera_controller.py` (BONUS: Precision Neural Hand Air-Control):**
   - Powered by Google MediaPipe Tasks HandLandmarker deep learning neural network.
   - Tracks the exact 21 anatomical landmarks of the hand with millimeter precision, immune to background walls, faces, or lighting.
   - Supports Pinch-to-Click and Dwell Hover selection in the air.

---

## 3. Algorithm Deep-Dive

### 3.1 Standard Minimax Algorithm
Minimax is a recursive, backtracking adversarial search algorithm. The AI acts as the **Maximizer** (aiming to maximize the score for 'O'), while the Human acts as the **Minimizer** (aiming to minimize the score for 'X').

#### Mathematical Formulation:
$$\text{Minimax}(s, d) = \begin{cases} 
\text{Utility}(s, d) & \text{if } \text{Terminal}(s) \text{ or } d \ge d_{\max} \\
\max_{a \in \text{Actions}(s)} \text{Minimax}(\text{Result}(s, a), d+1) & \text{if Player}(s) = \text{AI (O)} \\
\min_{a \in \text{Actions}(s)} \text{Minimax}(\text{Result}(s, a), d+1) & \text{if Player}(s) = \text{Human (X)}
\end{cases}$$

To encourage the AI to win as quickly as possible and delay human wins as long as possible, depth is factored into terminal utility:
- **AI Win:** $+100 - \text{depth}$
- **Human Win:** $-100 + \text{depth}$
- **Draw:** $0$

---

### 3.2 Alpha-Beta Pruning
Alpha-Beta pruning optimizes Minimax by skipping branches that cannot influence the final decision.
- $\alpha$: The highest (best) value that the Maximizer is guaranteed so far.
- $\beta$: The lowest (best) value that the Minimizer is guaranteed so far.

#### Pruning Condition:
If at any node $\beta \le \alpha$, the remaining child branches are pruned (**Cut-off**):
- **Beta cut-off (in Maximizer):** The Minimizer at an ancestor level already has a move that yields a smaller or equal value, so it would never allow this state.
- **Alpha cut-off (in Minimizer):** The Maximizer at an ancestor level already has a move yielding a larger or equal value.

**Crucial Property:** Alpha-Beta Pruning **always** returns the exact same optimal move as Minimax, but evaluates significantly fewer nodes ($O(b^{d/2})$ in the best case vs $O(b^d)$).

---

## 4. Difficulty Levels & Heuristic Evaluation Function

| Level | Search Depth ($d_{\max}$) | Algorithm & Mechanics | Behavior |
| :--- | :---: | :--- | :--- |
| **Easy** | $0$ | `random.choice(legal_moves)` | Completely random moves. Ideal for beginners or casual play. |
| **Medium** | $2$ | Depth-limited search with Heuristic Evaluation | Looks 2 moves ahead (1 human ply + 1 AI reply). Makes strategic moves but can be trapped. |
| **Hard** | $\le 9$ (Full Search) | Unbounded search to terminal states | **Optimal / Unbeatable.** Will win if given an opening, and forces at least a draw otherwise. |

### The Heuristic Evaluation Function (Medium Level)
When the search reaches depth limit $d = 2$ before a terminal state, an evaluation function estimates board favorability:
$$\text{Heuristic Score} = S_{\text{lines}} + S_{\text{position}}$$

1. **Line Threats ($S_{\text{lines}}$):** Evaluates all 8 winning lines:
   - Line with 2 'O's and 1 empty cell: $+10$ (immediate winning threat for AI)
   - Line with 2 'X's and 1 empty cell: $-10$ (immediate threat from human to block)
   - Line with 1 'O' and 2 empty cells: $+2$
   - Line with 1 'X' and 2 empty cells: $-2$
2. **Positional Weighting ($S_{\text{position}}$):**
   - Center cell (index 4): $+3$ for 'O', $-3$ for 'X'
   - Corner cells (indices 0, 2, 6, 8): $+1$ for 'O', $-1$ for 'X'

---

## 5. Experimental Verification: Minimax vs Alpha-Beta Pruning
An automated benchmark (`test_ai.py`) evaluated identical board states under both algorithms at **Hard Level (Full Search)**:

| Scenario / Board State | Minimax Move | Minimax Nodes | Alpha-Beta Move | Alpha-Beta Nodes | Pruning Efficiency (% Node Reduction) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Empty Board (Move 1)** | 0 | 549,945 | 0 | 20,865 | **96.2% fewer nodes** |
| **Center Occupied (Move 2)** | 0 | 55,504 | 0 | 2,458 | **95.6% fewer nodes** |
| **Human 2-in-a-row Threat** | 2 | 1,018 | 2 | 81 | **92.0% fewer nodes** |
| **AI Win Opportunity** | 6 | 156 | 6 | 62 | **60.3% fewer nodes** |
| **Fork Defense (Depth 4)** | 1 | 1,052 | 1 | 355 | **66.3% fewer nodes** |

### Key Findings:
1. **Identical Decision:** In 100% of cases, Minimax and Alpha-Beta returned the exact same move.
2. **Exponential Efficiency:** Alpha-Beta pruned up to **96.2%** of the state space, maintaining sub-millisecond decision times without any sacrifice in optimality.

---

## 6. Team Task Allocation (6 Members)

| Member Name | Student ID | Assigned Responsibilities |
| :--- | :---: | :--- |
| **Student 1 (Team Leader)** | *[Insert ID]* | System architecture design, `main.py`, project integration & review. |
| **Student 2** | *[Insert ID]* | Game rules, state representation, win/draw logic (`game_logic.py`). |
| **Student 3** | *[Insert ID]* | Standard Minimax algorithm implementation & node profiling (`ai.py`). |
| **Student 4** | *[Insert ID]* | Alpha-Beta Pruning optimization & cut-off conditions (`ai.py`). |
| **Student 5** | *[Insert ID]* | Difficulty levels (Easy, Medium, Hard) & heuristic evaluation function design. |
| **Student 6** | *[Insert ID]* | GUI design, Telemetry dashboard, Audio Trash-Talk Engine & Camera HCI integration. |

---

## 7. How to Run the Application

### Prerequisites:
- Python 3.8+ installed.
- Standard libraries + `pyttsx3`, `opencv-python`, `mediapipe`.

### Running the App:
```bash
python main.py
```

### Running the Automated Algorithm Benchmark:
```bash
python test_ai.py
```
