from pathlib import Path


def replace_once(path, old, new, label):
    p = Path(path)
    s = p.read_text()
    if old not in s:
        raise SystemExit(f'{label}: expected source anchor not found in {path}')
    p.write_text(s.replace(old, new, 1))
    print(f'APPLIED: {label}')

# Battle stat-stage detail palette. Keep the previously approved vivid red for drops
# and force boost detail text to the vivid green palette entry.
replace_once(
    'src/battle_controller_player.c',
    'static const u8 sStageUpColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_GREEN, TEXT_COLOR_DARK_GRAY };\n            static const u8 sStageDownColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_RED, TEXT_COLOR_DARK_GRAY };',
    'static const u8 sStageUpColors[] = { 14, 5, 15 };\n            static const u8 sStageDownColors[] = { 14, 1, 15 };',
    'vivid green boost detail / vivid red drop detail',
)

# Hard level cap. This block is after ApplyExperienceMultipliers and before
# BtlController_EmitExpUpdate, so this value is the actual reward sent to the
# player controller. A capped Pokemon receives exactly one EXP.
replace_once(
    'src/battle_script_commands.c',
    '''if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= levelCap)\n                            gBattleStruct->battlerExpReward = 0;''',
    '''if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= levelCap)\n                            gBattleStruct->battlerExpReward = 1;''',
    'final controller reward = 1 EXP at hard cap',
)

print('RUNTIME_BATTLE_PATCH_OK')
