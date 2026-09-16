from pathlib import Path

# Exact obedience function: debug important-battle teams should always obey.
p = Path('src/battle_util.c')
s = p.read_text()
anchor = '''    if (gBattleTypeFlags & (BATTLE_TYPE_LINK | BATTLE_TYPE_RECORDED_LINK))\n        return OBEYS;\n'''
replacement = '''    // Important-battle debug teams are test fixtures; bypass badge/met-level obedience only for them.\n    if (FlagGet(FLAG_TEMP_2))\n        return OBEYS;\n    if (gBattleTypeFlags & (BATTLE_TYPE_LINK | BATTLE_TYPE_RECORDED_LINK))\n        return OBEYS;\n'''
if 'FlagGet(FLAG_TEMP_2)' not in s[s.find('GetAttackerObedienceForAction'):s.find('GetAttackerObedienceForAction')+1800]:
    if anchor not in s:
        raise SystemExit('obedience anchor missing')
    s = s.replace(anchor, replacement, 1)
p.write_text(s)

# Ensure the important-battle debug launcher marks the battle.
p = Path('src/debug.c')
s = p.read_text()
needle = '    u8 testLevel = cap;\n'
pos = s.find(needle)
if pos < 0:
    raise SystemExit('important battle testLevel anchor missing')
window = s[pos:pos+2500]
if 'FLAG_TEMP_2' not in window:
    s = s[:pos+len(needle)] + '    FlagSet(FLAG_TEMP_2); // IMPORTANT_BATTLE_DEBUG_OBEDIENCE\n' + s[pos+len(needle):]
p.write_text(s)

# Positive stage text: use a dedicated custom green text color rather than guessing palette indexes.
p = Path('src/battle_controller_player.c')
s = p.read_text()
s = s.replace('static const u8 sStageUpColors[] = { 14, 2, 15 };', 'static const u8 sStageUpColors[] = { 14, TEXT_COLOR_GREEN, 15 };')
p.write_text(s)

# Stat arrows: they were deliberately coded to follow healthboxes on every battle screen.
# Restrict them to the main action screen, and never draw over a status condition.
p = Path('src/battle_interface.c')
s = p.read_text()
old = '''    // Follow the visible health box throughout battle, including messages,\n    // action selection, and move selection. Other screens hide/recreate it.\n    if (gSprites[healthboxId].invisible || !IsBattlerAlive(battler))\n    {\n        sprite->invisible = TRUE;\n        return;\n    }\n'''
new = '''    // Stage markers belong only on the normal action HUD. Never cover status text\n    // and never leak into move details, messages, or other battle sub-screens.\n    if (gSprites[healthboxId].invisible || !IsBattlerAlive(battler)\n     || gBattleMons[battler].status1 != STATUS1_NONE\n     || gBattleResources->bufferA[0][0] != CONTROLLER_CHOOSEACTION)\n    {\n        sprite->invisible = TRUE;\n        return;\n    }\n'''
if old not in s:
    raise SystemExit('exact stat marker lifecycle block missing')
s = s.replace(old, new, 1)
p.write_text(s)
print('Applied traced obedience, positive text, and stat-marker lifecycle fixes')
