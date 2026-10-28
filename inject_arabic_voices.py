# -*- coding: utf-8 -*-
"""
Rematch - Arabic Voice Injection Pipeline (Native Wwise Opus)
Encodes Arabic WAVs to exact Wwise Opus (.wem, format 0x3041, 48kHz mono, 128kbps)
and injects into BOTH Mandarin and English(US) paths in Runtime-WinGDKClient_99_P.pak.
"""

import os
import sys
import json
import shutil
import struct
import subprocess

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(SCRIPT_DIR, "arabic_voice_input")
MANDARIN_MAPPING_FILE = os.path.join(SCRIPT_DIR, "callouts_mapping.json")
ENGLISH_MAPPING_FILE = os.path.join(SCRIPT_DIR, "english_callouts_mapping.json")

OPUSENC = os.path.join(SCRIPT_DIR, "opus-tools", "x64", "opusenc.exe")
REPAK = os.path.join(SCRIPT_DIR, "repak.exe")
PATCH_PAK_ROOT = os.path.join(SCRIPT_DIR, "patch_pak_root")
OUTPUT_PAK = os.path.join(SCRIPT_DIR, "Runtime-WinGDKClient_99_P.pak")
GAME_PAK_DIR = r"c:\XboxGames\Rematch\Content\Runtime\Content\Paks"
GAME_PAK_DEST = os.path.join(GAME_PAK_DIR, "Runtime-WinGDKClient_99_P.pak")
GAME_SIG_DEST = os.path.join(GAME_PAK_DIR, "Runtime-WinGDKClient_99_P.sig")
ORIGINAL_SIG = os.path.join(GAME_PAK_DIR, "Runtime-WinGDKClient.sig")

# Category aliases
ALIASES = {
    "pass": "Pass_BallCallGeneric",
    "ballcall": "Pass_BallCallGeneric",
    "pass_ballcallgeneric": "Pass_BallCallGeneric",
    "passback": "PassBack",
    "pass_back": "PassBack",
    "cross": "Cross",
    "line": "Line",
    "backpost": "BackPost",
    "back_post": "BackPost",
    "frontpost": "FrontPost",
    "front_post": "FrontPost",
    "switch": "Switch",
    "help": "Help",
    "leaveit": "LeaveIt",
    "leave_it": "LeaveIt",
    "gotball": "GotBall",
    "got_ball": "GotBall",
    "danger": "Danger",
    "mark": "Mark",
    "good": "Good_Job",
    "good_job": "Good_Job",
    "goodjob": "Good_Job",
    "bravo": "Good_Job",
    "cheerup": "CheerUp",
    "cheer_up": "CheerUp",
    "sorry": "Sorry_Apologies",
    "sorry_apologies": "Sorry_Apologies",
    "apologies": "Sorry_Apologies",
    "reply_apologies": "Reply_Apologies",
    "replyapologies": "Reply_Apologies",
    "thanks": "Thanks_ReplySupport",
    "thanks_replysupport": "Thanks_ReplySupport",
    "reply_support": "Thanks_ReplySupport",
    "replysupport": "Thanks_ReplySupport"
}

BANK_TO_CATEGORY = {
    "Play_BallCallGeneric_Distance.bnk": "Pass_BallCallGeneric",
    "Play_BallCall_PassBack_Distance.bnk": "PassBack",
    "Play_BallCall_Cross_Distance.bnk": "Cross",
    "Play_BallCall_Line_Distance.bnk": "Line",
    "Play_BallCall_BackPost_Far_Voice.bnk": "BackPost",
    "Play_BallCall_FrontPost_Distance.bnk": "FrontPost",
    "Play_BallCall_Switch_Far_Voice.bnk": "Switch",
    "Play_BallCall_Help_Far_Voice.bnk": "Help",
    "Play_BallCall_LeaveIt_Close_Voice.bnk": "LeaveIt",
    "Play_BallCall_GotBall_Close_Voice.bnk": "GotBall",
    "Play_Tactics_Danger_Distance.bnk": "Danger",
    "Play_Tactics_Mark_Far_Voice.bnk": "Mark",
    "Play_Supportive_Good_Distance.bnk": "Good_Job",
    "Play_Supportive_CheerUp_Distance.bnk": "CheerUp",
    "Play_Apologies_Close_Voice.bnk": "Sorry_Apologies",
    "Play_Reply_Apologies_Close_Voice.bnk": "Reply_Apologies",
    "Play_Reply_Supportives_Close_Voice.bnk": "Thanks_ReplySupport"
}

def clean_name(filename):
    """Strip numbers, extensions, and underscores to find alias match."""
    base = os.path.splitext(filename)[0].lower()
    parts = base.split('_')
    if parts[0].isdigit() and len(parts) > 1:
        base = '_'.join(parts[1:])
    parts = base.split('_')
    if parts[-1].isdigit() and len(parts) > 1:
        base = '_'.join(parts[:-1])
    return base.replace('-', '_').replace(' ', '_').strip()

