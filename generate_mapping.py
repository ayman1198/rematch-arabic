# -*- coding: utf-8 -*-
import os, sys, json, struct

mandarin_media = r'C:\Users\ayman\.gemini\antigravity\scratch\rematch-tools\unpacked_pak\Runtime\Content\WwiseAudio\Media\Mandarin'
mandarin_events = r'C:\Users\ayman\.gemini\antigravity\scratch\rematch-tools\unpacked_pak\Runtime\Content\WwiseAudio\Event\Mandarin'
output_json = r'C:\Users\ayman\.gemini\antigravity\scratch\rematch-tools\callouts_mapping.json'

all_media = {}
for root, dirs, files in os.walk(mandarin_media):
    for f in files:
        if f.endswith('.wem'):
            mid = int(f[:-4])
            rel = os.path.relpath(os.path.join(root, f), mandarin_media).replace('\\', '/')
            all_media[mid] = rel

callouts_def = [
    {
        'category': 'Pass_BallCallGeneric',
        'bank': 'Play_BallCallGeneric_Distance.bnk',
        'arabic_name': 'طلب التمرير / مرر لي (عام)',
        'suggested_phrases': ['مرر لي!', 'الكرة هنا!', 'باص!'],
        'sample_duration': '0.55s'
    },
    {
        'category': 'PassBack',
        'bank': 'Play_BallCall_PassBack_Distance.bnk',
        'arabic_name': 'طلب التمرير للخلف',
        'suggested_phrases': ['للخلف!', 'رجعها للخلف!', 'وراء!'],
        'sample_duration': '0.95s'
    },
    {
        'category': 'Cross',
        'bank': 'Play_BallCall_Cross_Distance.bnk',
        'arabic_name': 'طلب عرضية',
        'suggested_phrases': ['عرضية!', 'ارفعها!', 'كروس!'],
        'sample_duration': '0.58s'
    },
    {
        'category': 'Line',
        'bank': 'Play_BallCall_Line_Distance.bnk',
        'arabic_name': 'طلب الكرة على الخط / الجناح',
        'suggested_phrases': ['على الخط!', 'على الجناح!'],
        'sample_duration': '0.62s'
    },
    {
        'category': 'BackPost',
        'bank': 'Play_BallCall_BackPost_Far_Voice.bnk',
        'arabic_name': 'طلب الكرة عند القائم البعيد',
        'suggested_phrases': ['القائم البعيد!', 'في البعيدة!'],
        'sample_duration': '0.98s'
    },
    {
        'category': 'FrontPost',
        'bank': 'Play_BallCall_FrontPost_Distance.bnk',
        'arabic_name': 'طلب الكرة عند القائم القريب',
        'suggested_phrases': ['القائم القريب!', 'في القريبة!'],
        'sample_duration': '0.88s'
    },
    {
        'category': 'Switch',
        'bank': 'Play_BallCall_Switch_Far_Voice.bnk',
        'arabic_name': 'طلب تغيير اتجاه اللعب / عكس الملعب',
        'suggested_phrases': ['اعكس اللعب!', 'الجهة الثانية!'],
        'sample_duration': '0.83s'
    },
    {
        'category': 'Help',
        'bank': 'Play_BallCall_Help_Far_Voice.bnk',
        'arabic_name': 'طلب المساندة / الدعم',
        'suggested_phrases': ['ساعدني!', 'معاك!', 'سند!'],
        'sample_duration': '0.71s'
    },
    {
        'category': 'LeaveIt',
        'bank': 'Play_BallCall_LeaveIt_Close_Voice.bnk',
        'arabic_name': 'اترك الكرة / خلها لي',
        'suggested_phrases': ['اتركها!', 'خلها!', 'لي!'],
        'sample_duration': '0.59s'
    },
    {
        'category': 'GotBall',
        'bank': 'Play_BallCall_GotBall_Close_Voice.bnk',
        'arabic_name': 'الكرة معي / عندي',
        'suggested_phrases': ['عندي!', 'معي الكرة!', 'استلمت!'],
        'sample_duration': '0.81s'
    },
    {
        'category': 'Danger',
        'bank': 'Play_Tactics_Danger_Distance.bnk',
        'arabic_name': 'تحذير تكتيكي / خطر / انتبه',
        'suggested_phrases': ['انتبه!', 'خطر!', 'وراك!'],
        'sample_duration': '0.72s'
    },
    {
        'category': 'Mark',
        'bank': 'Play_Tactics_Mark_Far_Voice.bnk',
        'arabic_name': 'تغطية ومراقبة لاعب / امسكه',
        'suggested_phrases': ['راقب لاعبك!', 'امسك!', 'غط عليه!'],
        'sample_duration': '0.75s'
    },
    {
        'category': 'Good_Job',
        'bank': 'Play_Supportive_Good_Distance.bnk',
        'arabic_name': 'تشجيع: أحسنت / لعب رائع',
        'suggested_phrases': ['أحسنت!', 'برافو!', 'عاش!'],
        'sample_duration': '1.48s'
    },
    {
        'category': 'CheerUp',
        'bank': 'Play_Supportive_CheerUp_Distance.bnk',
        'arabic_name': 'رفع المعنويات: لا بأس / شد حيلك',
        'suggested_phrases': ['معلش!', 'شد حيلك!', 'الجايات أحسن!'],
        'sample_duration': '0.92s'
    },
    {
        'category': 'Sorry_Apologies',
        'bank': 'Play_Apologies_Close_Voice.bnk',
        'arabic_name': 'اعتذار: عذراً / خطأي',
        'suggested_phrases': ['عذراً!', 'آسف!', 'غلطتي!'],
        'sample_duration': '0.62s'
    },
    {
        'category': 'Reply_Apologies',
        'bank': 'Play_Reply_Apologies_Close_Voice.bnk',
        'arabic_name': 'رد الاعتذار: ولا يهمك / فداك',
        'suggested_phrases': ['ولا يهمك!', 'فداك!', 'عادي!'],
        'sample_duration': '0.89s'
    },
    {
        'category': 'Thanks_ReplySupport',
        'bank': 'Play_Reply_Supportives_Close_Voice.bnk',
        'arabic_name': 'رد التشجيع / شكراً',
        'suggested_phrases': ['شكراً!', 'تسلم!', 'حبيبي!'],
        'sample_duration': '0.52s'
    }
]

total_found_wems = 0
for item in callouts_def:
    bank_name = item['bank']
    found_bank_path = None
    for root, dirs, files in os.walk(mandarin_events):
        if bank_name in files:
            found_bank_path = os.path.join(root, bank_name)
            break
    if not found_bank_path:
        print(f"MISSING BANK: {bank_name}")
        continue
    with open(found_bank_path, 'rb') as f:
        bdata = f.read()
    
    matched = []
    for i in range(0, len(bdata) - 4):
        val = struct.unpack('<I', bdata[i:i+4])[0]
        if val in all_media:
            rel = all_media[val]
            if rel not in matched:
                matched.append(rel)
    item['media_files'] = matched
    item['media_count'] = len(matched)
    total_found_wems += len(matched)
    print(f"{item['category']}: {len(matched)} variations found")

print(f"\nTotal mapped callout variations: {total_found_wems}")

with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(callouts_def, f, ensure_ascii=False, indent=2)

print(f"Saved mapping to: {output_json}")
