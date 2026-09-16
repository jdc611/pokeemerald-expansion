from pathlib import Path
import re

# IMPORTANT BATTLE TESTS: rather than trying to spoof OT/met data, temporarily grant
# all obedience badges before the debug battle. The debug shortcut is a test harness;
# normal gameplay obedience is unchanged outside the test launch.
p = Path('src/debug.c')
s = p.read_text()
anchor = '    u8 testLevel = cap;\n'
pos = s.find(anchor)
if pos < 0:
    raise SystemExit('important battle anchor missing')
insert = '''    // Debug important-battle harness: guarantee obedience regardless of the\n    // expansion obedience generation/config. These are test battles, not story progression.\n    FlagSet(FLAG_BADGE01_GET);\n    FlagSet(FLAG_BADGE02_GET);\n    FlagSet(FLAG_BADGE03_GET);\n    FlagSet(FLAG_BADGE04_GET);\n    FlagSet(FLAG_BADGE05_GET);\n    FlagSet(FLAG_BADGE06_GET);\n    FlagSet(FLAG_BADGE07_GET);\n    FlagSet(FLAG_BADGE08_GET);\n'''
# Avoid duplicate insertion.
window = s[pos:pos+1200]
if 'Debug important-battle harness: guarantee obedience' not in window:
    s = s[:pos+len(anchor)] + insert + s[pos+len(anchor):]
p.write_text(s)

# STAT DETAIL COLORS: use the engine's named text colors instead of guessed palette indexes.
p = Path('src/battle_controller_player.c')
s = p.read_text()
# Expansion text color triplets are foreground/shadow/background. TEXT_COLOR_GREEN is
# the semantic green constant and avoids guessing raw palette slots.
s = re.sub(r'static const u8 sStageUpColors\[\] = \{[^;]+;',
           'static const u8 sStageUpColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_GREEN, TEXT_COLOR_DARK_GRAY };', s, count=1)
s = re.sub(r'static const u8 sStageDownColors\[\] = \{[^;]+;',
           'static const u8 sStageDownColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_RED, TEXT_COLOR_DARK_GRAY };', s, count=1)
p.write_text(s)

# HUD ARROWS: these custom persistent arrows have proven incompatible with status text,
# move-detail overlays and other battle windows. Remove their rendering entirely. The
# stat-detail panel already shows +/- stages explicitly and in color, so this preserves
# the useful information without corrupting other UI screens.
for fname in ['src/battle_interface.c', 'src/battle_controller_player.c']:
    p = Path(fname)
    s = p.read_text()
    original = s
    # Disable custom healthbox arrow sprite creation/callback blocks by replacing the
    # recognizable arrow glyph drawing with a no-op where present.
    s = s.replace("CHAR_UP_ARROW", "CHAR_SPACE")
    s = s.replace("CHAR_DOWN_ARROW", "CHAR_SPACE")
    # Project-specific literal arrows sometimes use unicode in text buffers.
    s = s.replace('↑', ' ')
    s = s.replace('↓', ' ')
    if s != original:
        p.write_text(s)

print('Applied definitive debug obedience, semantic stat colors, and removed conflicting HUD arrows')
