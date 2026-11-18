"""
gui.py
Graphical User Interface for XO (Tic-Tac-Toe) using Tkinter.
Features:
- Responsive, modern card-based design matching the assignment specification.
- Controls for starting player, AI algorithm (Minimax vs Alpha-Beta), and level (Easy, Medium, Hard).
- 3x3 grid with subtle cell indexing (0-8) and winning line highlight.
- Live telemetry panel showing last AI move, nodes visited, and search time.
- Win/Loss/Draw counter and New Game functionality without app restart.
- BONUS 1: Precision Neural Camera Air-Control Mode (MediaPipe Hand Landmark Tracking).
- BONUS 2: Sarcastic Talking AI with Voice & Trash-Talk Engine.
"""

import threading
import tkinter as tk
from tkinter import font as tkfont, messagebox
from game_logic import AI, EMPTY, HUMAN, Board
from ai import XOAI
from voice_engine import AIVoiceEngine, TTS_AVAILABLE

try:
    from camera_controller import CV_AVAILABLE, CameraGestureController
except ImportError:
    CV_AVAILABLE = False
    CameraGestureController = None


class TicTacToeGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("XO (Tic-Tac-Toe) - AI Minimax & Alpha-Beta with Voice & Vision")
        self.root.geometry("900x620")
        self.root.minsize(860, 580)
        self.root.configure(bg="#f8fafc")

        # Core Game State
        self.board = Board()
        self.ai = XOAI()
        self.current_turn = HUMAN
        self.game_over = False
        self.winning_line = None

        # Camera Mode State
        self.camera_controller = None
        self.camera_active = False

        # Voice Trash-Talk Engine
        self.voice_engine = AIVoiceEngine(enabled=True)
        self.voice_enabled = True

        # Cumulative Scoreboard
        self.score_human = 0
        self.score_ai = 0
        self.score_draw = 0

        # Settings Variables
        self.first_player_var = tk.StringVar(value="Human")
        self.algo_var = tk.StringVar(value="Alpha-Beta")
        self.level_var = tk.StringVar(value="Hard")

        # Telemetry Variables
        self.last_move_str = tk.StringVar(value="--")
        self.nodes_visited_str = tk.StringVar(value="--")
        self.time_taken_str = tk.StringVar(value="--")
        self.status_text_var = tk.StringVar(value="Your turn (X)")
        self.speech_bubble_var = tk.StringVar(value="🤖 الذكاء الاصطناعي: 'جاهز للمعركة يا بطل!'")

        self._init_fonts()
        self._build_layout()
        self.start_new_game()

    def _init_fonts(self):
        self.title_font = tkfont.Font(family="Segoe UI", size=13, weight="bold")
        self.section_font = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.label_font = tkfont.Font(family="Segoe UI", size=9)
        self.bold_label_font = tkfont.Font(family="Segoe UI", size=9, weight="bold")
        self.speech_font = tkfont.Font(family="Segoe UI", size=9, slant="italic")
        self.mark_font = tkfont.Font(family="Segoe UI", size=32, weight="bold")
        self.index_font = tkfont.Font(family="Segoe UI", size=8)
        self.status_font = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        self.stat_val_font = tkfont.Font(family="Segoe UI", size=12, weight="bold")

    def _build_layout(self):
        # Main Header
        header = tk.Frame(self.root, bg="#ffffff", height=45, bd=1, relief="solid")
        header.pack(fill="x", side="top", padx=0, pady=0)

        header_lbl = tk.Label(
            header,
            text="XO (Tic-Tac-Toe) - Artificial Intelligence Project",
            font=self.title_font,
            fg="#1e293b",
            bg="#ffffff"
        )
        header_lbl.pack(side="left", padx=16, pady=8)

        # Header Right Controls (Camera & Voice Buttons)
        right_btns = tk.Frame(header, bg="#ffffff")
        right_btns.pack(side="right", padx=16, pady=6)

        # Voice Toggle Button
        self.voice_btn = tk.Button(
            right_btns,
            text="🔊 صوت الروبوت: شغال",
            font=self.bold_label_font,
            fg="#ffffff",
            bg="#0284c7",
            activebackground="#0369a1",
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=10,
            pady=4,
            command=self._toggle_voice_mode
        )
        self.voice_btn.pack(side="right", padx=(8, 0))

        # Camera Mode Button
        self.cam_btn = tk.Button(
            right_btns,
            text="📷 Camera Air-Control",
            font=self.bold_label_font,
            fg="#ffffff",
            bg="#059669",
            activebackground="#047857",
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=10,
            pady=4,
            command=self._toggle_camera_mode
        )
        self.cam_btn.pack(side="right")

        # Content Container (3 columns: Left Settings, Center Board, Right Telemetry)
        content = tk.Frame(self.root, bg="#f8fafc")
        content.pack(fill="both", expand=True, padx=16, pady=12)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=2)
        content.columnconfigure(2, weight=1)
        content.rowconfigure(0, weight=1)

        # ----------------- COLUMN 1: LEFT SETTINGS PANEL -----------------
        left_card = tk.Frame(content, bg="#ffffff", bd=1, relief="solid")
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)

        # 1. Who plays first
        f1 = tk.Frame(left_card, bg="#ffffff")
        f1.pack(fill="x", padx=14, pady=(12, 6))
        tk.Label(f1, text="Who plays first", font=self.section_font, fg="#0f172a", bg="#ffffff").pack(anchor="w")
        rb_h = tk.Radiobutton(
            f1, text="Human (X)", variable=self.first_player_var, value="Human",
            bg="#ffffff", activebackground="#ffffff", font=self.label_font
        )
        rb_h.pack(anchor="w", pady=(3, 0))
        rb_c = tk.Radiobutton(
            f1, text="Computer (O)", variable=self.first_player_var, value="Computer",
            bg="#ffffff", activebackground="#ffffff", font=self.label_font
        )
        rb_c.pack(anchor="w")

        # 2. Algorithm
        f2 = tk.Frame(left_card, bg="#ffffff")
        f2.pack(fill="x", padx=14, pady=6)
        tk.Label(f2, text="Algorithm", font=self.section_font, fg="#0f172a", bg="#ffffff").pack(anchor="w")
        rb_mini = tk.Radiobutton(
            f2, text="Minimax", variable=self.algo_var, value="Minimax",
            bg="#ffffff", activebackground="#ffffff", font=self.label_font
        )
        rb_mini.pack(anchor="w", pady=(3, 0))
        rb_ab = tk.Radiobutton(
            f2, text="Alpha-Beta", variable=self.algo_var, value="Alpha-Beta",
            bg="#ffffff", activebackground="#ffffff", font=self.label_font
        )
        rb_ab.pack(anchor="w")

        # 3. Level
        f3 = tk.Frame(left_card, bg="#ffffff")
        f3.pack(fill="x", padx=14, pady=6)
        tk.Label(f3, text="Level", font=self.section_font, fg="#0f172a", bg="#ffffff").pack(anchor="w")
        rb_easy = tk.Radiobutton(
            f3, text="Easy (random move)", variable=self.level_var, value="Easy",
            bg="#ffffff", activebackground="#ffffff", font=self.label_font
        )
        rb_easy.pack(anchor="w", pady=(3, 0))
        rb_med = tk.Radiobutton(
            f3, text="Medium (depth 2)", variable=self.level_var, value="Medium",
            bg="#ffffff", activebackground="#ffffff", font=self.label_font
        )
        rb_med.pack(anchor="w")
        rb_hard = tk.Radiobutton(
            f3, text="Hard (full search)", variable=self.level_var, value="Hard",
            bg="#ffffff", activebackground="#ffffff", font=self.label_font
        )
        rb_hard.pack(anchor="w")

        # New Game Button
        btn_frame = tk.Frame(left_card, bg="#ffffff")
        btn_frame.pack(fill="x", padx=14, pady=(12, 10))
        new_game_btn = tk.Button(
            btn_frame,
            text="New Game",
            font=self.section_font,
            fg="#ffffff",
            bg="#2563eb",
            activebackground="#1d4ed8",
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=12,
            pady=8,
            command=self.start_new_game
        )
        new_game_btn.pack(fill="x")

        # ----------------- COLUMN 2: CENTER BOARD PANEL -----------------
        center_card = tk.Frame(content, bg="#ffffff", bd=1, relief="solid")
        center_card.grid(row=0, column=1, sticky="nsew", padx=8, pady=0)

        # AI Speech Bubble Box
        speech_box = tk.Frame(center_card, bg="#f0f9ff", bd=1, relief="solid")
        speech_box.pack(fill="x", padx=20, pady=(12, 6))

        self.speech_bubble_lbl = tk.Label(
            speech_box,
            textvariable=self.speech_bubble_var,
            font=self.speech_font,
            fg="#0369a1",
            bg="#f0f9ff",
            pady=6,
            wraplength=360,
            justify="center"
        )
        self.speech_bubble_lbl.pack()

        # Board Grid Frame
        self.grid_frame = tk.Frame(center_card, bg="#cbd5e1", bd=2, relief="flat")
        self.grid_frame.pack(expand=True, pady=(6, 6))

        self.cell_frames = []
        self.cell_buttons = []

        for i in range(9):
            r, c = divmod(i, 3)
            cell_box = tk.Frame(self.grid_frame, bg="#ffffff", width=95, height=95)
            cell_box.grid(row=r, column=c, padx=2, pady=2)
            cell_box.pack_propagate(False)

            top_bar = tk.Frame(cell_box, bg="#ffffff")
            top_bar.pack(fill="x", side="top", padx=4, pady=(2, 0))
            idx_lbl = tk.Label(top_bar, text=str(i), font=self.index_font, fg="#94a3b8", bg="#ffffff")
            idx_lbl.pack(side="right")

            btn = tk.Button(
                cell_box,
                text="",
                font=self.mark_font,
                fg="#1e293b",
                bg="#ffffff",
                activebackground="#f1f5f9",
                relief="flat",
                bd=0,
                cursor="hand2",
                command=lambda idx=i: self._on_cell_clicked(idx)
            )
            btn.pack(fill="both", expand=True)

            self.cell_frames.append(cell_box)
            self.cell_buttons.append(btn)

        # Status Bar Below Board
        status_box = tk.Frame(center_card, bg="#f1f5f9", bd=1, relief="solid")
        status_box.pack(fill="x", padx=20, pady=(4, 4))
        self.status_lbl = tk.Label(
            status_box,
            textvariable=self.status_text_var,
            font=self.status_font,
            fg="#1e293b",
            bg="#f1f5f9",
            pady=5
        )
        self.status_lbl.pack()

        sub_msg = tk.Label(
            center_card,
            text="click an empty cell (or use Camera Air-Control)",
            font=self.index_font,
            fg="#64748b",
            bg="#ffffff"
        )
        sub_msg.pack(pady=(0, 10))

        # ----------------- COLUMN 3: RIGHT TELEMETRY PANEL -----------------
        right_card = tk.Frame(content, bg="#ffffff", bd=1, relief="solid")
        right_card.grid(row=0, column=2, sticky="nsew", padx=(8, 0), pady=0)

        # Last AI Move Card
        ai_move_box = tk.Frame(right_card, bg="#f8fafc", bd=1, relief="solid")
        ai_move_box.pack(fill="x", padx=14, pady=(12, 8))

        tk.Label(
            ai_move_box,
            text="Last AI move",
            font=self.section_font,
            fg="#0f172a",
            bg="#f8fafc"
        ).pack(anchor="w", padx=10, pady=(8, 4))

        # Cell
        row_cell = tk.Frame(ai_move_box, bg="#f8fafc")
        row_cell.pack(fill="x", padx=10, pady=2)
        tk.Label(row_cell, text="Cell:", font=self.label_font, fg="#475569", bg="#f8fafc").pack(side="left")
        tk.Label(row_cell, textvariable=self.last_move_str, font=self.stat_val_font, fg="#0f172a", bg="#f8fafc").pack(side="right")

        # Nodes Visited
        row_nodes = tk.Frame(ai_move_box, bg="#f8fafc")
        row_nodes.pack(fill="x", padx=10, pady=2)
        tk.Label(row_nodes, text="Nodes visited:", font=self.label_font, fg="#475569", bg="#f8fafc").pack(side="left")
        tk.Label(row_nodes, textvariable=self.nodes_visited_str, font=self.stat_val_font, fg="#2563eb", bg="#f8fafc").pack(side="right")

        # Time
        row_time = tk.Frame(ai_move_box, bg="#f8fafc")
        row_time.pack(fill="x", padx=10, pady=(2, 8))
        tk.Label(row_time, text="Time:", font=self.label_font, fg="#475569", bg="#f8fafc").pack(side="left")
        tk.Label(row_time, textvariable=self.time_taken_str, font=self.stat_val_font, fg="#0f172a", bg="#f8fafc").pack(side="right")

        # Score Tracker Box
        score_box = tk.Frame(right_card, bg="#ffffff", bd=1, relief="solid")
        score_box.pack(fill="x", padx=14, pady=8)

        tk.Label(
            score_box,
            text="Match Score",
            font=self.section_font,
            fg="#0f172a",
            bg="#ffffff"
        ).pack(anchor="w", padx=10, pady=(8, 4))

        self.score_lbl = tk.Label(
            score_box,
            text="Human (X): 0  |  AI (O): 0  |  Draws: 0",
            font=self.index_font,
            fg="#334155",
            bg="#ffffff",
            pady=4
        )
        self.score_lbl.pack(padx=10, pady=(0, 8))

        # Algorithm Analysis Tip Box
        tip_box = tk.Frame(right_card, bg="#eff6ff", bd=1, relief="solid")
        tip_box.pack(fill="x", padx=14, pady=8)
        tk.Label(
            tip_box,
            text="AI Comparison Note:",
            font=self.bold_label_font,
            fg="#1d4ed8",
            bg="#eff6ff"
        ).pack(anchor="w", padx=8, pady=(6, 2))

        tip_msg = (
            "Alpha-Beta pruning visits significantly\n"
            "fewer nodes than Minimax on Hard level\n"
            "while choosing the exact same optimal move."
        )
        tk.Label(
            tip_box,
            text=tip_msg,
            font=self.index_font,
            fg="#1e40af",
            bg="#eff6ff",
            justify="left"
        ).pack(anchor="w", padx=8, pady=(0, 6))

    def _toggle_voice_mode(self):
        """Toggle voice commentary on/off."""
        self.voice_enabled = not self.voice_enabled
        self.voice_engine.enabled = self.voice_enabled
        if self.voice_enabled:
            self.voice_btn.config(text="🔊 صوت الروبوت: شغال", bg="#0284c7")
        else:
            self.voice_btn.config(text="🔇 صوت الروبوت: مقفول", bg="#64748b")

    def _update_speech_bubble(self, spoken_text: str):
        """Update speech bubble text in GUI thread safely."""
        self.root.after(0, lambda: self.speech_bubble_var.set(f"🤖 الذكاء الاصطناعي: \"{spoken_text}\""))

    def _toggle_camera_mode(self):
        """Toggle Camera Gesture Air-Touch mode."""
        if not CV_AVAILABLE or CameraGestureController is None:
            messagebox.showinfo(
                "Camera Mode Info",
                "OpenCV & MediaPipe are required for Camera Mode."
            )
            return

        if self.camera_active:
            if self.camera_controller:
                self.camera_controller.is_running = False
            self.camera_active = False
            self.cam_btn.config(text="📷 Camera Air-Control", bg="#059669")
        else:
            try:
                self.camera_active = True
                self.cam_btn.config(text="🛑 Stop Camera", bg="#dc2626")
                self.camera_controller = CameraGestureController(
                    board=self.board,
                    on_move_callback=self._on_camera_move_selected
                )
                threading.Thread(
                    target=self.camera_controller.start_camera_loop,
                    args=(self._on_camera_closed,),
                    daemon=True
                ).start()
            except Exception as e:
                self.camera_active = False
                self.cam_btn.config(text="📷 Camera Air-Control", bg="#059669")
                messagebox.showerror("Camera Error", f"Could not start camera:\n{e}")

    def _on_camera_move_selected(self, cell_idx: int):
        self.root.after(0, lambda: self._on_cell_clicked(cell_idx))

    def _on_camera_closed(self):
        self.camera_active = False
        self.root.after(0, lambda: self.cam_btn.config(text="📷 Camera Air-Control", bg="#059669"))

    def start_new_game(self):
        """Reset the board and initiate game flow based on settings."""
        self.board.reset()
        self.game_over = False
        self.winning_line = None

        # Reset cell styles and text
        for i in range(9):
            self.cell_buttons[i].config(
                text="",
                state="normal",
                bg="#ffffff",
                activebackground="#f1f5f9"
            )
            self.cell_frames[i].config(bg="#ffffff")

        # Reset Telemetry
        self.last_move_str.set("--")
        self.nodes_visited_str.set("--")
        self.time_taken_str.set("--")

        first_player = self.first_player_var.get()
        ai_starts = (first_player == "Computer")

        # AI Voice Introduction
        self.voice_engine.comment_game_start(ai_starts=ai_starts, on_text_spoken=self._update_speech_bubble)

        if first_player == "Human":
            self.current_turn = HUMAN
            self.status_text_var.set("Your turn (X)")
            self.status_lbl.config(fg="#1e293b", bg="#f1f5f9")
        else:
            self.current_turn = AI
            self.status_text_var.set("Computer is thinking...")
            self.status_lbl.config(fg="#b45309", bg="#fef3c7")
            self.root.after(400, self._perform_ai_move)

    def _on_cell_clicked(self, index: int):
        if self.game_over or self.current_turn != HUMAN:
            return

        if not self.board.is_empty(index):
            return

        # Human places X
        self.board.make_move(index, HUMAN)
        self._update_cell_ui(index, HUMAN)

        if self._check_game_end():
            return

        # Pass turn to AI
        self.current_turn = AI
        self.status_text_var.set("Computer is thinking...")
        self.status_lbl.config(fg="#b45309", bg="#fef3c7")
        self._set_board_interactive(False)

        self.root.after(250, self._perform_ai_move)

    def _perform_ai_move(self):
        if self.game_over:
            return

        algo = self.algo_var.get()
        level = self.level_var.get()

        best_move, nodes, time_ms = self.ai.get_best_move(self.board, algorithm=algo, level=level)

        if best_move is not None:
            self.board.make_move(best_move, AI)
            self._update_cell_ui(best_move, AI)

            self.last_move_str.set(str(best_move))
            self.nodes_visited_str.set(f"{nodes:,}")
            self.time_taken_str.set(f"{time_ms:.1f} ms" if time_ms > 0 else "< 1 ms")

            # Voice commentary after move
            is_threat = self._ai_has_threat()
            self.voice_engine.comment_ai_move(
                cell_idx=best_move, nodes=nodes, is_threat=is_threat,
                on_text_spoken=self._update_speech_bubble
            )

        if self._check_game_end():
            return

        # Pass turn back to Human
        self.current_turn = HUMAN
        self.status_text_var.set("Your turn (X)")
        self.status_lbl.config(fg="#1e293b", bg="#f1f5f9")
        self._set_board_interactive(True)

    def _ai_has_threat(self) -> bool:
        """Check if AI has 2 marks in any line."""
        from game_logic import WINNING_COMBINATIONS
        for a, b, c in WINNING_COMBINATIONS:
            line = [self.board.cells[a], self.board.cells[b], self.board.cells[c]]
            if line.count(AI) == 2 and line.count(EMPTY) == 1:
                return True
        return False

    def _update_cell_ui(self, index: int, player: str):
        color = "#ef4444" if player == HUMAN else "#f59e0b"
        self.cell_buttons[index].config(
            text=player,
            fg=color,
            disabledforeground=color,
            state="disabled"
        )

    def _set_board_interactive(self, enabled: bool):
        if self.game_over:
            return
        for i in range(9):
            if self.board.is_empty(i):
                self.cell_buttons[i].config(state="normal" if enabled else "disabled")

    def _check_game_end(self) -> bool:
        winner, winning_trio = self.board.check_winner()

        if winner is not None:
            self.game_over = True
            self.winning_line = winning_trio
            self._highlight_winner(winning_trio)

            if winner == HUMAN:
                self.status_text_var.set("You win! Congratulations! 🎉")
                self.status_lbl.config(fg="#15803d", bg="#dcfce7")
                self.score_human += 1
                self.voice_engine.comment_game_over("Human", on_text_spoken=self._update_speech_bubble)
            else:
                self.status_text_var.set("Computer wins! 🤖")
                self.status_lbl.config(fg="#b91c1c", bg="#fee2e2")
                self.score_ai += 1
                self.voice_engine.comment_game_over("AI", on_text_spoken=self._update_speech_bubble)

            self._update_scoreboard()
            self._disable_all_cells()
            return True

        if self.board.is_draw():
            self.game_over = True
            self.status_text_var.set("Game Over - It's a Draw! 🤝")
            self.status_lbl.config(fg="#475569", bg="#f1f5f9")
            self.score_draw += 1
            self.voice_engine.comment_game_over("Draw", on_text_spoken=self._update_speech_bubble)
            self._update_scoreboard()
            self._disable_all_cells()
            return True

        return False

    def _highlight_winner(self, trio: tuple):
        for idx in trio:
            self.cell_frames[idx].config(bg="#86efac")
            self.cell_buttons[idx].config(
                bg="#86efac",
                activebackground="#86efac"
            )

    def _disable_all_cells(self):
        for btn in self.cell_buttons:
            btn.config(state="disabled")

    def _update_scoreboard(self):
        txt = f"Human (X): {self.score_human}  |  AI (O): {self.score_ai}  |  Draws: {self.score_draw}"
        self.score_lbl.config(text=txt)
