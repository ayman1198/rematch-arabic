# -*- coding: utf-8 -*-
"""
Generate energetic Arabic match callout voice files using edge-tts and vgmstream.
Outputs high-quality WAV files directly into arabic_voice_input/.
"""

import os
import sys
import asyncio
import subprocess

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import edge_tts

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(SCRIPT_DIR, "arabic_voice_input")
VGMSTREAM = os.path.join(SCRIPT_DIR, "vgmstream", "vgmstream-cli.exe")
TEMP_DIR = os.path.join(SCRIPT_DIR, "temp_tts_mp3")

os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# Callouts definitions with multiple voice variations for maximum variety in match
CALLOUTS = [
    # 1. Pass / مرر لي
    {
        "category": "Pass",
        "variations": [
            {"filename": "Pass_1.wav", "text": "مرر لي!", "voice": "ar-EG-ShakirNeural", "rate": "+28%", "pitch": "+5Hz"},
            {"filename": "Pass_2.wav", "text": "الكرة هنا!", "voice": "ar-SA-HamedNeural", "rate": "+25%", "pitch": "+4Hz"},
            {"filename": "Pass_3.wav", "text": "باص يا كابتن!", "voice": "ar-AE-HamdanNeural", "rate": "+30%", "pitch": "+6Hz"},
        ]
    },
    # 2. PassBack / للخلف
    {
        "category": "PassBack",
        "variations": [
            {"filename": "PassBack_1.wav", "text": "للخلف!", "voice": "ar-EG-ShakirNeural", "rate": "+25%", "pitch": "+5Hz"},
            {"filename": "PassBack_2.wav", "text": "رجعها وراك!", "voice": "ar-SA-HamedNeural", "rate": "+25%", "pitch": "+4Hz"},
            {"filename": "PassBack_3.wav", "text": "وراك للخلف!", "voice": "ar-AE-HamdanNeural", "rate": "+28%", "pitch": "+5Hz"},
        ]
    },
    # 3. Cross / عرضية
    {
        "category": "Cross",
        "variations": [
            {"filename": "Cross_1.wav", "text": "عرضية!", "voice": "ar-EG-ShakirNeural", "rate": "+28%", "pitch": "+6Hz"},
            {"filename": "Cross_2.wav", "text": "ارفع الكرة!", "voice": "ar-SA-HamedNeural", "rate": "+25%", "pitch": "+5Hz"},
            {"filename": "Cross_3.wav", "text": "كروس هنا!", "voice": "ar-AE-HamdanNeural", "rate": "+30%", "pitch": "+6Hz"},
        ]
    },
    # 4. Line / على الخط
    {
        "category": "Line",
        "variations": [
            {"filename": "Line_1.wav", "text": "على الخط!", "voice": "ar-EG-ShakirNeural", "rate": "+25%", "pitch": "+5Hz"},
            {"filename": "Line_2.wav", "text": "على الجناح!", "voice": "ar-SA-HamedNeural", "rate": "+25%", "pitch": "+5Hz"},
            {"filename": "Line_3.wav", "text": "الطرف يا كابتن!", "voice": "ar-AE-HamdanNeural", "rate": "+28%", "pitch": "+5Hz"},
        ]
    },
    # 5. BackPost / القائم البعيد
    {
        "category": "BackPost",
        "variations": [
            {"filename": "BackPost_1.wav", "text": "في البعيدة!", "voice": "ar-EG-ShakirNeural", "rate": "+25%", "pitch": "+5Hz"},
            {"filename": "BackPost_2.wav", "text": "القائم البعيد!", "voice": "ar-SA-HamedNeural", "rate": "+22%", "pitch": "+4Hz"},
            {"filename": "BackPost_3.wav", "text": "العبها بعيد!", "voice": "ar-AE-HamdanNeural", "rate": "+25%", "pitch": "+5Hz"},
        ]
    },
    # 6. FrontPost / القائم القريب
    {
        "category": "FrontPost",
        "variations": [
            {"filename": "FrontPost_1.wav", "text": "في القريبة!", "voice": "ar-EG-ShakirNeural", "rate": "+28%", "pitch": "+6Hz"},
            {"filename": "FrontPost_2.wav", "text": "القائم القريب!", "voice": "ar-SA-HamedNeural", "rate": "+25%", "pitch": "+5Hz"},
            {"filename": "FrontPost_3.wav", "text": "هنا في القريبة!", "voice": "ar-AE-HamdanNeural", "rate": "+28%", "pitch": "+5Hz"},
        ]
    },
    # 7. Switch / عكس اللعب
    {
        "category": "Switch",
        "variations": [
            {"filename": "Switch_1.wav", "text": "اعكس اللعب!", "voice": "ar-EG-ShakirNeural", "rate": "+25%", "pitch": "+5Hz"},
            {"filename": "Switch_2.wav", "text": "الجهة الثانية!", "voice": "ar-SA-HamedNeural", "rate": "+25%", "pitch": "+4Hz"},
            {"filename": "Switch_3.wav", "text": "غير الاتجاه!", "voice": "ar-AE-HamdanNeural", "rate": "+25%", "pitch": "+5Hz"},
        ]
    },
    # 8. Help / ساعدني
    {
        "category": "Help",
        "variations": [
            {"filename": "Help_1.wav", "text": "ساعدني!", "voice": "ar-EG-ShakirNeural", "rate": "+28%", "pitch": "+7Hz"},
            {"filename": "Help_2.wav", "text": "معاك سند!", "voice": "ar-SA-HamedNeural", "rate": "+25%", "pitch": "+5Hz"},
            {"filename": "Help_3.wav", "text": "محتاج دعم!", "voice": "ar-AE-HamdanNeural", "rate": "+28%", "pitch": "+6Hz"},
        ]
    },
    # 9. LeaveIt / اتركها
    {
        "category": "LeaveIt",
        "variations": [
            {"filename": "LeaveIt_1.wav", "text": "اتركها!", "voice": "ar-EG-ShakirNeural", "rate": "+30%", "pitch": "+7Hz"},
            {"filename": "LeaveIt_2.wav", "text": "خلها لي!", "voice": "ar-SA-HamedNeural", "rate": "+25%", "pitch": "+5Hz"},
            {"filename": "LeaveIt_3.wav", "text": "سيبها عندي!", "voice": "ar-EG-ShakirNeural", "rate": "+28%", "pitch": "+6Hz"},
        ]
    },
    # 10. GotBall / استلمت
    {
        "category": "GotBall",
        "variations": [
            {"filename": "GotBall_1.wav", "text": "عندي!", "voice": "ar-EG-ShakirNeural", "rate": "+25%", "pitch": "+4Hz"},
            {"filename": "GotBall_2.wav", "text": "معي الكرة!", "voice": "ar-SA-HamedNeural", "rate": "+22%", "pitch": "+3Hz"},
            {"filename": "GotBall_3.wav", "text": "استلمت خلاص!", "voice": "ar-AE-HamdanNeural", "rate": "+25%", "pitch": "+4Hz"},
        ]
    },
    # 11. Danger / انتبه
    {
        "category": "Danger",
        "variations": [
            {"filename": "Danger_1.wav", "text": "انتبه وراك!", "voice": "ar-EG-ShakirNeural", "rate": "+30%", "pitch": "+8Hz"},
            {"filename": "Danger_2.wav", "text": "خطر، انتبه!", "voice": "ar-SA-HamedNeural", "rate": "+28%", "pitch": "+7Hz"},
            {"filename": "Danger_3.wav", "text": "وراك لاعب!", "voice": "ar-AE-HamdanNeural", "rate": "+30%", "pitch": "+8Hz"},
        ]
    },
    # 12. Mark / راقب لاعبك
    {
        "category": "Mark",
        "variations": [
            {"filename": "Mark_1.wav", "text": "راقب لاعبك!", "voice": "ar-EG-ShakirNeural", "rate": "+25%", "pitch": "+5Hz"},
            {"filename": "Mark_2.wav", "text": "امسك اللاعب!", "voice": "ar-SA-HamedNeural", "rate": "+25%", "pitch": "+5Hz"},
            {"filename": "Mark_3.wav", "text": "غط عليه سريع!", "voice": "ar-AE-HamdanNeural", "rate": "+28%", "pitch": "+6Hz"},
        ]
    },
    # 13. Good_Job / أحسنت
    {
        "category": "Good_Job",
        "variations": [
            {"filename": "Good_Job_1.wav", "text": "عاش يا وحش!", "voice": "ar-EG-ShakirNeural", "rate": "+22%", "pitch": "+6Hz"},
            {"filename": "Good_Job_2.wav", "text": "أحسنت، برافو!", "voice": "ar-SA-HamedNeural", "rate": "+20%", "pitch": "+5Hz"},
            {"filename": "Good_Job_3.wav", "text": "لعب رائع، استمر!", "voice": "ar-AE-HamdanNeural", "rate": "+22%", "pitch": "+5Hz"},
        ]
    },
    # 14. CheerUp / لا بأس
    {
        "category": "CheerUp",
        "variations": [
            {"filename": "CheerUp_1.wav", "text": "معلش، ولا يهمك!", "voice": "ar-EG-ShakirNeural", "rate": "+22%", "pitch": "+4Hz"},
            {"filename": "CheerUp_2.wav", "text": "شد حيلك يا كابتن!", "voice": "ar-SA-HamedNeural", "rate": "+22%", "pitch": "+4Hz"},
            {"filename": "CheerUp_3.wav", "text": "الجايات أحسن!", "voice": "ar-AE-HamdanNeural", "rate": "+22%", "pitch": "+3Hz"},
        ]
    },
    # 15. Sorry / آسف
    {
        "category": "Sorry",
        "variations": [
            {"filename": "Sorry_1.wav", "text": "عذراً مني!", "voice": "ar-EG-ShakirNeural", "rate": "+25%", "pitch": "+4Hz"},
            {"filename": "Sorry_2.wav", "text": "آسف، غلطتي!", "voice": "ar-SA-HamedNeural", "rate": "+25%", "pitch": "+3Hz"},
            {"filename": "Sorry_3.wav", "text": "حقك علي!", "voice": "ar-AE-HamdanNeural", "rate": "+25%", "pitch": "+3Hz"},
        ]
    },
    # 16. Reply_Apologies / فداك
    {
        "category": "Reply_Apologies",
        "variations": [
            {"filename": "Reply_Apologies_1.wav", "text": "ولا يهمك يا كابتن!", "voice": "ar-EG-ShakirNeural", "rate": "+22%", "pitch": "+3Hz"},
            {"filename": "Reply_Apologies_2.wav", "text": "فداك، كمل!", "voice": "ar-SA-HamedNeural", "rate": "+22%", "pitch": "+3Hz"},
            {"filename": "Reply_Apologies_3.wav", "text": "عادي، ركز في الجاية!", "voice": "ar-AE-HamdanNeural", "rate": "+22%", "pitch": "+4Hz"},
        ]
    },
    # 17. Thanks / شكراً
    {
        "category": "Thanks",
        "variations": [
            {"filename": "Thanks_1.wav", "text": "تسلم يا غالي!", "voice": "ar-EG-ShakirNeural", "rate": "+25%", "pitch": "+4Hz"},
            {"filename": "Thanks_2.wav", "text": "شكراً يا كابتن!", "voice": "ar-SA-HamedNeural", "rate": "+25%", "pitch": "+4Hz"},
            {"filename": "Thanks_3.wav", "text": "حبيبي، شكراً!", "voice": "ar-AE-HamdanNeural", "rate": "+25%", "pitch": "+4Hz"},
        ]
    },
]

