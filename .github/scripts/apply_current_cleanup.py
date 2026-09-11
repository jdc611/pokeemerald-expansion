from pathlib import Path
import re


def must_replace(text, old, new, label):
    if old not in text:
        raise SystemExit(f"Missing expected block: {label}")
    return text.replace(old, new, 1)

# ---------------- Start menu: remove Type Hints from page 2 ----------------
p = Path('src/start_menu.c')
text = p.read_text()
text = text.replace('    AddStartMenuAction(MENU_ACTION_TYPE_HINTS);\n', '', 1)
p.write_text(text)

# ---------------- Options: add visible Type Hints row ----------------
p = Path('src/option_menu.c')
text = p.read_text()
if 'MENUITEM_TYPEHINTS' not in text:
    text = must_replace(text, '#include "constants/rgb.h"\n', '#include "constants/rgb.h"\n#include "event_data.h"\n#include "constants/type_hints.h"\n#include "constants/vars.h"\n', 'option includes')
    text = must_replace(text, '#define tWindowFrameType data[6]\n', '#define tWindowFrameType data[6]\n#define tTypeHints data[7]\n', 'option task data')
    text = must_replace(text, '    MENUITEM_FRAMETYPE,\n    MENUITEM_CANCEL,', '    MENUITEM_FRAMETYPE,\n    MENUITEM_TYPEHINTS,\n    MENUITEM_CANCEL,', 'option enum')
    text = must_replace(text, '#define YPOS_FRAMETYPE    (MENUITEM_FRAMETYPE * 16)\n', '#define YPOS_FRAMETYPE    (MENUITEM_FRAMETYPE * 16)\n#define YPOS_TYPEHINTS    (MENUITEM_TYPEHINTS * 16)\n', 'option ypos')
    text = must_replace(text, 'static void ButtonMode_DrawChoices(u8 selection);\n', 'static void ButtonMode_DrawChoices(u8 selection);\nstatic u8 TypeHints_ProcessInput(u8 selection);\nstatic void TypeHints_DrawChoices(u8 selection);\n', 'option prototypes')
    text = must_replace(text, 'static const u8 gText_ButtonTypeLEqualsA[] = _("{COLOR GREEN}{SHADOW LIGHT_GREEN}L=A");\n', 'static const u8 gText_ButtonTypeLEqualsA[] = _("{COLOR GREEN}{SHADOW LIGHT_GREEN}L=A");\nstatic const u8 gText_TypeHintsAlways[] = _("{COLOR GREEN}{SHADOW LIGHT_GREEN}ALWAYS");\nstatic const u8 gText_TypeHintsSeen[] = _("{COLOR GREEN}{SHADOW LIGHT_GREEN}SEEN");\nstatic const u8 gText_TypeHintsCaught[] = _("{COLOR GREEN}{SHADOW LIGHT_GREEN}CAUGHT");\nstatic const u8 gText_TypeHintsOff[] = _("{COLOR GREEN}{SHADOW LIGHT_GREEN}OFF");\n', 'option strings')
    text = must_replace(text, '    [MENUITEM_FRAMETYPE]   = COMPOUND_STRING("FRAME"),\n    [MENUITEM_CANCEL]', '    [MENUITEM_FRAMETYPE]   = COMPOUND_STRING("FRAME"),\n    [MENUITEM_TYPEHINTS]   = COMPOUND_STRING("TYPE HINTS"),\n    [MENUITEM_CANCEL]', 'option names')
    text = must_replace(text, '        .tilemapTop = 5,\n        .width = 26,\n        .height = 14,', '        .tilemapTop = 4,\n        .width = 26,\n        .height = 16,', 'option window size')
    text = must_replace(text, '        gTasks[taskId].tWindowFrameType = gSaveBlock2Ptr->optionsWindowFrameType;\n', '        gTasks[taskId].tWindowFrameType = gSaveBlock2Ptr->optionsWindowFrameType;\n        gTasks[taskId].tTypeHints = VarGet(VAR_TYPE_HINTS_MODE);\n', 'option init value')
    text = must_replace(text, '        FrameType_DrawChoices(gTasks[taskId].tWindowFrameType);\n', '        FrameType_DrawChoices(gTasks[taskId].tWindowFrameType);\n        TypeHints_DrawChoices(gTasks[taskId].tTypeHints);\n', 'option initial draw')
    old_case = '''        case MENUITEM_FRAMETYPE:\n            previousOption = gTasks[taskId].tWindowFrameType;\n            gTasks[taskId].tWindowFrameType = FrameType_ProcessInput(gTasks[taskId].tWindowFrameType);\n\n            if (previousOption != gTasks[taskId].tWindowFrameType)\n                FrameType_DrawChoices(gTasks[taskId].tWindowFrameType);\n            break;\n'''
    new_case = old_case + '''        case MENUITEM_TYPEHINTS:\n            previousOption = gTasks[taskId].tTypeHints;\n            gTasks[taskId].tTypeHints = TypeHints_ProcessInput(gTasks[taskId].tTypeHints);\n            if (previousOption != gTasks[taskId].tTypeHints)\n                TypeHints_DrawChoices(gTasks[taskId].tTypeHints);\n            break;\n'''
    text = must_replace(text, old_case, new_case, 'option input case')
    text = must_replace(text, '    gSaveBlock2Ptr->optionsWindowFrameType = gTasks[taskId].tWindowFrameType;\n', '    gSaveBlock2Ptr->optionsWindowFrameType = gTasks[taskId].tWindowFrameType;\n    VarSet(VAR_TYPE_HINTS_MODE, gTasks[taskId].tTypeHints);\n', 'option save')

    # Insert simple single-choice renderer before DrawHeaderText.
    anchor = 'static void DrawHeaderText(void)\n'
    impl = '''static u8 TypeHints_ProcessInput(u8 selection)\n{\n    if (JOY_NEW(DPAD_RIGHT))\n    {\n        selection = (selection + 1) % TYPE_HINTS_COUNT;\n        sArrowPressed = TRUE;\n    }\n    else if (JOY_NEW(DPAD_LEFT))\n    {\n        selection = (selection + TYPE_HINTS_COUNT - 1) % TYPE_HINTS_COUNT;\n        sArrowPressed = TRUE;\n    }\n    return selection;\n}\n\nstatic void TypeHints_DrawChoices(u8 selection)\n{\n    const u8 *text;\n    FillWindowPixelRect(WIN_OPTIONS, PIXEL_FILL(1), 110, YPOS_TYPEHINTS, 90, 16);\n    switch (selection)\n    {\n    case TYPE_HINTS_ALWAYS: text = gText_TypeHintsAlways; break;\n    case TYPE_HINTS_CAUGHT: text = gText_TypeHintsCaught; break;\n    case TYPE_HINTS_OFF: text = gText_TypeHintsOff; break;\n    case TYPE_HINTS_SEEN:\n    default: text = gText_TypeHintsSeen; break;\n    }\n    AddTextPrinterParameterized(WIN_OPTIONS, FONT_NORMAL, text, 110, YPOS_TYPEHINTS + 1, TEXT_SKIP_DRAW, NULL);\n}\n\n'''
    idx = text.rfind(anchor)
    if idx < 0:
        raise SystemExit('DrawHeaderText implementation anchor not found')
    text = text[:idx] + impl + text[idx:]
    p.write_text(text)

