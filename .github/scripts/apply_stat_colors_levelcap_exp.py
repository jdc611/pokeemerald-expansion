from pathlib import Path


def replace_once(path, old, new, label):
    p = Path(path)
    s = p.read_text()
    if old not in s:
        raise SystemExit(f'{label}: expected source anchor not found in {path}')
    p.write_text(s.replace(old, new, 1))
    print(f'APPLIED: {label}')

# Preserve the known-good battle/obedience source and change only the stat-panel
# text palettes. Boost detail text uses vivid green; drops use the approved vivid red.
replace_once(
    'src/battle_controller_player.c',
    'static const u8 sStageUpColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_GREEN, TEXT_COLOR_DARK_GRAY };\n            static const u8 sStageDownColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_RED, TEXT_COLOR_DARK_GRAY };',
    'static const u8 sStageUpColors[] = { 14, 5, 15 };\n            static const u8 sStageDownColors[] = { 14, 1, 15 };',
    'vivid green boost text / vivid red drop text',
)

# Hard cap: force the final reward value to exactly one for a Pokemon already at
# the current cap. Do this after the normal reward calculation, immediately before
# the reward is consumed by the EXP controller path.
p = Path('src/battle_script_commands.c')
s = p.read_text()
old = '''if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= levelCap)\n                            gBattleStruct->battlerExpReward = 0;'''
new = '''if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= levelCap)\n                            gBattleStruct->battlerExpReward = 1;'''
if old not in s:
    raise SystemExit('level-cap final reward anchor not found; refusing EXP guess')
s = s.replace(old, new, 1)
p.write_text(s)
print('APPLIED: exact 1 EXP at hard level cap')

print('CORRECTIVE_BATTLE_PATCH_OK')
