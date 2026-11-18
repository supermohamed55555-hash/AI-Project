"""
voice_engine.py
Native Arabic Voice & Trash-Talk Engine for XO (Tic-Tac-Toe).
Plays authentic, studio-quality Native Arabic speech recordings completely OFFLINE!
Uses Windows Multimedia API (mciSendString) for instantaneous, zero-lag playback.
"""

import ctypes
import os
import random
import threading
from typing import Callable, Optional

AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
TTS_AVAILABLE = True


class AIVoiceEngine:
    """Manages Native Arabic voice playback and speech bubble updates."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.last_comment: str = "جاهز للمعركة يا بطل!"
        self._lock = threading.Lock()

        # Arabic Lines with corresponding MP3 audio files
        self.audio_start = [
            ("يلا يا بطل.. وريني هتعمل إيه قدام خوارزمية مينيمكس!", "start_1.mp3"),
            ("ابدأ أنت الأول.. بس خلي بالك، النهاية محسومة للكمبيوتر!", "start_2.mp3"),
            ("الذكاء الاصطناعي جاهز للمعركة.. جاهز للخسارة يا بشمهندس؟", "start_3.mp3"),
        ]

        self.audio_start_ai = [
            ("أنا هبدأ الأول عشان أوريك اللعب الصح بيتعمل إزاي!", "start_ai_1.mp3"),
            ("الكمبيوتر بيبدأ أولاً.. بداية النهاية بالنسبة لك يا هندسة!", "start_ai_2.mp3"),
        ]

        self.audio_threat = [
            ("سايب المربع دا مكشوف كدا ليه؟ شكلك مستغني عن الجيم!", "threat_1.mp3"),
            ("كش ملك يا فنان! خطوتين والجيم يخلص في ثواني!", "threat_2.mp3"),
            ("وقعت في الفخ بتاعي خلاص.. مفيش مفر يا هندسة!", "threat_3.mp3"),
        ]

        self.audio_win_ai = [
            ("مبروك عليا الفوز! الرياضيات والذكاء الاصطناعي مبيخسروش!", "win_ai_1.mp3"),
            ("جيم أوفر يا هندسة! مينيمكس لا يُهزم أبداً!", "win_ai_2.mp3"),
        ]

        self.audio_win_human = [
            ("إيه دا؟! مستحيل تكون كسبتني! أكيد في خطأ في الكود!", "win_human.mp3"),
        ]

        self.audio_draw = [
            ("تعادل! لا برافو عليك.. عرفت تقفل الجيم صح قدامي!", "draw_1.mp3"),
            ("تعادل عادل.. مفيش ولا غلطة على اللوحة.. شابوه يا بطل!", "draw_2.mp3"),
        ]

    def _play_mp3_async(self, mp3_filename: str):
        """Plays the native Arabic MP3 in a background thread."""
        if not self.enabled:
            return

        mp3_path = os.path.join(AUDIO_DIR, mp3_filename)
        if not os.path.exists(mp3_path):
            return

        def _worker():
            with self._lock:
                try:
                    alias = f"ai_voice_{random.randint(100, 999)}"
                    # Stop any previous playback
                    ctypes.windll.winmm.mciSendStringW(f'close all', None, 0, None)
                    # Open and play MP3 via Windows Multimedia API
                    ctypes.windll.winmm.mciSendStringW(f'open "{mp3_path}" type mpegvideo alias {alias}', None, 0, None)
                    ctypes.windll.winmm.mciSendStringW(f'play {alias} wait', None, 0, None)
                    ctypes.windll.winmm.mciSendStringW(f'close {alias}', None, 0, None)
                except Exception as e:
                    print(f"Audio Playback Notice: {e}")

        threading.Thread(target=_worker, daemon=True).start()

    def play_phrase(self, text_arabic: str, mp3_name: str, on_text_spoken: Optional[Callable[[str], None]] = None):
        """Updates UI with Arabic text and plays native Arabic audio."""
        self.last_comment = text_arabic
        if on_text_spoken:
            on_text_spoken(text_arabic)
        self._play_mp3_async(mp3_name)

    def comment_game_start(self, ai_starts: bool = False, on_text_spoken: Optional[Callable[[str], None]] = None):
        choices = self.audio_start_ai if ai_starts else self.audio_start
        txt, mp3 = random.choice(choices)
        self.play_phrase(txt, mp3, on_text_spoken)

    def comment_ai_move(self, cell_idx: int, nodes: int, is_threat: bool = False, on_text_spoken: Optional[Callable[[str], None]] = None):
        if is_threat:
            txt, mp3 = random.choice(self.audio_threat)
        else:
            txt = f"المربع رقم {cell_idx} دا بتاعي خلاص.. وريني هتلعب فين بقى!" if cell_idx != 4 else "المربع السحري في المنتصف بتاعي.. وريني هتلعب فين بقى!"
            mp3 = f"move_{cell_idx}.mp3"
        self.play_phrase(txt, mp3, on_text_spoken)

    def comment_game_over(self, winner: Optional[str], on_text_spoken: Optional[Callable[[str], None]] = None):
        if winner == "AI":
            txt, mp3 = random.choice(self.audio_win_ai)
        elif winner == "Human":
            txt, mp3 = random.choice(self.audio_win_human)
        else:
            txt, mp3 = random.choice(self.audio_draw)
        self.play_phrase(txt, mp3, on_text_spoken)
