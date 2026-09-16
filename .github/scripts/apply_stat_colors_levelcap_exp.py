from pathlib import Path


def replace_once(path, old, new, label):
    p = Path(path)
    s = p.read_text()
    if old not in s:
        raise SystemExit(f'{label}: expected source anchor not found in {path}')
    s = s.replace(old, new, 1)
    p.write_text(s)
    print(f'APPLIED: {label}')

# Battle stat-stage detail colors. These numeric palette entries are deliberate:
# 5 = vivid green used for boosts; 1 = the previously approved vivid red for drops.
replace_once(
    'src/battle_controller_player.c',
    'static const u8 sStageUpColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_GREEN, TEXT_COLOR_DARK_GRAY };\n            static const u8 sStageDownColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_RED, TEXT_COLOR_DARK_GRAY };',
    'static const u8 sStageUpColors[] = { 14, 5, 15 };\n            static const u8 sStageDownColors[] = { 14, 1, 15 };',
    'vivid green boosts / vivid red drops',
)

# Radical-Red-style hard level cap: a Pokemon already at the current cap receives
# exactly 1 EXP from an otherwise eligible battle instead of the previous 0 EXP.
# This does not allow a level-up beyond the cap because the cap clamp still applies
# to Pokemon below the cap and capped Pokemon only receive this single point.
replace_once(
    'src/battle_script_commands.c',
    'if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= levelCap)\n                            gBattleStruct->battlerExpReward = 0;',
    'if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= levelCap)\n                            gBattleStruct->battlerExpReward = 1;',
    '1 EXP at hard level cap',
)

print('STAT_COLOR_LEVEL_CAP_EXP_IMPLEMENTATION_OK')