def encode_wav_to_wwise_opus(wav_path, out_wem_path, temp_dir):
    """Encodes a WAV file to standard Audiokinetic Wwise Opus (.wem, format 0x3041)."""
    bname = os.path.splitext(os.path.basename(wav_path))[0]
    temp_opus = os.path.join(temp_dir, f"{bname}.temp.opus")
    
    # 1. Encode with opusenc (20ms frames, 128 kbps, mono)
    cmd = [OPUSENC, "--framesize", "20", "--bitrate", "128", wav_path, temp_opus]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or not os.path.exists(temp_opus):
        raise RuntimeError(f"opusenc failed: {res.stderr}")
    
    with open(temp_opus, "rb") as f:
        ogg_data = f.read()
    
    try:
        os.remove(temp_opus)
    except Exception:
        pass
    
    # 2. Extract raw Opus packets from Ogg pages
    offset = 0
    packets = []
    while offset < len(ogg_data):
        if ogg_data[offset:offset+4] != b'OggS':
            break
        num_segments = ogg_data[offset+26]
        segment_table = ogg_data[offset+27:offset+27+num_segments]
        body_offset = offset + 27 + num_segments
        packet_len = 0
        for s in segment_table:
            packet_len += s
            if s < 255:
                pkt = ogg_data[body_offset:body_offset+packet_len]
                packets.append(pkt)
                body_offset += packet_len
                packet_len = 0
        offset = body_offset

    if len(packets) < 3:
        raise ValueError(f"Too few Opus packets in {wav_path}: {len(packets)}")

    opus_head = packets[0]
    preskip = struct.unpack('<H', opus_head[10:12])[0]
    audio_packets = packets[2:]

    data_bytes = b''.join(audio_packets)
    seek_bytes = b''.join(struct.pack('<H', len(p)) for p in audio_packets)

    samples_per_frame = 960
    packet_count = len(audio_packets)
    total_samples = packet_count * samples_per_frame - preskip
    duration_sec = total_samples / 48000.0
    avg_bytes_per_sec = int(len(data_bytes) / duration_sec) if duration_sec > 0 else 16000

    fmt_payload = struct.pack(
        '<HHIIHHH' 'H' 'I' 'I' 'I' 'H' 'B' 'B',
        0x3041,            # wFormatTag = AK_WAVE_FORMAT_OPUS_WEM
        1,                 # nChannels = 1
        48000,             # nSamplesPerSec = 48000
        avg_bytes_per_sec, # nAvgBytesPerSec
        0,                 # nBlockAlign = 0
        0,                 # wBitsPerSample = 0
        18,                # cbSize = 18
        samples_per_frame, # samples_per_frame = 960
        0x00004101,        # channel_config
        total_samples,     # total_samples
        packet_count,      # table_count
        preskip,           # skip
        1,                 # codec_version = 1
        0                  # mapping = 0
    )

    def make_chunk(cid, payload):
        pad = b'\x00' if len(payload) % 2 == 1 else b''
        return cid + struct.pack('<I', len(payload)) + payload + pad

    chunks = [
        make_chunk(b'fmt ', fmt_payload),
        make_chunk(b'seek', seek_bytes),
        make_chunk(b'data', data_bytes)
    ]

    riff_body = b'WAVE' + b''.join(chunks)
    wem_bytes = b'RIFF' + struct.pack('<I', len(riff_body)) + riff_body

    os.makedirs(os.path.dirname(os.path.abspath(out_wem_path)), exist_ok=True)
    with open(out_wem_path, 'wb') as f:
        f.write(wem_bytes)

    return len(wem_bytes)

