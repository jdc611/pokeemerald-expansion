from pathlib import Path


def must_replace(text, old, new, label):
    if old not in text:
        raise SystemExit(f"Missing expected block: {label}")
    return text.replace(old, new, 1)

# ---------------------------------------------------------------------------
# Battle interface: remove the experimental stat arrows completely.
# ---------------------------------------------------------------------------
p = Path("src/battle_interface.c")
s = p.read_text()

# Do not create stage-marker sprites at all. This guarantees no arrows can
# overlap healthboxes/status ailments regardless of submenu or battle state.
old = '''    if (GetSpriteTileStartByTag(TAG_STAGE_MARKER_GFX) == 0xFFFF)\n    {\n        LoadSpriteSheet(&sStatStageMarkerSheet);\n        LoadSpritePalette(&sStatStageMarkerPal);\n    }\n    u8 stageMarkerId = CreateSprite(&sStatStageMarkerTemplate, DISPLAY_WIDTH, DISPLAY_HEIGHT, 0);\n    if (stageMarkerId != MAX_SPRITES)\n    {\n        gSprites[stageMarkerId].data[0] = healthboxLeftSpriteId;\n        gSprites[stageMarkerId].data[1] = battler;\n        gSprites[stageMarkerId].invisible = TRUE;\n    }\n\n'''
if old in s:
    s = s.replace(old, '', 1)
p.write_text(s)

# ---------------------------------------------------------------------------
# Battle windows: make the L prompt narrow/tall on the far-left edge.
# It exists only while CHOOSEACTION is active because controller code below
# explicitly shows it there and hides it before every submenu/action.
# ---------------------------------------------------------------------------
p = Path("src/battle_bg.c")
s = p.read_text()
old = '''    [B_WIN_STAGE_TAB] = {\n        .bg = 0, .tilemapLeft = 1, .tilemapTop = 33,\n        .width = 8, .height = 2, .paletteNum = 5, .baseBlock = 0x03E0,\n    },'''
new = '''    [B_WIN_STAGE_TAB] = {\n        .bg = 0, .tilemapLeft = 0, .tilemapTop = 31,\n        .width = 5, .height = 4, .paletteNum = 5, .baseBlock = 0x03E0,\n    },'''
s = must_replace(s, old, new, 'standard status tab window')
p.write_text(s)

# ---------------------------------------------------------------------------
# Player battle controller: green boosts + compact Status Details prompt.
# ---------------------------------------------------------------------------
p = Path("src/battle_controller_player.c")
s = p.read_text()

# Explicit bright green/red palette values.  Red was already visually correct;
# bright green uses the light-green battle text entry rather than dark green.
s = s.replace(
    'static const u8 sStageUpColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_GREEN, TEXT_COLOR_DARK_GRAY };',
    'static const u8 sStageUpColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_LIGHT_GREEN, TEXT_COLOR_DARK_GRAY };'
)
s = s.replace(
    'static const u8 sStageUpColors[] = { 14, 5, 15 };',
    'static const u8 sStageUpColors[] = { 14, 6, 15 };'
)

