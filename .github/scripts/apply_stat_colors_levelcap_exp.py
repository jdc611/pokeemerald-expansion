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

# Narrow/tall far-left prompt window.
p = Path("src/battle_bg.c")
s = p.read_text()
old = '''    [B_WIN_STAGE_TAB] = {\n        .bg = 0, .tilemapLeft = 1, .tilemapTop = 33,\n        .width = 8, .height = 2, .paletteNum = 5, .baseBlock = 0x03E0,\n    },'''
new = '''    [B_WIN_STAGE_TAB] = {\n        .bg = 0, .tilemapLeft = 0, .tilemapTop = 31,\n        .width = 5, .height = 4, .paletteNum = 5, .baseBlock = 0x03E0,\n    },'''
s = must_replace(s, old, new, 'standard status tab window')
p.write_text(s)

# Status details UI and positive-stage color.
p = Path("src/battle_controller_player.c")
s = p.read_text()
s = s.replace(
    'static const u8 sStageUpColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_GREEN, TEXT_COLOR_DARK_GRAY };',
    'static const u8 sStageUpColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_LIGHT_GREEN, TEXT_COLOR_DARK_GRAY };'
)
s = s.replace(
    'static const u8 sStageUpColors[] = { 14, 5, 15 };',
    'static const u8 sStageUpColors[] = { 14, 6, 15 };'
)

anchor = 'static bool8 sStagePanelOpen = FALSE;\n'
helper = '''static const u8 sStatusDetailsLabel[] = _("L\\nSTATUS");\nstatic const u8 sStatusDetailsColors[] = { 14, 13, 15 };\n\nstatic void ShowStatusDetailsPrompt(void)\n{\n    FillWindowPixelBuffer(B_WIN_STAGE_TAB, PIXEL_FILL(14));\n    FillWindowPixelRect(B_WIN_STAGE_TAB, PIXEL_FILL(13), 0, 0, 40, 2);\n    FillWindowPixelRect(B_WIN_STAGE_TAB, PIXEL_FILL(13), 0, 0, 2, 32);\n    FillWindowPixelRect(B_WIN_STAGE_TAB, PIXEL_FILL(13), 38, 0, 2, 32);\n    FillWindowPixelRect(B_WIN_STAGE_TAB, PIXEL_FILL(13), 0, 30, 40, 2);\n    AddTextPrinterParameterized3(B_WIN_STAGE_TAB, FONT_SMALL, 5, 2, sStatusDetailsColors, 0, sStatusDetailsLabel);\n    PutWindowTilemap(B_WIN_STAGE_TAB);\n    CopyWindowToVram(B_WIN_STAGE_TAB, COPYWIN_FULL);\n}\n\nstatic void HideStatusDetailsPrompt(void)\n{\n    ClearWindowTilemap(B_WIN_STAGE_TAB);\n    CopyWindowToVram(B_WIN_STAGE_TAB, COPYWIN_MAP);\n}\n\n'''
if helper not in s:
    s = must_replace(s, anchor, helper + anchor, 'status details helper anchor')

s = s.replace('FillWindowPixelRect(B_WIN_STAGE_TAB, PIXEL_FILL(13), 0, 1, 56, 15);',
              'FillWindowPixelRect(B_WIN_STAGE_TAB, PIXEL_FILL(13), 0, 1, 36, 15);')
s = s.replace('FillWindowPixelRect(B_WIN_STAGE_TAB, PIXEL_FILL(13), 56, 3, 4, 13);',
              'FillWindowPixelRect(B_WIN_STAGE_TAB, PIXEL_FILL(13), 36, 3, 2, 13);')
s = s.replace('FillWindowPixelRect(B_WIN_STAGE_TAB, PIXEL_FILL(13), 60, 5, 4, 11);',
              'FillWindowPixelRect(B_WIN_STAGE_TAB, PIXEL_FILL(13), 38, 5, 2, 11);')
s = s.replace('AddTextPrinterParameterized3(B_WIN_STAGE_TAB, FONT_SMALL, 8, 2, sTabColors, 0, heading);',
              'AddTextPrinterParameterized3(B_WIN_STAGE_TAB, FONT_SMALL, 4, 2, sTabColors, 0, heading);')