# ---------------- Battle UI: force a dedicated dynamic palette color ----------------
p = Path('src/battle_controller_player.c')
text = p.read_text()
text = text.replace('_("{COLOR GREEN}{UP_ARROW}+")', '_("{COLOR DYNAMIC_COLOR1}{UP_ARROW}+")')
text = text.replace('_("{COLOR GREEN}{UP_ARROW}")', '_("{COLOR DYNAMIC_COLOR1}{UP_ARROW}")')
text = text.replace('_("{COLOR RED}X")', '_("{COLOR DYNAMIC_COLOR1}X")')
old = '''    // DYNAMIC_COLOR1 is reserved here as the resistance-hint yellow.\n    // The other hint colors use the standard GREEN and RED text slots.\n    {\n        u16 yellow = RGB_YELLOW;\n        u32 paletteNum = GetWindowAttribute(B_WIN_PP, WINDOW_PALETTE_NUM);\n        LoadPalette(&yellow, BG_PLTT_ID(paletteNum) + 10, sizeof(yellow));\n    }\n'''
new = '''    // Use one known battle-text palette slot and recolor it for the current hint.\n    {\n        u16 hintColor;\n        u32 paletteNum = GetWindowAttribute(B_WIN_PP, WINDOW_PALETTE_NUM);\n        switch (foeEffectiveness)\n        {\n        case EFFECTIVENESS_SUPER_EFFECTIVE:\n        case EFFECTIVENESS_EXTREMELY_EFFECTIVE:\n            hintColor = RGB(0, 31, 0);\n            break;\n        case EFFECTIVENESS_NO_EFFECT:\n            hintColor = RGB(31, 0, 0);\n            break;\n        case EFFECTIVENESS_NOT_VERY_EFFECTIVE:\n        case EFFECTIVENESS_MOSTLY_INEFFECTIVE:\n        default:\n            hintColor = RGB(31, 31, 0);\n            break;\n        }\n        LoadPalette(&hintColor, BG_PLTT_ID(paletteNum) + 10, sizeof(hintColor));\n    }\n'''
if old in text:
    text = text.replace(old, new, 1)
