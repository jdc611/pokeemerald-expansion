from pathlib import Path


def must_replace(text, old, new, label):
    if old not in text:
        raise SystemExit(f"Missing expected block: {label}")
    return text.replace(old, new, 1)

# Remove experimental healthbox stat arrows.
p = Path("src/battle_interface.c")
s = p.read_text()
old = '''    if (GetSpriteTileStartByTag(TAG_STAGE_MARKER_GFX) == 0xFFFF)\n    {\n        LoadSpriteSheet(&sStatStageMarkerSheet);\n        LoadSpritePalette(&sStatStageMarkerPal);\n    }\n    u8 stageMarkerId = CreateSprite(&sStatStageMarkerTemplate, DISPLAY_WIDTH, DISPLAY_HEIGHT, 0);\n    if (stageMarkerId != MAX_SPRITES)\n    {\n        gSprites[stageMarkerId].data[0] = healthboxLeftSpriteId;\n        gSprites[stageMarkerId].data[1] = battler;\n        gSprites[stageMarkerId].invisible = TRUE;\n    }\n\n'''
if old in s:
    s = s.replace(old, '', 1)
p.write_text(s)

# Keep the original 8x2 window for YOU/FOE so the details bookmark is restored.
# The home-screen prompt is drawn as a tiny L badge inside that window instead
# of resizing the shared window and corrupting the details tab.
p = Path("src/battle_bg.c")
s = p.read_text()
# Intentionally leave B_WIN_STAGE_TAB at its stock custom 8x2 geometry.
p.write_text(s)

p = Path("src/battle_controller_player.c")
s = p.read_text()

# Use explicit palette index 6 for boosts. Runtime proved the named GREEN entry
# was the dark color; index 6 is the bright green battle-text entry.
s = s.replace(
    'static const u8 sStageUpColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_GREEN, TEXT_COLOR_DARK_GRAY };',
    'static const u8 sStageUpColors[] = { 14, 6, 15 };'
)

anchor = 'static bool8 sStagePanelOpen = FALSE;\n'
helper = '''static const u8 sStatusDetailsLabel[] = _("L");\nstatic const u8 sStatusDetailsColors[] = { 14, 13, 15 };\n\nstatic void ShowStatusDetailsPrompt(void)\n{\n    // Tiny far-left badge. The shared 8x2 window remains unchanged so YOU/FOE\n    // retains its original dimensions when the full details panel is open.\n    FillWindowPixelBuffer(B_WIN_STAGE_TAB, PIXEL_FILL(0));\n    FillWindowPixelRect(B_WIN_STAGE_TAB, PIXEL_FILL(13), 0, 1, 18, 15);\n    AddTextPrinterParameterized3(B_WIN_STAGE_TAB, FONT_SMALL, 6, 2, sStatusDetailsColors, 0, sStatusDetailsLabel);\n    PutWindowTilemap(B_WIN_STAGE_TAB);\n    CopyWindowToVram(B_WIN_STAGE_TAB, COPYWIN_FULL);\n}\n\nstatic void HideStatusDetailsPrompt(void)\n{\n    ClearWindowTilemap(B_WIN_STAGE_TAB);\n    CopyWindowToVram(B_WIN_STAGE_TAB, COPYWIN_MAP);\n}\n\n'''
if helper not in s:
    s = must_replace(s, anchor, helper + anchor, 'status details helper anchor')

# Restore original YOU/FOE bookmark geometry exactly.
# No replacements are needed here because source still has the correct 56/60px layout.

old = '''            ActionSelectionCreateCursorAt(gActionSelectionCursor[battler], 0);\n        }\n        return;'''
new = '''            ActionSelectionCreateCursorAt(gActionSelectionCursor[battler], 0);\n            ShowStatusDetailsPrompt();\n        }\n        return;'''
s = must_replace(s, old, new, 'restore prompt after details')

old = '''        sStagePanelOpen = TRUE;\n        sStagePanelSlot = 0;\n        ActionSelectionDestroyCursorAt(gActionSelectionCursor[battler]);'''
new = '''        sStagePanelOpen = TRUE;\n        sStagePanelSlot = 0;\n        HideStatusDetailsPrompt();\n        ActionSelectionDestroyCursorAt(gActionSelectionCursor[battler]);'''
s = must_replace(s, old, new, 'hide prompt opening details')

old = '''    if (JOY_NEW(A_BUTTON))\n    {\n        PlaySE(SE_SELECT);\n        TryHideLastUsedBall();'''
new = '''    if (JOY_NEW(A_BUTTON))\n    {\n        PlaySE(SE_SELECT);\n        HideStatusDetailsPrompt();\n        TryHideLastUsedBall();'''
s = must_replace(s, old, new, 'hide prompt on action select')