old = '''            ActionSelectionCreateCursorAt(gActionSelectionCursor[battler], 0);\n        }\n        return;'''
new = '''            ActionSelectionCreateCursorAt(gActionSelectionCursor[battler], 0);\n            ShowStatusDetailsPrompt();\n        }\n        return;'''
s = must_replace(s, old, new, 'restore prompt after details')

old = '''        sStagePanelOpen = TRUE;\n        sStagePanelSlot = 0;\n        ActionSelectionDestroyCursorAt(gActionSelectionCursor[battler]);'''
new = '''        sStagePanelOpen = TRUE;\n        sStagePanelSlot = 0;\n        HideStatusDetailsPrompt();\n        ActionSelectionDestroyCursorAt(gActionSelectionCursor[battler]);'''
s = must_replace(s, old, new, 'hide prompt opening details')

old = '''    if (JOY_NEW(A_BUTTON))\n    {\n        PlaySE(SE_SELECT);\n        TryHideLastUsedBall();'''
new = '''    if (JOY_NEW(A_BUTTON))\n    {\n        PlaySE(SE_SELECT);\n        HideStatusDetailsPrompt();\n        TryHideLastUsedBall();'''
s = must_replace(s, old, new, 'hide prompt on action select')

# Actual current PlayerHandleChooseAction has cursor cleanup and last-ball restore
# between drawing the menu and creating its cursor. Anchor directly to the
# cursor creation that follows TryRestoreLastUsedBall instead of assuming they
# are adjacent.
old = '''    TryRestoreLastUsedBall();\n    ActionSelectionCreateCursorAt(gActionSelectionCursor[battler], 0);\n    PREPARE_MON_NICK_BUFFER(gBattleTextBuff1, battler, gBattlerPartyIndexes[battler]);'''
new = '''    TryRestoreLastUsedBall();\n    ActionSelectionCreateCursorAt(gActionSelectionCursor[battler], 0);\n    ShowStatusDetailsPrompt();\n    PREPARE_MON_NICK_BUFFER(gBattleTextBuff1, battler, gBattlerPartyIndexes[battler]);'''
s = must_replace(s, old, new, 'actual normal action-menu cursor sequence')
p.write_text(s)

# Exactly 1 EXP at the current active cap.
p = Path("src/battle_script_commands.c")
s = p.read_text()
s = s.replace(
    '''if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= levelCap)\n                            gBattleStruct->battlerExpReward = 0;''',
    '''if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= levelCap)\n                            gBattleStruct->battlerExpReward = 1;'''
)
needle = '                    PREPARE_MON_NICK_WITH_PREFIX_BUFFER(gBattleTextBuff1, 0, *expMonId);\n'
clamp = '''                    if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= GetCurrentLevelCap())\n                        gBattleStruct->battlerExpReward = 1;\n\n                    PREPARE_MON_NICK_WITH_PREFIX_BUFFER(gBattleTextBuff1, 0, *expMonId);\n'''
if clamp not in s:
    s = must_replace(s, needle, clamp, 'EXP display clamp')
emit = '                BtlController_EmitExpUpdate(0, B_COMM_TO_CONTROLLER, *expMonId, gBattleStruct->battlerExpReward);\n'
emit_new = '''                if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= GetCurrentLevelCap())\n                    gBattleStruct->battlerExpReward = 1;\n                BtlController_EmitExpUpdate(0, B_COMM_TO_CONTROLLER, *expMonId, gBattleStruct->battlerExpReward);\n'''
if emit_new not in s:
    s = must_replace(s, emit, emit_new, 'EXP controller clamp')
p.write_text(s)

# Roxanne-legal debug party, all normalized by existing debug code to the
# current important-battle cap.
p = Path("src/debug.c")
s = p.read_text()
old = '''    static const u16 sEarlyParty[] =\n    {\n        SPECIES_TREECKO,\n        SPECIES_TORCHIC,\n        SPECIES_MUDKIP,\n        SPECIES_TAILLOW,\n        SPECIES_RALTS,\n        SPECIES_SHROOMISH,\n    };'''
new = '''    static const u16 sEarlyParty[] =\n    {\n        SPECIES_SHROOMISH,\n        SPECIES_LOTAD,\n        SPECIES_MANKEY,\n        SPECIES_TREECKO,\n        SPECIES_MUDKIP,\n        SPECIES_MARILL,\n    };'''
s = must_replace(s, old, new, 'early important battle test party')
p.write_text(s)

print('Final battle status UI, cap EXP, and Roxanne test party patch applied')
