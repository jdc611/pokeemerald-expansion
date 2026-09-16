from pathlib import Path

# Important-battle debug teams: normalize ownership/met data at creation time.
p = Path('src/debug.c')
s = p.read_text()
anchor = '''        ScriptGiveMon(species[i], testLevel, ITEM_NONE);\n        // Debug battle teams are the player's own test Pokemon, never traded Pokemon.\n        SetMonData(&gPlayerParty[i], MON_DATA_OT_ID, &gSaveBlock2Ptr->playerTrainerId[0]);\n'''
replacement = '''        ScriptGiveMon(species[i], testLevel, ITEM_NONE);\n        // Debug battle teams are native player Pokemon. Modern obedience also considers\n        // the level at which a Pokemon was obtained, so normalize both ownership and met level.\n        SetMonData(&gPlayerParty[i], MON_DATA_OT_ID, &gSaveBlock2Ptr->playerTrainerId[0]);\n        {\n            u8 metLevel = testLevel;\n            SetMonData(&gPlayerParty[i], MON_DATA_MET_LEVEL, &metLevel);\n        }\n'''
if anchor not in s:
    raise SystemExit('important battle generated-mon ownership block missing')
s = s.replace(anchor, replacement, 1)
p.write_text(s)

# Positive stat stages: use vivid green; negative red is already confirmed good.
p = Path('src/battle_controller_player.c')
s = p.read_text()
s = s.replace('static const u8 sStageUpColors[] = { 14, 6, 15 };', 'static const u8 sStageUpColors[] = { 14, 2, 15 };', 1)
s = s.replace('static const u8 sStageUpColors[] = { 14, 5, 15 };', 'static const u8 sStageUpColors[] = { 14, 2, 15 };', 1)
p.write_text(s)

print('Applied important-battle met-level obedience normalization and vivid green boosts')