old = '''    TryRestoreLastUsedBall();\n    ActionSelectionCreateCursorAt(gActionSelectionCursor[battler], 0);\n    PREPARE_MON_NICK_BUFFER(gBattleTextBuff1, battler, gBattlerPartyIndexes[battler]);'''
new = '''    TryRestoreLastUsedBall();\n    ActionSelectionCreateCursorAt(gActionSelectionCursor[battler], 0);\n    ShowStatusDetailsPrompt();\n    PREPARE_MON_NICK_BUFFER(gBattleTextBuff1, battler, gBattlerPartyIndexes[battler]);'''
s = must_replace(s, old, new, 'normal action-menu prompt')
p.write_text(s)

# EXP: clamp at the real reward-calculation path. The earlier patch attempted
# to key off a hard-cap config and missed this runtime. Here the active current
# cap is authoritative, and the clamp happens after every multiplier/share
# calculation but before both message buffering and controller application.
p = Path("src/battle_script_commands.c")
s = p.read_text()
needle = '''                    ApplyExperienceMultipliers(&gBattleStruct->battlerExpReward, *expMonId, gBattlerFainted);\n\n                    if (B_EXP_CAP_TYPE == EXP_CAP_HARD && gBattleStruct->battlerExpReward != 0)'''
replacement = '''                    ApplyExperienceMultipliers(&gBattleStruct->battlerExpReward, *expMonId, gBattlerFainted);\n\n                    if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= GetCurrentLevelCap())\n                        gBattleStruct->battlerExpReward = 1;\n\n                    if (B_EXP_CAP_TYPE == EXP_CAP_HARD && gBattleStruct->battlerExpReward != 0)'''
s = must_replace(s, needle, replacement, 'authoritative EXP calculation clamp')
# Prevent the hard-cap branch from changing our 1 back to 0.
s = s.replace(
    '''if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= levelCap)\n                            gBattleStruct->battlerExpReward = 0;''',
    '''if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= levelCap)\n                            gBattleStruct->battlerExpReward = 1;'''
)
# Belt-and-suspenders at the exact controller handoff.
emit = '                BtlController_EmitExpUpdate(0, B_COMM_TO_CONTROLLER, *expMonId, gBattleStruct->battlerExpReward);\n'
emit_new = '''                if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= GetCurrentLevelCap())\n                    gBattleStruct->battlerExpReward = 1;\n                BtlController_EmitExpUpdate(0, B_COMM_TO_CONTROLLER, *expMonId, gBattleStruct->battlerExpReward);\n'''
s = must_replace(s, emit, emit_new, 'EXP controller handoff')
p.write_text(s)

# Roxanne test party: legal Lv15 species plus a guaranteed positive-stage move
# on Shroomish so green can be verified immediately. Growth raises Sp. Atk.
p = Path("src/debug.c")
s = p.read_text()
old = '''    static const u16 sEarlyParty[] =\n    {\n        SPECIES_TREECKO,\n        SPECIES_TORCHIC,\n        SPECIES_MUDKIP,\n        SPECIES_TAILLOW,\n        SPECIES_RALTS,\n        SPECIES_SHROOMISH,\n    };'''
new = '''    static const u16 sEarlyParty[] =\n    {\n        SPECIES_SHROOMISH,\n        SPECIES_LOTAD,\n        SPECIES_MANKEY,\n        SPECIES_TREECKO,\n        SPECIES_MUDKIP,\n        SPECIES_MARILL,\n    };'''
s = must_replace(s, old, new, 'Roxanne test species')
old = '''        SetMonData(&gPlayerParty[i], MON_DATA_OT_ID, &gSaveBlock2Ptr->playerTrainerId[0]);\n        {\n            u8 metLevel = testLevel;\n            SetMonData(&gPlayerParty[i], MON_DATA_MET_LEVEL, &metLevel);\n        }'''
new = '''        SetMonData(&gPlayerParty[i], MON_DATA_OT_ID, &gSaveBlock2Ptr->playerTrainerId[0]);\n        {\n            u8 metLevel = testLevel;\n            SetMonData(&gPlayerParty[i], MON_DATA_MET_LEVEL, &metLevel);\n        }\n        if (i == 0 && cap <= 19)\n        {\n            u16 growth = MOVE_GROWTH;\n            SetMonData(&gPlayerParty[i], MON_DATA_MOVE1, &growth);\n            SetMonData(&gPlayerParty[i], MON_DATA_PP1, &gMovesInfo[MOVE_GROWTH].pp);\n        }'''
s = must_replace(s, old, new, 'Shroomish Growth test move')
p.write_text(s)

print('Applied runtime-tested status layout, positive-stage test, and EXP cap fixes')