elif 'u16 hintColor;' not in text:
    raise SystemExit('Battle color block not found')
p.write_text(text)

# ---------------- Debug Test Hub ----------------
p = Path('src/debug.c')
text = p.read_text()
if 'sDebugMenu_Actions_TestHub' not in text:
    anchor = 'static const struct DebugMenuOption sDebugMenu_Actions_Main[] =\n{\n'
    submenu = '''static const struct DebugMenuOption sDebugMenu_Actions_TestHub[] =\n{\n    { COMPOUND_STRING("Early Free Roam"),       DebugAction_Util_CheatStart },\n    { COMPOUND_STRING("Fly / Checkpoints…"),    DebugAction_Util_Fly },\n    { COMPOUND_STRING("Set Test Party"),        DebugAction_Party_SetParty },\n    { COMPOUND_STRING("Heal Party"),            DebugAction_Party_HealParty },\n    { COMPOUND_STRING("Fill Bag…"),             DebugAction_OpenSubMenu, sDebugMenu_Actions_PCBag_Fill },\n    { COMPOUND_STRING("Give X…"),               DebugAction_OpenSubMenu, sDebugMenu_Actions_Give },\n    { COMPOUND_STRING("Progress / Flags…"),     DebugAction_OpenSubMenuFlagsVars, sDebugMenu_Actions_Flags },\n    { COMPOUND_STRING("Starter Test"),          DebugAction_Util_StarterTest },\n    { COMPOUND_STRING("Start Debug Battle"),    DebugAction_Party_BattleSingle },\n    { NULL }\n};\n\n'''
    if anchor not in text:
        raise SystemExit('Debug main menu anchor not found')
    text = text.replace(anchor, submenu + anchor, 1)
    text = text.replace(anchor + '    { COMPOUND_STRING("Utilities…"),', anchor + '    { COMPOUND_STRING("TEST HUB…"),      DebugAction_OpenSubMenu, sDebugMenu_Actions_TestHub, },\n    { COMPOUND_STRING("Utilities…"),', 1)
    p.write_text(text)

# ---------------- DexNav: use randomized slot species when deriving encounter level ----------------
p = Path('src/dexnav.c')
text = p.read_text()
if 'DEXNAV_RANDOMIZER_LEVEL_FIX' not in text:
    start = text.find('static u8 GetEncounterLevelFromMapData(enum Species species, enum EncounterType environment)\n{')
    if start < 0:
        raise SystemExit('DexNav level function not found')
    # Find function end with brace counting.
    brace = text.find('{', start)
    depth = 0
    end = None
    for i in range(brace, len(text)):
        if text[i] == '{': depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    body = text[start:end]
    # Replace direct slot-species expressions inside this function with the same seeded species mapping used by the GUI.
    # Preserve original slot levels; only species identity is randomized.
    def repl_land(m):
        expr = m.group(0)
        return '(gSaveBlock3Ptr->randomizerEnabled ? GetDexNavSeededSpecies(WILD_AREA_LAND, i) : ' + expr + ')'
    def repl_water(m):
        expr = m.group(0)
        return '(gSaveBlock3Ptr->randomizerEnabled ? GetDexNavSeededSpecies(WILD_AREA_WATER, i) : ' + expr + ')'
    original = body
    # Variable names differ by expansion version; key off land/water info identifiers on each expression.
    body = re.sub(r'land[A-Za-z0-9_]*->wildPokemon\[i\]\.species', repl_land, body)
    body = re.sub(r'water[A-Za-z0-9_]*->wildPokemon\[i\]\.species', repl_water, body)
    if body == original:
        raise SystemExit('DexNav slot species expressions not found')
    body = body.replace('{\n', '{\n    // DEXNAV_RANDOMIZER_LEVEL_FIX: search uses the same seeded species slots as the GUI.\n', 1)
    text = text[:start] + body + text[end:]
    p.write_text(text)

print('Current cleanup patch applied')
