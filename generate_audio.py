"""
generate_audio.py
Pre-generates high-quality Native Arabic voice lines using Google's Neural Arabic TTS.
Saves them into the audio/ directory for 100% offline, native Arabic playback!
"""

import os
from gtts import gTTS

AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

# List of Arabic Voice Lines to Pre-generate
AUDIO_LINES = {
    # Start lines
    "start_1": "يلا يا بطل.. وريني هتعمل إيه قدام خوارزمية مينيمكس!",
    "start_2": "ابدأ أنت الأول.. بس خلي بالك، النهاية محسومة للكمبيوتر!",
    "start_3": "الذكاء الاصطناعي جاهز للمعركة.. جاهز للخسارة يا بشمهندس؟",
    "start_ai_1": "أنا هبدأ الأول عشان أوريك اللعب الصح بيتعمل إزاي!",
    "start_ai_2": "الكمبيوتر بيبدأ أولاً.. بداية النهاية بالنسبة لك يا هندسة!",

    # Moves
    "move_0": "المربع رقم صفر دا بتاعي خلاص.. وريني هتلعب فين بقى!",
    "move_1": "المربع رقم واحد دا بتاعي خلاص.. وريني هتلعب فين بقى!",
    "move_2": "المربع رقم اثنين دا بتاعي خلاص.. وريني هتلعب فين بقى!",
    "move_3": "المربع رقم ثلاثة دا بتاعي خلاص.. وريني هتلعب فين بقى!",
    "move_4": "المربع السحري في المنتصف بتاعي.. وريني هتلعب فين بقى!",
    "move_5": "المربع رقم خمسة دا بتاعي خلاص.. وريني هتلعب فين بقى!",
    "move_6": "المربع رقم ستة دا بتاعي خلاص.. وريني هتلعب فين بقى!",
    "move_7": "المربع رقم سبعة دا بتاعي خلاص.. وريني هتلعب فين بقى!",
    "move_8": "المربع رقم ثمانية دا بتاعي خلاص.. وريني هتلعب فين بقى!",

    "threat_1": "سايب المربع دا مكشوف كدا ليه؟ شكلك مستغني عن الجيم!",
    "threat_2": "كش ملك يا فنان! خطوتين والجيم يخلص في ثواني!",
    "threat_3": "وقعت في الفخ بتاعي خلاص.. مفيش مفر يا هندسة!",

    # Game Over
    "win_ai_1": "مبروك عليا الفوز! الرياضيات والذكاء الاصطناعي مبيخسروش!",
    "win_ai_2": "جيم أوفر يا هندسة! مينيمكس لا يُهزم أبداً!",
    "win_human": "إيه دا؟! مستحيل تكون كسبتني! أكيد في خطأ في الكود!",
    "draw_1": "تعادل! لا برافو عليك.. عرفت تقفل الجيم صح قدامي!",
    "draw_2": "تعادل عادل.. مفيش ولا غلطة على اللوحة.. شابوه يا بطل!"
}

def main():
    print("Generating Native Arabic Voice Audio Files...")
    for key, text in AUDIO_LINES.items():
        out_file = os.path.join(AUDIO_DIR, f"{key}.mp3")
        if not os.path.exists(out_file):
            print(f"Generating {key}: {text}")
            tts = gTTS(text=text, lang="ar")
            tts.save(out_file)
        else:
            print(f"Skipping {key} (already exists)")
    print("All Arabic audio files generated successfully!")

if __name__ == "__main__":
    main()