def main():
    print("=" * 60)
    print("  Rematch - Arabic Voice Injection (Mandarin & English)")
    print("  Codec: Native Wwise Opus (0x3041, 48kHz, mono, 128kbps)")
    print("=" * 60)

    # 1. Load mappings
    with open(MANDARIN_MAPPING_FILE, 'r', encoding='utf-8') as f:
        mandarin_defs = json.load(f)
    mandarin_map = {item['category']: item['media_files'] for item in mandarin_defs}

    with open(ENGLISH_MAPPING_FILE, 'r', encoding='utf-8') as f:
        english_bank_defs = json.load(f)
    english_map = {}
    for bank, media_list in english_bank_defs.items():
        cat = BANK_TO_CATEGORY.get(bank)
        if cat:
            english_map[cat] = media_list

    # 2. Check input WAV files
    wav_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith('.wav')]
    if not wav_files:
        print(f"[!] No WAV files found in {INPUT_DIR}")
        return

    print(f"\n[+] Found {len(wav_files)} WAV files in {INPUT_DIR}")

    # Map files to categories
    category_wavs = {}
    for wf in wav_files:
        cname = clean_name(wf)
        cat = ALIASES.get(cname)
        if not cat:
            for alias, target_cat in ALIASES.items():
                if alias in cname:
                    cat = target_cat
                    break
        if cat:
            category_wavs.setdefault(cat, []).append(os.path.join(INPUT_DIR, wf))

    print(f"[+] Successfully mapped WAVs to {len(category_wavs)} categories")

    # 3. Cache encoded WEM files
    temp_wem_cache = os.path.join(SCRIPT_DIR, "temp_wem_cache")
    os.makedirs(temp_wem_cache, exist_ok=True)
    converted_cache = {}

    print("\n[+] Encoding input WAVs to Wwise Opus (.wem)...")
    for wf in wav_files:
        wpath = os.path.join(INPUT_DIR, wf)
        bname = os.path.splitext(wf)[0]
        out_wem = os.path.join(temp_wem_cache, f"{bname}.wem")
        encode_wav_to_wwise_opus(wpath, out_wem, temp_wem_cache)
        converted_cache[wpath] = out_wem

    print(f"[+] All {len(converted_cache)} audio files encoded to valid Wwise Opus!")

    # 4. Inject into patch_pak_root for Mandarin AND English(US)
    media_root = os.path.join(PATCH_PAK_ROOT, "Runtime", "Content", "WwiseAudio", "Media")
    mandarin_root = os.path.join(media_root, "Mandarin")
    english_root = os.path.join(media_root, "English(US)")

    # Clean old wems in patch_pak_root to avoid stale files
    if os.path.exists(mandarin_root):
        shutil.rmtree(mandarin_root)
    if os.path.exists(english_root):
        shutil.rmtree(english_root)

    total_injected = 0

    # Inject Mandarin
    print("\n[*] Injecting into Mandarin media path...")
    mandarin_count = 0
    for cat, rel_paths in mandarin_map.items():
        wav_list = category_wavs.get(cat)
        if not wav_list:
            continue
        for idx, rel_path in enumerate(rel_paths):
            chosen_wav = wav_list[idx % len(wav_list)]
            src_wem = converted_cache[chosen_wav]
            dest = os.path.join(mandarin_root, rel_path.replace('/', os.sep))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(src_wem, dest)
            mandarin_count += 1
    print(f"    -> Injected {mandarin_count} Mandarin WEM files")
    total_injected += mandarin_count

    # Inject English(US)
    print("\n[*] Injecting into English(US) media path...")
    english_count = 0
    for cat, rel_paths in english_map.items():
        wav_list = category_wavs.get(cat)
        if not wav_list:
            continue
        for idx, rel_path in enumerate(rel_paths):
            chosen_wav = wav_list[idx % len(wav_list)]
            src_wem = converted_cache[chosen_wav]
            dest = os.path.join(english_root, rel_path.replace('/', os.sep))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy2(src_wem, dest)
            english_count += 1
    print(f"    -> Injected {english_count} English(US) WEM files")
    total_injected += english_count

    print(f"\n[+] Total .wem files placed in patch_pak_root: {total_injected}")

    # 5. Pack with repak
    print("\n[+] Packing Runtime-WinGDKClient_99_P.pak using repak...")
    pack_cmd = [
        REPAK, "pack",
        "--version", "V11",
        "--mount-point", "../../../",
        "--path-hash-seed", "544121096",
        "--compression", "Oodle",
        PATCH_PAK_ROOT,
        OUTPUT_PAK
    ]
    res = subprocess.run(pack_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[ERROR] repak pack failed: {res.stderr}")
        sys.exit(1)

    pak_size = os.path.getsize(OUTPUT_PAK)
    print(f"[+] Successfully built: {OUTPUT_PAK} ({pak_size:,} bytes)")

    # 6. Deploy to game folder
    print(f"\n[+] Deploying patch pak to game: {GAME_PAK_DEST}")
    shutil.copy2(OUTPUT_PAK, GAME_PAK_DEST)

    # Ensure signature file exists
    if not os.path.exists(GAME_SIG_DEST) and os.path.exists(ORIGINAL_SIG):
        print(f"[+] Creating signature file: {GAME_SIG_DEST}")
        shutil.copy2(ORIGINAL_SIG, GAME_SIG_DEST)

    print("\n" + "=" * 60)
    print("   [SUCCESS] Full Arabic Callouts Injected Successfully!")
    print(f"   Injected: Text Locres + {mandarin_count} Mandarin + {english_count} English WEMs")
    print(f"   Destination: {GAME_PAK_DEST}")
    print("=" * 60)

if __name__ == "__main__":
    main()
