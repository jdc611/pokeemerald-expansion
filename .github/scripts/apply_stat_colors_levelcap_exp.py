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

# IMPORTANT: the repo was still configured with EXP_CAP_NONE / LEVEL_CAP_NONE.
# That is why changing Cmd_getexp repeatedly never produced the intended cap
# behavior. Enable the project's native flag-list hard cap, then make native
# hard-cap rewards exactly 1 EXP instead of 0.
p = Path("include/config/caps.h")
s = p.read_text()
s = must_replace(s,
    '#define B_EXP_CAP_TYPE                  EXP_CAP_NONE   // [EXP_CAP_NONE, EXP_CAP_HARD, EXP_CAP_SOFT] choose the type of level cap to apply',
    '#define B_EXP_CAP_TYPE                  EXP_CAP_HARD   // [EXP_CAP_NONE, EXP_CAP_HARD, EXP_CAP_SOFT] choose the type of level cap to apply',
    'enable hard EXP cap')
s = must_replace(s,
    '#define B_LEVEL_CAP_TYPE                LEVEL_CAP_NONE // [LEVEL_CAP_NONE, LEVEL_CAP_FLAG_LIST, LEVEL_CAP_VARIABLE] choose the method to derive the level cap',
    '#define B_LEVEL_CAP_TYPE                LEVEL_CAP_FLAG_LIST // [LEVEL_CAP_NONE, LEVEL_CAP_FLAG_LIST, LEVEL_CAP_VARIABLE] choose the method to derive the level cap',
    'enable flag-list level caps')
s = s.replace('#define B_RARE_CANDY_CAP                FALSE', '#define B_RARE_CANDY_CAP                TRUE', 1)
p.write_text(s)

# Status panel: do not share/resize the YOU/FOE bookmark for the home prompt.
# Draw only a tiny L marker at the extreme left of the existing bookmark window.
p = Path("src/battle_controller_player.c")
s = p.read_text()

# Use the same explicit inline color control used elsewhere in this project.
# This bypasses the palette-index guessing that runtime proved was ineffective.
old_func = '''static void AppendBattleStatStage(u8 *line, enum BattlerId battler, u8 index)\n{\n    static const u8 sPlus[] = _("+");\n    static const u8 sMinus[] = _("-");\n    static const u8 sEmpty[] = _("");\n    s8 stage = gBattleMons[battler].statStages[sStagePanelStats[index]] - DEFAULT_STAT_STAGE;\n\n    StringAppend(line, sStagePanelNames[index]);\n    StringAppend(line, stage < 0 ? sMinus : sPlus);\n    ConvertIntToDecimalStringN(StringAppend(line, sEmpty), stage < 0 ? -stage : stage, STR_CONV_MODE_LEFT_ALIGN, 1);\n}\n'''
new_func = '''static void AppendBattleStatStage(u8 *line, enum BattlerId battler, u8 index)\n{\n    static const u8 sPlus[] = _("+");\n    static const u8 sMinus[] = _("-");\n    static const u8 sEmpty[] = _("");\n    static const u8 sGreen[] = _("{COLOR LIGHT_GREEN}");\n    static const u8 sRed[] = _("{COLOR RED}");\n    s8 stage = gBattleMons[battler].statStages[sStagePanelStats[index]] - DEFAULT_STAT_STAGE;\n\n    if (stage > 0)\n        StringAppend(line, sGreen);\n    else if (stage < 0)\n        StringAppend(line, sRed);\n    StringAppend(line, sStagePanelNames[index]);\n    StringAppend(line, stage < 0 ? sMinus : sPlus);\n    ConvertIntToDecimalStringN(StringAppend(line, sEmpty), stage < 0 ? -stage : stage, STR_CONV_MODE_LEFT_ALIGN, 1);\n}\n'''
s = must_replace(s, old_func, new_func, 'inline stat stage colors')

# With inline controls in the string, use the normal panel palette for printing.
old_colors = '''            static const u8 sStageUpColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_GREEN, TEXT_COLOR_DARK_GRAY };\n            static const u8 sStageDownColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_RED, TEXT_COLOR_DARK_GRAY };\n            s8 stage = gBattleMons[battler].statStages[sStagePanelStats[i]] - DEFAULT_STAT_STAGE;\n            const u8 *stageColors = stage > 0 ? sStageUpColors : (stage < 0 ? sStageDownColors : sPanelColors);\n\n            AppendBattleStatStage(line, battler, i);\n            AddTextPrinterParameterized3(B_WIN_STAGE_PANEL, FONT_SMALL,\n                                         12 + (i % 4) * 58, 4 + (i / 4) * 18,\n                                         stageColors, 0, line);'''
new_colors = '''            AppendBattleStatStage(line, battler, i);\n            AddTextPrinterParameterized3(B_WIN_STAGE_PANEL, FONT_SMALL,\n                                         12 + (i % 4) * 58, 4 + (i / 4) * 18,\n                                         sPanelColors, 0, line);'''
s = must_replace(s, old_colors, new_colors, 'remove palette guessing')

