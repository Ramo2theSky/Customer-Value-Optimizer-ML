"""Fix emoji characters in Python files for Windows compatibility"""

import os
import re

# Emoji to text replacements
EMOJI_MAP = {
    '📊': '[DATA]',
    '✅': '[OK]',
    '🎯': '[TARGET]',
    '⚠️': '[WARN]',
    '💡': '[IDEA]',
    '🔍': '[SEARCH]',
    '📈': '[CHART]',
    '🎊': '[SUCCESS]',
    '🎖️': '[MEDAL]',
    '🏆': '[TROPHY]',
    '⭐': '[STAR]',
    '🌟': '[STAR]',
    '💪': '[STRONG]',
    '👍': '[OK]',
    '🙏': '[THANKS]',
    '🤝': '[HANDSHAKE]',
    '💼': '[BRIEFCASE]',
    '📋': '[LIST]',
    '📄': '[FILE]',
    '📑': '[DOCS]',
    '🔧': '[FIX]',
    '🛠️': '[TOOLS]',
    '⚙️': '[GEAR]',
    '🚀': '[LAUNCH]',
    '🔥': '[HOT]',
    '💰': '[MONEY]',
    '💎': '[DIAMOND]',
    '🔒': '[LOCK]',
    '🔓': '[UNLOCK]',
    '📝': '[WRITE]',
    '📉': '[DOWN]',
    '🎉': '[SUCCESS]',
    '🎖': '[MEDAL]',
    '🏠': '[HOME]',
    '🏢': '[OFFICE]',
    '🏛️': '[GOV]',
    '🏫': '[SCHOOL]',
    '🏥': '[HOSPITAL]',
    '🏦': '[BANK]',
    '🏬': '[MALL]',
    '🏭': '[FACTORY]',
    '🌐': '[WEB]',
    '📱': '[MOBILE]',
    '💻': '[PC]',
    '🖥️': '[DESKTOP]',
    '⚡': '[POWER]',
    '🔌': '[PLUG]',
    '📡': '[SAT]',
    '🛰️': '[SAT]',
    '🔋': '[BATTERY]',
    '🌱': '[GROW]',
    '📶': '[SIGNAL]',
    '🔔': '[BELL]',
    '📢': '[ALERT]',
    '📣': '[ANNOUNCE]',
    '🔊': '[SOUND]',
    '🔉': '[VOL]',
    '🔈': '[VOL]',
    '🎵': '[MUSIC]',
    '🎶': '[MUSIC]',
    '🔔': '[BELL]',
    '📌': '[PIN]',
    '📍': '[PIN]',
    '🚩': '[FLAG]',
    '🏴': '[FLAG]',
    '🏳️': '[FLAG]',
    '🏁': '[CHECKERED]',
    '🚥': '[TRAFFIC]',
    '🚦': '[TRAFFIC]',
}

def remove_emojis(text):
    """Remove all emojis from text"""
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001F900-\U0001F9FF"  # supplemental symbols
        u"\U0001FA00-\U0001FA6F"  # chess symbols
        u"\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-a
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def fix_file(filepath):
    """Fix emojis in a single file"""
    print(f"Processing: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Replace known emojis with text equivalents
    for emoji, replacement in EMOJI_MAP.items():
        content = content.replace(emoji, replacement)
    
    # Remove any remaining emojis
    content = remove_emojis(content)
    
    if original != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  [FIXED] {filepath}")
    else:
        print(f"  [NONE] No emojis in {filepath}")

# Fix main files
files_to_fix = [
    'cvo_smart_classifier_v30.py',
    'export_dashboard_data.py',
    'cvo_nbo_v30.py',
]

for filename in files_to_fix:
    filepath = os.path.join('D:\\ICON+', filename)
    if os.path.exists(filepath):
        fix_file(filepath)
    else:
        print(f"File not found: {filepath}")

print("\nDone!")
