from pathlib import Path

# 1) Test battle obedience: mark important-battle debug launches with a temp flag,
# then bypass obedience only while that flag is active.
p = Path('src/debug.c')
s = p.read_text()
# Locate our custom important-battle party builder by the testLevel line and set a temp flag near launch.
needle = '    u8 testLevel = cap;\n'
pos = s.find(needle)
if pos < 0:
    raise SystemExit('important battle testLevel anchor missing')
# Add a marker flag once in this custom function. TEMP flags are cleared on map transition,
# so this remains scoped to the debug-launched battle.
insert_at = pos + len(needle)
if 'FLAG_TEMP_2); // IMPORTANT_BATTLE_DEBUG_OBEDIENCE' not in s[pos:pos+2500]:
    s = s[:insert_at] + '    FlagSet(FLAG_TEMP_2); // IMPORTANT_BATTLE_DEBUG_OBEDIENCE\n' + s[insert_at:]
p.write_text(s)

p = Path('src/battle_util.c')
s = p.read_text()
anchor = '''    if (gBattleTypeFlags & (BATTLE_TYPE_LINK | BATTLE_TYPE_RECORDED_LINK))\n        return OBEYS;\n'''
replacement = '''    // Important-battle debug teams are generated for testing and must always obey.\n    if (FlagGet(FLAG_TEMP_2))\n        return OBEYS;\n    if (gBattleTypeFlags & (BATTLE_TYPE_LINK | BATTLE_TYPE_RECORDED_LINK))\n        return OBEYS;\n'''
if anchor not in s:
    raise SystemExit('obedience anchor missing')
s = s.replace(anchor, replacement, 1)
p.write_text(s)

# 2) Stage panel: force a genuinely bright green palette index for boosts.
p = Path('src/battle_controller_player.c')
s = p.read_text()
# Red index 1 is confirmed vivid in-game. Use the expansion's bright green text index 2.
s = s.replace('static const u8 sStageUpColors[] = { 14, 6, 15 };', 'static const u8 sStageUpColors[] = { 14, 2, 15 };', 1)
p.write_text(s)

# 3) Healthbox arrows: when a status condition is present, shift the stat-change arrow away
# from the status text. Patch the custom arrow positioning at its sprite coordinate anchor.
p = Path('src/battle_interface.c')
s = p.read_text()
# Search common custom arrow positioning patterns added by this project.
patterns = [
    ('gSprites[arrowSpriteId].x2 =', 'arrowSpriteId'),
    ('gSprites[arrowSpriteId].x =', 'arrowSpriteId'),
    ('gSprites[statSpriteId].x2 =', 'statSpriteId'),
    ('gSprites[statSpriteId].x =', 'statSpriteId'),
]
patched = False
for pattern, var in patterns:
    idx = s.find(pattern)
    if idx >= 0:
        line_end = s.find('\n', idx)
        line = s[idx:line_end]
        # Add an x offset immediately after the existing coordinate assignment.
        extra = f'\n    if (gBattleMons[battler].status1 != STATUS1_NONE)\n        gSprites[{var}].x2 += 18; // keep stat arrow clear of SLP/PSN/etc.'
        s = s[:line_end] + extra + s[line_end:]
        patched = True
        break
if not patched:
    # Do not silently claim this part was applied.
    raise SystemExit('healthbox stat-arrow positioning anchor missing')
p.write_text(s)

print('Applied debug obedience bypass, bright green boosts, and status-safe HUD arrow position')
