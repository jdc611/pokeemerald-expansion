from pathlib import Path


def replace_once(text, old, new, label):
    if new in text:
        return text
    if old not in text:
        raise SystemExit(f"Missing expected block: {label}")
    return text.replace(old, new, 1)

# Make the status-detail positive stage color visibly light green.
p = Path("src/battle_controller_player.c")
s = p.read_text()
s = replace_once(
    s,
    'static const u8 sStageUpColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_GREEN, TEXT_COLOR_DARK_GRAY };',
    'static const u8 sStageUpColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_LIGHT_GREEN, TEXT_COLOR_DARK_GRAY };',
    'positive stage light green',
)

# Put the status hint inside the normal action-prompt window instead of reusing
# the YOU/FOE bookmark. This keeps the bookmark untouched and makes the hint
# exist only on the Fight/Pokemon/Bag/Run home screen.
helper_anchor = '''static void RestoreBattleStagePanelUnderlay(void)\n{\n    CopyToBgTilemapBufferRect(0, sStagePanelUnderlay, 0, 33, 30, 7);\n    CopyBgTilemapBufferToVram(0);\n}\n'''
helper = '''static void RestoreBattleStagePanelUnderlay(void)\n{\n    CopyToBgTilemapBufferRect(0, sStagePanelUnderlay, 0, 33, 30, 7);\n    CopyBgTilemapBufferToVram(0);\n}\n\nstatic void ShowStatusDetailsPrompt(void)\n{\n    static const u8 sStatusHint[] = _("L:STATUS");\n    static const u8 sStatusHintColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_DARK_GRAY, TEXT_COLOR_LIGHT_GRAY };\n\n    AddTextPrinterParameterized3(B_WIN_ACTION_PROMPT, FONT_SMALL, 0, 24, sStatusHintColors, 0, sStatusHint);\n    CopyWindowToVram(B_WIN_ACTION_PROMPT, COPYWIN_GFX);\n}\n'''
s = replace_once(s, helper_anchor, helper, 'status hint helper')

restore_old = '''            else\n                BattlePutTextOnWindow(gDisplayedStringBattle, B_WIN_ACTION_PROMPT);\n            ActionSelectionCreateCursorAt(gActionSelectionCursor[battler], 0);'''
restore_new = '''            else\n                BattlePutTextOnWindow(gDisplayedStringBattle, B_WIN_ACTION_PROMPT);\n            ShowStatusDetailsPrompt();\n            ActionSelectionCreateCursorAt(gActionSelectionCursor[battler], 0);'''
s = replace_once(s, restore_old, restore_new, 'status hint after detail close')

home_old = '''    else\n    {\n        BattlePutTextOnWindow(gDisplayedStringBattle, B_WIN_ACTION_PROMPT);\n    }\n}\n\nstatic void PlayerHandleYesNoBox'''
home_new = '''    else\n    {\n        BattlePutTextOnWindow(gDisplayedStringBattle, B_WIN_ACTION_PROMPT);\n    }\n    ShowStatusDetailsPrompt();\n}\n\nstatic void PlayerHandleYesNoBox'''
s = replace_once(s, home_old, home_new, 'status hint on action home')

# Clamp at the controller boundary too. This is the final value actually handed
# to the EXP task, so at/above the active cap it cannot accidentally receive the
# earlier calculated normal reward.
exp_old = '''        LoadBattleBarGfx(1);\n        expPointsToGive = T1_READ_32(&gBattleResources->bufferA[battler][2]);\n        taskId = CreateTask(Task_GiveExpToMon, 10);'''
exp_new = '''        LoadBattleBarGfx(1);\n        expPointsToGive = T1_READ_32(&gBattleResources->bufferA[battler][2]);\n        if (GetMonData(&gParties[B_TRAINER_PLAYER][monId], MON_DATA_LEVEL) >= GetCurrentLevelCap())\n            expPointsToGive = 1;\n        taskId = CreateTask(Task_GiveExpToMon, 10);'''
s = replace_once(s, exp_old, exp_new, 'controller cap EXP clamp')
p.write_text(s)

# Native hard-cap reward should also be 1 at the calculation source.
p = Path("src/battle_script_commands.c")
s = p.read_text()
old = '''if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= levelCap)\n                            gBattleStruct->battlerExpReward = 0;'''
new = '''if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= levelCap)\n                            gBattleStruct->battlerExpReward = 1;'''
s = replace_once(s, old, new, 'native hard-cap reward')
p.write_text(s)

# Preserve the already-approved early important-battle test party in source and
# give Shroomish Growth so positive-stage green can be tested deterministically.
p = Path("src/debug.c")
s = p.read_text()
old_party = '''    static const u16 sEarlyParty[] =\n    {\n        SPECIES_TREECKO,\n        SPECIES_TORCHIC,\n        SPECIES_MUDKIP,\n        SPECIES_TAILLOW,\n        SPECIES_RALTS,\n        SPECIES_SHROOMISH,\n    };'''
new_party = '''    static const u16 sEarlyParty[] =\n    {\n        SPECIES_SHROOMISH,\n        SPECIES_LOTAD,\n        SPECIES_MANKEY,\n        SPECIES_TREECKO,\n        SPECIES_MUDKIP,\n        SPECIES_MARILL,\n    };'''
s = replace_once(s, old_party, new_party, 'approved early test party')

move_old = '''        SetMonData(&gPlayerParty[i], MON_DATA_OT_ID, &gSaveBlock2Ptr->playerTrainerId[0]);\n        {\n            u8 metLevel = testLevel;\n            SetMonData(&gPlayerParty[i], MON_DATA_MET_LEVEL, &metLevel);\n        }'''
move_new = '''        SetMonData(&gPlayerParty[i], MON_DATA_OT_ID, &gSaveBlock2Ptr->playerTrainerId[0]);\n        {\n            u8 metLevel = testLevel;\n            SetMonData(&gPlayerParty[i], MON_DATA_MET_LEVEL, &metLevel);\n        }\n        if (i == 0 && cap <= 19)\n        {\n            u16 growth = MOVE_GROWTH;\n            SetMonData(&gPlayerParty[i], MON_DATA_MOVE1, &growth);\n            SetMonData(&gPlayerParty[i], MON_DATA_PP1, &gMovesInfo[MOVE_GROWTH].pp);\n        }'''
s = replace_once(s, move_old, move_new, 'Growth test move')
p.write_text(s)

print('Applied native status hint, green stages, 1-EXP cap, and approved test party')
