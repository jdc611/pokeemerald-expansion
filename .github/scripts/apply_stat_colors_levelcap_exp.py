from pathlib import Path


def replace_once(path, old, new, label):
    p = Path(path)
    s = p.read_text()
    if old not in s:
        raise SystemExit(f'{label}: expected source anchor not found in {path}')
    p.write_text(s.replace(old, new, 1))
    print(f'APPLIED: {label}')

# Stat detail colors: preserve the working vivid red and use the brighter green slot.
replace_once(
    'src/battle_controller_player.c',
    'static const u8 sStageUpColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_GREEN, TEXT_COLOR_DARK_GRAY };\n            static const u8 sStageDownColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_RED, TEXT_COLOR_DARK_GRAY };',
    'static const u8 sStageUpColors[] = { 14, 6, 15 };\n            static const u8 sStageDownColors[] = { 14, 1, 15 };',
    'vivid green boost detail / preserve vivid red drop detail',
)

# HUD arrows: put both player and foe markers on the nickname/level row.
# Major status stays on its normal lower-row slot and no longer hides the arrows.
replace_once(
    'src/battle_interface.c',
    '''    // Stage markers belong only on the normal action HUD. Never cover status text
    // and never leak into move details, messages, or other battle sub-screens.
    if (gSprites[healthboxId].invisible || !IsBattlerAlive(battler)
     || gBattleMons[battler].status1 != STATUS1_NONE
     || gBattleResources->bufferA[0][0] != CONTROLLER_CHOOSEACTION)
    {
        sprite->invisible = TRUE;
        return;
    }''',
    '''    // Stage markers belong only on the normal action HUD. They live on the
    // nickname/level row, so major status can use its normal lower-row slot.
    if (gSprites[healthboxId].invisible || !IsBattlerAlive(battler)
     || gBattleResources->bufferA[0][0] != CONTROLLER_CHOOSEACTION)
    {
        sprite->invisible = TRUE;
        return;
    }''',
    'keep stat arrows visible while statused',
)
replace_once(
    'src/battle_interface.c',
    '''    sprite->x = gSprites[healthboxId].x - (IsOnPlayerSide(battler) ? 12 : 16);
    sprite->y = gSprites[healthboxId].y + (IsOnPlayerSide(battler) ? 8 : 6);''',
    '''    // 16x8 marker centered in the reserved gap immediately before the level.
    sprite->x = gSprites[healthboxId].x + 56;
    sprite->y = gSprites[healthboxId].y - 8;''',
    'move player/foe arrows between nickname and level',
)
replace_once(
    'src/battle_interface.c',
    '    u32 fontId = GetFontIdToFit(gDisplayedStringBattle, FONT_SMALL, 0, 55);',
    '    u32 fontId = GetFontIdToFit(gDisplayedStringBattle, FONT_SMALL, 0, 39);',
    'reserve nickname/level gap for stage arrows',
)

# Level-cap EXP: the project cap itself is authoritative. A Pokemon already at that
# cap gets exactly one EXP, regardless of the expansion's generic EXP_CAP_TYPE.
replace_once(
    'src/battle_script_commands.c',
    '''                    if (B_EXP_CAP_TYPE == EXP_CAP_HARD && gBattleStruct->battlerExpReward != 0)
                    {
                        enum GrowthRate growthRate = gSpeciesInfo[GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_SPECIES)].growthRate;
                        u32 currentExp = GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_EXP);
                        u32 levelCap = GetCurrentLevelCap();

                        if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= levelCap)
                            gBattleStruct->battlerExpReward = 0;
                        else if (gExperienceTables[growthRate][levelCap] < currentExp + gBattleStruct->battlerExpReward)
                            gBattleStruct->battlerExpReward = gExperienceTables[growthRate][levelCap] - currentExp;
                    }''',
    '''                    {
                        enum GrowthRate growthRate = gSpeciesInfo[GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_SPECIES)].growthRate;
                        u32 currentExp = GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_EXP);
                        u32 levelCap = GetCurrentLevelCap();

                        if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= levelCap)
                            gBattleStruct->battlerExpReward = 1;
                        else if (B_EXP_CAP_TYPE == EXP_CAP_HARD
                              && gExperienceTables[growthRate][levelCap] < currentExp + gBattleStruct->battlerExpReward)
                            gBattleStruct->battlerExpReward = gExperienceTables[growthRate][levelCap] - currentExp;
                    }''',
    'force displayed reward to 1 EXP at current level cap',
)
replace_once(
    'src/battle_script_commands.c',
    '''                BtlController_EmitExpUpdate(0, B_COMM_TO_CONTROLLER, *expMonId, gBattleStruct->battlerExpReward);
                MarkBattlerForControllerExec(0);''',
    '''                if (currLvl >= GetCurrentLevelCap())
                    gBattleStruct->battlerExpReward = 1;
                BtlController_EmitExpUpdate(0, B_COMM_TO_CONTROLLER, *expMonId, gBattleStruct->battlerExpReward);
                MarkBattlerForControllerExec(0);''',
    'final controller handoff clamped to 1 EXP at cap',
)

print('HUD_STAT_EXP_FIX_V3_OK')