# Add a dedicated compact action-screen prompt. The details panel continues to
# use the same window as its YOU/FOE bookmark while open.
anchor = 'static bool8 sStagePanelOpen = FALSE;\n'
helper = '''static const u8 sStatusDetailsLabel[] = _("L\\nSTATUS");\nstatic const u8 sStatusDetailsColors[] = { 14, 13, 15 };\n\nstatic void ShowStatusDetailsPrompt(void)\n{\n    FillWindowPixelBuffer(B_WIN_STAGE_TAB, PIXEL_FILL(14));\n    FillWindowPixelRect(B_WIN_STAGE_TAB, PIXEL_FILL(13), 0, 0, 40, 2);\n    FillWindowPixelRect(B_WIN_STAGE_TAB, PIXEL_FILL(13), 0, 0, 2, 32);\n    FillWindowPixelRect(B_WIN_STAGE_TAB, PIXEL_FILL(13), 38, 0, 2, 32);\n    FillWindowPixelRect(B_WIN_STAGE_TAB, PIXEL_FILL(13), 0, 30, 40, 2);\n    AddTextPrinterParameterized3(B_WIN_STAGE_TAB, FONT_SMALL, 5, 2, sStatusDetailsColors, 0, sStatusDetailsLabel);\n    PutWindowTilemap(B_WIN_STAGE_TAB);\n    CopyWindowToVram(B_WIN_STAGE_TAB, COPYWIN_FULL);\n}\n\nstatic void HideStatusDetailsPrompt(void)\n{\n    ClearWindowTilemap(B_WIN_STAGE_TAB);\n    CopyWindowToVram(B_WIN_STAGE_TAB, COPYWIN_MAP);\n}\n\n'''
if helper not in s:
    s = must_replace(s, anchor, helper + anchor, 'status details helper anchor')

# The details panel tab itself must fit the now narrow window.
s = s.replace('FillWindowPixelRect(B_WIN_STAGE_TAB, PIXEL_FILL(13), 0, 1, 56, 15);',
              'FillWindowPixelRect(B_WIN_STAGE_TAB, PIXEL_FILL(13), 0, 1, 36, 15);')
s = s.replace('FillWindowPixelRect(B_WIN_STAGE_TAB, PIXEL_FILL(13), 56, 3, 4, 13);',
              'FillWindowPixelRect(B_WIN_STAGE_TAB, PIXEL_FILL(13), 36, 3, 2, 13);')
s = s.replace('FillWindowPixelRect(B_WIN_STAGE_TAB, PIXEL_FILL(13), 60, 5, 4, 11);',
              'FillWindowPixelRect(B_WIN_STAGE_TAB, PIXEL_FILL(13), 38, 5, 2, 11);')
s = s.replace('AddTextPrinterParameterized3(B_WIN_STAGE_TAB, FONT_SMALL, 8, 2, sTabColors, 0, heading);',
              'AddTextPrinterParameterized3(B_WIN_STAGE_TAB, FONT_SMALL, 4, 2, sTabColors, 0, heading);')

# When closing details, restore the compact prompt because we are back on the
# FIGHT/BAG/POKEMON/RUN page.
old = '''            ActionSelectionCreateCursorAt(gActionSelectionCursor[battler], 0);\n        }\n        return;'''
new = '''            ActionSelectionCreateCursorAt(gActionSelectionCursor[battler], 0);\n            ShowStatusDetailsPrompt();\n        }\n        return;'''
s = must_replace(s, old, new, 'restore prompt after details')

# Hide prompt before opening details so the panel can reuse the same window.
old = '''        sStagePanelOpen = TRUE;\n        sStagePanelSlot = 0;\n        ActionSelectionDestroyCursorAt(gActionSelectionCursor[battler]);'''
new = '''        sStagePanelOpen = TRUE;\n        sStagePanelSlot = 0;\n        HideStatusDetailsPrompt();\n        ActionSelectionDestroyCursorAt(gActionSelectionCursor[battler]);'''
s = must_replace(s, old, new, 'hide prompt opening details')

# Hide it as soon as the user commits to Fight/Bag/Pokemon/Run. This ensures it
# cannot remain visible on move selection or any other submenu.
old = '''    if (JOY_NEW(A_BUTTON))\n    {\n        PlaySE(SE_SELECT);\n        TryHideLastUsedBall();'''
new = '''    if (JOY_NEW(A_BUTTON))\n    {\n        PlaySE(SE_SELECT);\n        HideStatusDetailsPrompt();\n        TryHideLastUsedBall();'''
s = must_replace(s, old, new, 'hide prompt on action select')

