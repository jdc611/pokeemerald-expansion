from pathlib import Path


def replace_once(text, old, new, label):
    if new in text:
        return text
    if old not in text:
        raise SystemExit(f"Missing expected block: {label}")
    return text.replace(old, new, 1)

p = Path("src/battle_controller_player.c")
s = p.read_text()

# Positive stages: use the actual GREEN text index (0x6). Runtime showed the
# previous LIGHT_GREEN entry rendered red in this battle window palette.
s = replace_once(
    s,
    'static const u8 sStageUpColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_GREEN, TEXT_COLOR_DARK_GRAY };',
    'static const u8 sStageUpColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_GREEN, TEXT_COLOR_DARK_GRAY };',
    'positive stage green',
)

# Keep the action hint minimal. Do not write STATUS across the prompt text.
helper_anchor = '''static void RestoreBattleStagePanelUnderlay(void)\n{\n    CopyToBgTilemapBufferRect(0, sStagePanelUnderlay, 0, 33, 30, 7);\n    CopyBgTilemapBufferToVram(0);\n}\n'''
helper = '''static void RestoreBattleStagePanelUnderlay(void)\n{\n    CopyToBgTilemapBufferRect(0, sStagePanelUnderlay, 0, 33, 30, 7);\n    CopyBgTilemapBufferToVram(0);\n}\n\nstatic void ShowStatusDetailsPrompt(void)\n{\n    static const u8 sStatusHint[] = _("L");\n    static const u8 sStatusHintColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_DARK_GRAY, TEXT_COLOR_LIGHT_GRAY };\n\n    // Small L-only control in the lower-left of the command prompt. This avoids\n    // overwriting the normal 'What will ... do?' text while still exposing L.\n    AddTextPrinterParameterized3(B_WIN_ACTION_PROMPT, FONT_SMALL, 2, 25, sStatusHintColors, 0, sStatusHint);\n    CopyWindowToVram(B_WIN_ACTION_PROMPT, COPYWIN_GFX);\n}\n'''
s = replace_once(s, helper_anchor, helper, 'small L hint helper')

restore_old = '''            else\n                BattlePutTextOnWindow(gDisplayedStringBattle, B_WIN_ACTION_PROMPT);\n            ActionSelectionCreateCursorAt(gActionSelectionCursor[battler], 0);'''
restore_new = '''            else\n                BattlePutTextOnWindow(gDisplayedStringBattle, B_WIN_ACTION_PROMPT);\n            ShowStatusDetailsPrompt();\n            ActionSelectionCreateCursorAt(gActionSelectionCursor[battler], 0);'''
s = replace_once(s, restore_old, restore_new, 'hint after details close')

home_old = '''    else\n    {\n        BattlePutTextOnWindow(gDisplayedStringBattle, B_WIN_ACTION_PROMPT);\n    }\n}\n\nstatic void PlayerHandleYesNoBox'''
home_new = '''    else\n    {\n        BattlePutTextOnWindow(gDisplayedStringBattle, B_WIN_ACTION_PROMPT);\n    }\n    ShowStatusDetailsPrompt();\n}\n\nstatic void PlayerHandleYesNoBox'''
s = replace_once(s, home_old, home_new, 'hint on action home')

# Final EXP boundary. GetCurrentLevelCap now returns the selected important
# battle's actual debug-party level instead of 58 from the obedience badges.
exp_old = '''        LoadBattleBarGfx(1);\n        expPointsToGive = T1_READ_32(&gBattleResources->bufferA[battler][2]);\n        taskId = CreateTask(Task_GiveExpToMon, 10);'''
exp_new = '''        LoadBattleBarGfx(1);\n        expPointsToGive = T1_READ_32(&gBattleResources->bufferA[battler][2]);\n        if (GetMonData(&gParties[B_TRAINER_PLAYER][monId], MON_DATA_LEVEL) >= GetCurrentLevelCap())\n            expPointsToGive = 1;\n        taskId = CreateTask(Task_GiveExpToMon, 10);'''
s = replace_once(s, exp_old, exp_new, 'controller 1 EXP clamp')
p.write_text(s)

p = Path("src/battle_script_commands.c")
s = p.read_text()
old = '''if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= levelCap)\n                            gBattleStruct->battlerExpReward = 0;'''
new = '''if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= levelCap)\n                            gBattleStruct->battlerExpReward = 1;'''
s = replace_once(s, old, new, 'native hard-cap 1 EXP')
p.write_text(s)

# Preserve the approved test party and Growth test move.
p = Path("src/debug.c")
s = p.read_text()
old_party = '''    static const u16 sEarlyParty[] =\n    {\n        SPECIES_TREECKO,\n        SPECIES_TORCHIC,\n        SPECIES_MUDKIP,\n        SPECIES_TAILLOW,\n        SPECIES_RALTS,\n        SPECIES_SHROOMISH,\n    };'''
new_party = '''    static const u16 sEarlyParty[] =\n    {\n        SPECIES_SHROOMISH,\n        SPECIES_LOTAD,\n        SPECIES_MANKEY,\n        SPECIES_TREECKO,\n        SPECIES_MUDKIP,\n        SPECIES_MARILL,\n    };'''
s = replace_once(s, old_party, new_party, 'approved early party')
move_old = '''        SetMonData(&gPlayerParty[i], MON_DATA_OT_ID, &gSaveBlock2Ptr->playerTrainerId[0]);\n        {\n            u8 metLevel = testLevel;\n            SetMonData(&gPlayerParty[i], MON_DATA_MET_LEVEL, &metLevel);\n        }'''
move_new = '''        SetMonData(&gPlayerParty[i], MON_DATA_OT_ID, &gSaveBlock2Ptr->playerTrainerId[0]);\n        {\n            u8 metLevel = testLevel;\n            SetMonData(&gPlayerParty[i], MON_DATA_MET_LEVEL, &metLevel);\n        }\n        if (i == 0 && cap <= 19)\n        {\n            u16 growth = MOVE_GROWTH;\n            SetMonData(&gPlayerParty[i], MON_DATA_MOVE1, &growth);\n            SetMonData(&gPlayerParty[i], MON_DATA_PP1, &gMovesInfo[MOVE_GROWTH].pp);\n        }'''
s = replace_once(s, move_old, move_new, 'Growth test move')
p.write_text(s)

print('Applied small L hint, true green positive stages, and debug-aware 1 EXP cap')
