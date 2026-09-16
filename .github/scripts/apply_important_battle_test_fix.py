from pathlib import Path

# Important battle debug teams should be exactly on par with the opponent's highest level.
p = Path('src/debug.c')
s = p.read_text()
s = s.replace('    u8 testLevel = cap > 2 ? cap - 2 : cap;\n', '    u8 testLevel = cap;\n', 1)
# Make generated debug mons owned by the player so badge obedience rules cannot treat them as traded mons.
old = '    for (u32 i = 0; i < trainer->partySize && i < PARTY_SIZE; i++)\n        ScriptGiveMon(species[i], testLevel, ITEM_NONE);\n    HealPlayerParty();\n'
new = '''    for (u32 i = 0; i < trainer->partySize && i < PARTY_SIZE; i++)\n    {\n        ScriptGiveMon(species[i], testLevel, ITEM_NONE);\n        // Debug battle teams are the player's own test Pokemon, never traded Pokemon.\n        SetMonData(&gPlayerParty[i], MON_DATA_OT_ID, &gSaveBlock2Ptr->playerTrainerId[0]);\n    }\n    HealPlayerParty();\n'''
if old not in s:
    raise SystemExit('Missing important battle party creation block')
s = s.replace(old, new, 1)
p.write_text(s)

# Make stat changes visually unmistakable: vivid green/red with dark shadow.
p = Path('src/battle_controller_player.c')
s = p.read_text()
s = s.replace('static const u8 sStageUpColors[] = { 14, 5, 15 };', 'static const u8 sStageUpColors[] = { 14, 6, 15 };', 1)
s = s.replace('static const u8 sStageDownColors[] = { 14, 4, 15 };', 'static const u8 sStageDownColors[] = { 14, 1, 15 };', 1)
p.write_text(s)
print('Applied important-battle level parity, player ownership, and vivid stage colors')