async def generate_single(text, voice, rate, pitch, out_mp3):
    comm = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await comm.save(out_mp3)

async def main():
    print("=" * 60)
    print("   Rematch - Energetic Arabic Voice Generation (edge-tts)")
    print("=" * 60)

    total_generated = 0
    for group in CALLOUTS:
        cat = group["category"]
        print(f"\n[*] Generating Callout: {cat} (3 variations)...")
        for var in group["variations"]:
            fname = var["filename"]
            text = var["text"]
            voice = var["voice"]
            rate = var["rate"]
            pitch = var["pitch"]

            mp3_path = os.path.join(TEMP_DIR, fname.replace(".wav", ".mp3"))
            wav_path = os.path.join(INPUT_DIR, fname)

            # Generate MP3
            await generate_single(text, voice, rate, pitch, mp3_path)

            # Convert MP3 to WAV via vgmstream
            cmd = [VGMSTREAM, "-o", wav_path, mp3_path]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0 or not os.path.exists(wav_path):
                print(f"[ERROR] Failed to convert {mp3_path} to {wav_path}: {res.stderr}")
                continue

            total_generated += 1
            wav_size = os.path.getsize(wav_path)
            print(f"    [+] {fname:22} | \"{text}\" | Voice: {voice[:10]} | Size: {wav_size:,} bytes")

    print(f"\n[SUCCESS] Generated all {total_generated} Arabic callout WAV files in:")
    print(f"          {INPUT_DIR}")

if __name__ == "__main__":
    asyncio.run(main())