# Show the prompt every time the normal action menu is freshly drawn.
# PlayerHandleChooseAction contains this exact menu/cursor sequence.
needle = '''    BattlePutTextOnWindow(gText_BattleMenu, B_WIN_ACTION_MENU);\n    ActionSelectionCreateCursorAt(gActionSelectionCursor[battler], 0);'''
replacement = '''    BattlePutTextOnWindow(gText_BattleMenu, B_WIN_ACTION_MENU);\n    ActionSelectionCreateCursorAt(gActionSelectionCursor[battler], 0);\n    ShowStatusDetailsPrompt();'''
if needle in s:
    s = s.replace(needle, replacement, 1)
else:
    # Fail loudly rather than shipping a build where the prompt lifecycle is uncertain.
    raise SystemExit('Missing normal action-menu draw sequence')

p.write_text(s)

# ---------------------------------------------------------------------------
# EXP: current active cap is authoritative, independent of compile-time cap mode.
# The old attempts were gated behind B_EXP_CAP_TYPE == EXP_CAP_HARD, while this
# project can reach its custom current cap with a different config. Clamp both
# the displayed reward and the exact amount handed to the controller.
# ---------------------------------------------------------------------------
p = Path("src/battle_script_commands.c")
s = p.read_text()

# Existing hard-cap branch should also say 1 rather than 0.
s = s.replace(
    '''if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= levelCap)\n                            gBattleStruct->battlerExpReward = 0;''',
    '''if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= levelCap)\n                            gBattleStruct->battlerExpReward = 1;'''
)

# Unconditional custom-cap clamp after all reward calculations/multipliers and
# immediately before text buffering.
needle = '                    PREPARE_MON_NICK_WITH_PREFIX_BUFFER(gBattleTextBuff1, 0, *expMonId);\n'
clamp = '''                    if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= GetCurrentLevelCap())\n                        gBattleStruct->battlerExpReward = 1;\n\n                    PREPARE_MON_NICK_WITH_PREFIX_BUFFER(gBattleTextBuff1, 0, *expMonId);\n'''
if clamp not in s:
    s = must_replace(s, needle, clamp, 'EXP display clamp')

emit = '                BtlController_EmitExpUpdate(0, B_COMM_TO_CONTROLLER, *expMonId, gBattleStruct->battlerExpReward);\n'
emit_new = '''                if (GetMonData(&gParties[B_TRAINER_PLAYER][*expMonId], MON_DATA_LEVEL) >= GetCurrentLevelCap())\n                    gBattleStruct->battlerExpReward = 1;\n                BtlController_EmitExpUpdate(0, B_COMM_TO_CONTROLLER, *expMonId, gBattleStruct->battlerExpReward);\n'''
if emit_new not in s:
    s = must_replace(s, emit, emit_new, 'EXP controller clamp')
p.write_text(s)

# ---------------------------------------------------------------------------
# Important battle test team: Roxanne-legal, useful matchups at the actual cap.
# Preserve six slots for later important battles, but the first three are the
# requested Shroomish/Lotad/Mankey and all are created at that battle's cap.
# ---------------------------------------------------------------------------
p = Path("src/debug.c")
s = p.read_text()
old = '''    static const u16 sEarlyParty[] =\n    {\n        SPECIES_TREECKO,\n        SPECIES_TORCHIC,\n        SPECIES_MUDKIP,\n        SPECIES_TAILLOW,\n        SPECIES_RALTS,\n        SPECIES_SHROOMISH,\n    };'''
new = '''    static const u16 sEarlyParty[] =\n    {\n        SPECIES_SHROOMISH,\n        SPECIES_LOTAD,\n        SPECIES_MANKEY,\n        SPECIES_TREECKO,\n        SPECIES_MUDKIP,\n        SPECIES_MARILL,\n    };'''
s = must_replace(s, old, new, 'early important battle test party')
p.write_text(s)

print('Final battle status UI, cap EXP, and Roxanne test party patch applied')