anchor = 'static bool8 sStagePanelOpen = FALSE;\n'
helper = '''static const u8 sStatusDetailsLabel[] = _("L");\nstatic const u8 sStatusDetailsColors[] = { 14, 13, 15 };\n\nstatic void ShowStatusDetailsPrompt(void)\n{\n    // Only 2 tiles wide. Clear the remainder of the shared 8x2 bookmark so the\n    // home screen cannot leave the large black rectangle seen in the playtest.\n    FillWindowPixelBuffer(B_WIN_STAGE_TAB, PIXEL_FILL(0));\n    FillWindowPixelRect(B_WIN_STAGE_TAB, PIXEL_FILL(13), 0, 1, 16, 15);\n    AddTextPrinterParameterized3(B_WIN_STAGE_TAB, FONT_SMALL, 5, 2, sStatusDetailsColors, 0, sStatusDetailsLabel);\n    PutWindowTilemap(B_WIN_STAGE_TAB);\n    CopyWindowToVram(B_WIN_STAGE_TAB, COPYWIN_FULL);\n}\n\nstatic void HideStatusDetailsPrompt(void)\n{\n    ClearWindowTilemap(B_WIN_STAGE_TAB);\n    FillWindowPixelBuffer(B_WIN_STAGE_TAB, PIXEL_FILL(0));\n    CopyWindowToVram(B_WIN_STAGE_TAB, COPYWIN_FULL);\n}\n\n'''
if helper not in s:
    s = must_replace(s, anchor, helper + anchor, 'status prompt helper')

old = '''            ActionSelectionCreateCursorAt(gActionSelectionCursor[battler], 0);\n        }\n        return;'''
new = '''            ActionSelectionCreateCursorAt(gActionSelectionCursor[battler], 0);\n            ShowStatusDetailsPrompt();\n        }\n        return;'''
s = must_replace(s, old, new, 'restore prompt after panel')
old = '''        sStagePanelOpen = TRUE;\n        sStagePanelSlot = 0;\n        ActionSelectionDestroyCursorAt(gActionSelectionCursor[battler]);'''
new = '''        sStagePanelOpen = TRUE;\n        sStagePanelSlot = 0;\n        HideStatusDetailsPrompt();\n        ActionSelectionDestroyCursorAt(gActionSelectionCursor[battler]);'''
s = must_replace(s, old, new, 'hide prompt opening panel')
old = '''    if (JOY_NEW(A_BUTTON))\n    {\n        PlaySE(SE_SELECT);\n        TryHideLastUsedBall();'''
new = '''    if (JOY_NEW(A_BUTTON))\n    {\n        PlaySE(SE_SELECT);\n        HideStatusDetailsPrompt();\n        TryHideLastUsedBall();'''
s = must_replace(s, old, new, 'hide prompt entering submenu')
old = '''    TryRestoreLastUsedBall();\n    ActionSelectionCreateCursorAt(gActionSelectionCursor[battler], 0);\n    PREPARE_MON_NICK_BUFFER(gBattleTextBuff1, battler, gBattlerPartyIndexes[battler]);'''
new = '''    TryRestoreLastUsedBall();\n    ActionSelectionCreateCursorAt(gActionSelectionCursor[battler], 0);\n    ShowStatusDetailsPrompt();\n    PREPARE_MON_NICK_BUFFER(gBattleTextBuff1, battler, gBattlerPartyIndexes[battler]);'''
s = must_replace(s, old, new, 'show prompt on action menu')
p.write_text(s)

# Native hard-cap branch: award exactly 1 EXP at/above the active cap.
p = Path("src/battle_script_commands.c")
s = p.read_text()
s = must_replace(s,
    '''if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= levelCap)\n                            gBattleStruct->battlerExpReward = 0;''',
    '''if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= levelCap)\n                            gBattleStruct->battlerExpReward = 1;''',
    'native hard cap 1 EXP')
p.write_text(s)

# Roxanne test party + Growth for deterministic positive-stage testing.
p = Path("src/debug.c")
s = p.read_text()
old = '''    static const u16 sEarlyParty[] =\n    {\n        SPECIES_TREECKO,\n        SPECIES_TORCHIC,\n        SPECIES_MUDKIP,\n        SPECIES_TAILLOW,\n        SPECIES_RALTS,\n        SPECIES_SHROOMISH,\n    };'''
new = '''    static const u16 sEarlyParty[] =\n    {\n        SPECIES_SHROOMISH,\n        SPECIES_LOTAD,\n        SPECIES_MANKEY,\n        SPECIES_TREECKO,\n        SPECIES_MUDKIP,\n        SPECIES_MARILL,\n    };'''
s = must_replace(s, old, new, 'Roxanne party')
old = '''        SetMonData(&gPlayerParty[i], MON_DATA_OT_ID, &gSaveBlock2Ptr->playerTrainerId[0]);\n        {\n            u8 metLevel = testLevel;\n            SetMonData(&gPlayerParty[i], MON_DATA_MET_LEVEL, &metLevel);\n        }'''
new = '''        SetMonData(&gPlayerParty[i], MON_DATA_OT_ID, &gSaveBlock2Ptr->playerTrainerId[0]);\n        {\n            u8 metLevel = testLevel;\n            SetMonData(&gPlayerParty[i], MON_DATA_MET_LEVEL, &metLevel);\n        }\n        if (i == 0 && cap <= 19)\n        {\n            u16 growth = MOVE_GROWTH;\n            SetMonData(&gPlayerParty[i], MON_DATA_MOVE1, &growth);\n            SetMonData(&gPlayerParty[i], MON_DATA_PP1, &gMovesInfo[MOVE_GROWTH].pp);\n        }'''
s = must_replace(s, old, new, 'Growth test move')
p.write_text(s)

print('Applied native cap enable, 1 EXP, inline stat colors, and compact L badge')
