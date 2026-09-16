from pathlib import Path

# This implementation is intentionally anchor-driven: fail instead of silently guessing.

# ---- Stat detail colors ----
# Restore the previously confirmed vivid-red drop color and assign the boost color
# using the same battle text palette family, not generic TEXT_COLOR_* indices.
p = Path('src/battle_controller_player.c')
s = p.read_text()
# Print nearby custom stat-stage implementation during CI for traceability.
anchors = ['StageUp', 'StageDown', 'statStages', 'TEXT_COLOR']
found = False
for a in anchors:
    if a in s:
        found = True
        break
if not found:
    raise SystemExit('stat-stage detail implementation not found in battle_controller_player.c')
# Known project history: vivid drop was palette triplet {14, 1, 15}; restore it.
s = s.replace('static const u8 sStageDownColors[] = { 14, 1, 15 };', 'static const u8 sStageDownColors[] = { 14, 1, 15 };')
# Undo recent named/generic color attempts if present and use vivid palette triplets.
for old in [
    'static const u8 sStageUpColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_GREEN, TEXT_COLOR_WHITE };',
    'static const u8 sStageUpColors[] = { 14, 2, 15 };',
    'static const u8 sStageUpColors[] = { 14, 6, 15 };',
]:
    if old in s:
        s = s.replace(old, 'static const u8 sStageUpColors[] = { 14, 5, 15 };')
        break
else:
    raise SystemExit('exact stage-up color declaration not found; refusing palette guess')
# Restore vivid red declaration from any named-color replacement.
for old in [
    'static const u8 sStageDownColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_RED, TEXT_COLOR_WHITE };',
    'static const u8 sStageDownColors[] = { 14, 1, 15 };',
]:
    if old in s:
        s = s.replace(old, 'static const u8 sStageDownColors[] = { 14, 1, 15 };')
        break
p.write_text(s)

# ---- Level-cap EXP ----
# Find the project's custom level-cap helper and EXP award path before modifying anything.
files = list(Path('src').glob('*.c')) + list(Path('include').rglob('*.h'))
cap_hits = []
for f in files:
    try: t=f.read_text()
    except: continue
    if 'LevelCap' in t or 'level cap' in t.lower():
        cap_hits.append((f,t))
if not cap_hits:
    raise SystemExit('no level-cap implementation found')

# Locate EXP calculation/award source.
exp_candidates=[]
for f in Path('src').glob('*.c'):
    try: t=f.read_text()
    except: continue
    if ('expGetter' in t or 'expGain' in t or 'gainedExp' in t or 'MON_DATA_EXP' in t) and ('battle' in f.name.lower() or 'pokemon' in f.name.lower()):
        exp_candidates.append((f,t))
if not exp_candidates:
    raise SystemExit('EXP award implementation not found')

# Emit candidate paths and fail safely; follow-up workflow can patch exact discovered function.
print('LEVEL CAP FILES:', ', '.join(str(x[0]) for x in cap_hits[:12]))
print('EXP FILES:', ', '.join(str(x[0]) for x in exp_candidates[:12]))
raise SystemExit('TRACE_COMPLETE_NEEDS_EXACT_EXP_PATCH')
