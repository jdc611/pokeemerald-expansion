from pathlib import Path
import re


def replace_once(path, old, new):
    p = Path(path)
    text = p.read_text()
    if old not in text:
        raise SystemExit(f"Expected block not found in {path}: {old[:120]!r}")
    text = text.replace(old, new, 1)
    p.write_text(text)

# Persistent save var. 0x404E was explicitly unused in Emerald.
replace_once(
    "include/constants/vars.h",
    "#define VAR_UNUSED_0x404E                                0x404E // Unused Var",
    "#define VAR_TYPE_HINTS_MODE                              0x404E // 0=Seen, 1=Always, 2=Caught, 3=Off",
)

# Start menu: add a page-2 Type Hints setting that cycles Seen -> Caught -> Off -> Always.
p = Path("src/start_menu.c")
text = p.read_text()
text = text.replace(
    '#include "constants/songs.h"\n',
    '#include "constants/songs.h"\n#include "constants/type_hints.h"\n',
    1,
)
text = text.replace(
    "    MENU_ACTION_CHANGE_GENDER,\n};",
    "    MENU_ACTION_CHANGE_GENDER,\n    MENU_ACTION_TYPE_HINTS,\n};",
    1,
)
text = text.replace(
    "static bool8 StartMenuChangeGender(void);\n",
    "static bool8 StartMenuChangeGender(void);\nstatic bool8 StartMenuTypeHints(void);\n",
    1,
)
text = text.replace(
    'static const u8 sText_ExitPage2[] = _("EXIT  2/2");\n',
    'static const u8 sText_ExitPage2[] = _("EXIT  2/2");\n'
    'static const u8 sText_TypeHintsSeen[] = _("TYPE HINTS: SEEN");\n'
    'static const u8 sText_TypeHintsAlways[] = _("TYPE HINTS: ALWAYS");\n'
    'static const u8 sText_TypeHintsCaught[] = _("TYPE HINTS: CAUGHT");\n'
    'static const u8 sText_TypeHintsOff[] = _("TYPE HINTS: OFF");\n',
    1,
)
text = text.replace(
    '    [MENU_ACTION_CHANGE_GENDER] = {COMPOUND_STRING("GENDER"), {.u8_void = StartMenuChangeGender}},\n};',
    '    [MENU_ACTION_CHANGE_GENDER] = {COMPOUND_STRING("GENDER"), {.u8_void = StartMenuChangeGender}},\n'
    '    [MENU_ACTION_TYPE_HINTS] = {COMPOUND_STRING("TYPE HINTS"), {.u8_void = StartMenuTypeHints}},\n};',
    1,
)
text = text.replace(
    "    AddStartMenuAction(MENU_ACTION_CHANGE_GENDER);\n    AddStartMenuAction(MENU_ACTION_EXIT);",
    "    AddStartMenuAction(MENU_ACTION_CHANGE_GENDER);\n    AddStartMenuAction(MENU_ACTION_TYPE_HINTS);\n    AddStartMenuAction(MENU_ACTION_EXIT);",
    1,
)
old_print = '''            if (sCurrentStartMenuActions[index] == MENU_ACTION_EXIT)
{
    if (sStartMenuPage == 0)
        StringCopy(gStringVar4, sText_ExitPage1);
    else
        StringCopy(gStringVar4, sText_ExitPage2);
}
else
{
    StringExpandPlaceholders(gStringVar4, sStartMenuItems[sCurrentStartMenuActions[index]].text);
}'''
new_print = '''            if (sCurrentStartMenuActions[index] == MENU_ACTION_EXIT)
{
    if (sStartMenuPage == 0)
        StringCopy(gStringVar4, sText_ExitPage1);
    else
        StringCopy(gStringVar4, sText_ExitPage2);
}
else if (sCurrentStartMenuActions[index] == MENU_ACTION_TYPE_HINTS)
{
    switch (VarGet(VAR_TYPE_HINTS_MODE))
    {
    case TYPE_HINTS_ALWAYS:
        StringCopy(gStringVar4, sText_TypeHintsAlways);
        break;
    case TYPE_HINTS_CAUGHT:
        StringCopy(gStringVar4, sText_TypeHintsCaught);
        break;
    case TYPE_HINTS_OFF:
        StringCopy(gStringVar4, sText_TypeHintsOff);
        break;
    case TYPE_HINTS_SEEN:
    default:
        StringCopy(gStringVar4, sText_TypeHintsSeen);
        break;
    }
}
else
{
    StringExpandPlaceholders(gStringVar4, sStartMenuItems[sCurrentStartMenuActions[index]].text);
}'''
if old_print not in text:
    raise SystemExit("Start menu print block not found")
text = text.replace(old_print, new_print, 1)
text = text.replace(
    "            && gMenuCallback != StartMenuChangeGender)",
    "            && gMenuCallback != StartMenuChangeGender\n            && gMenuCallback != StartMenuTypeHints)",
    1,
)
anchor = '''static bool8 StartMenuChangeGender(void)
{
    if (!gPaletteFade.active)
    {
        RemoveExtraStartMenuWindows();
        HideStartMenu();
        ScriptContext_SetupScript(EventScript_ChangeGender);
        return TRUE;
    }

    return FALSE;
}
'''
callback = anchor + '''
static bool8 StartMenuTypeHints(void)
{
    u16 mode = VarGet(VAR_TYPE_HINTS_MODE);

    switch (mode)
    {
    case TYPE_HINTS_SEEN:
        mode = TYPE_HINTS_CAUGHT;
        break;
    case TYPE_HINTS_CAUGHT:
        mode = TYPE_HINTS_OFF;
        break;
    case TYPE_HINTS_OFF:
        mode = TYPE_HINTS_ALWAYS;
        break;
    case TYPE_HINTS_ALWAYS:
    default:
        mode = TYPE_HINTS_SEEN;
        break;
    }

    VarSet(VAR_TYPE_HINTS_MODE, mode);
    ClearStdWindowAndFrame(GetStartMenuWindowId(), TRUE);
    RemoveStartMenuWindow();
    InitStartMenu();
    gMenuCallback = HandleStartMenuInput;
    return FALSE;
}
'''
if anchor not in text:
    raise SystemExit("StartMenuChangeGender callback block not found")
text = text.replace(anchor, callback, 1)
p.write_text(text)

# Battle UI: use the saved mode and replace the stock symbols with our arrow language.
p = Path("src/battle_controller_player.c")
text = p.read_text()
text = text.replace(
    '#include "event_object_movement.h"\n' if '#include "event_object_movement.h"\n' in text else '#include "data.h"\n',
    ('#include "event_object_movement.h"\n#include "event_data.h"\n' if '#include "event_object_movement.h"\n' in text else '#include "data.h"\n#include "event_data.h"\n'),
    1,
)
text = text.replace(
    '#include "constants/trainers.h"\n',
    '#include "constants/trainers.h"\n#include "constants/type_hints.h"\n#include "constants/vars.h"\n',
    1,
)
old_should = '''static bool32 ShouldShowTypeEffectiveness(u32 targetId)
{
    if (IsGhostBattleWithoutScope())
        return FALSE;

    if (B_SHOW_EFFECTIVENESS == SHOW_EFFECTIVENESS_CAUGHT)
        return GetSetPokedexFlag(SpeciesToNationalPokedexNum(gBattleMons[targetId].species), FLAG_GET_CAUGHT);

    if (B_SHOW_EFFECTIVENESS == SHOW_EFFECTIVENESS_SEEN)
        return GetSetPokedexFlag(SpeciesToNationalPokedexNum(gBattleMons[targetId].species), FLAG_GET_SEEN);

    return TRUE;
}'''
new_should = '''static bool32 ShouldShowTypeEffectiveness(u32 targetId)
{
    u16 mode = VarGet(VAR_TYPE_HINTS_MODE);

    if (IsGhostBattleWithoutScope())
        return FALSE;

    switch (mode)
    {
    case TYPE_HINTS_ALWAYS:
        return TRUE;
    case TYPE_HINTS_CAUGHT:
        return GetSetPokedexFlag(SpeciesToNationalPokedexNum(gBattleMons[targetId].species), FLAG_GET_CAUGHT);
    case TYPE_HINTS_OFF:
        return FALSE;
    case TYPE_HINTS_SEEN:
    default:
        return GetSetPokedexFlag(SpeciesToNationalPokedexNum(gBattleMons[targetId].species), FLAG_GET_SEEN);
    }
}'''
if old_should not in text:
    raise SystemExit("ShouldShowTypeEffectiveness block not found")
text = text.replace(old_should, new_should, 1)
old_icons = '''    static const u8 noIcon[] =  _("");
    static const u8 effectiveIcon[] =  _("{CIRCLE_HOLLOW}");
    static const u8 extremeleyEffectiveIcon[] =  _("{STAR}");
    static const u8 superEffectiveIcon[] =  _("{CIRCLE_DOT}");
    static const u8 notVeryEffectiveIcon[] =  _("{TRIANGLE}");
    static const u8 mostlyIneffectiveIcon[] =  _("{TRIANGLE_UPSIDE_DOWN}");
    static const u8 immuneIcon[] =  _("{BIG_MULT_X}");'''
new_icons = '''    static const u8 noIcon[] =  _("");
    static const u8 effectiveIcon[] =  _("");
    static const u8 extremeleyEffectiveIcon[] =  _("{COLOR GREEN}{UP_ARROW}+");
    static const u8 superEffectiveIcon[] =  _("{COLOR GREEN}{UP_ARROW}");
    static const u8 notVeryEffectiveIcon[] =  _("{COLOR DYNAMIC_COLOR1}{DOWN_ARROW}");
    static const u8 mostlyIneffectiveIcon[] =  _("{COLOR DYNAMIC_COLOR1}{DOWN_ARROW}-");
    static const u8 immuneIcon[] =  _("{COLOR RED}X");'''
if old_icons not in text:
    raise SystemExit("Effectiveness icon block not found")
text = text.replace(old_icons, new_icons, 1)
old_put = '''    BattlePutTextOnWindow(gDisplayedStringBattle, B_WIN_PP);
}'''
new_put = '''    // DYNAMIC_COLOR1 is reserved here as the resistance-hint yellow.
    // The other hint colors use the standard GREEN and RED text slots.
    {
        u16 yellow = RGB_YELLOW;
        u32 paletteNum = GetWindowAttribute(B_WIN_PP, WINDOW_PALETTE_NUM);
        LoadPalette(&yellow, BG_PLTT_ID(paletteNum) + 10, sizeof(yellow));
    }

    BattlePutTextOnWindow(gDisplayedStringBattle, B_WIN_PP);
}'''
# This exact tail occurs in MoveSelectionDisplayMoveEffectiveness; replace the LAST relevant occurrence
idx = text.find(old_put, text.find('static void MoveSelectionDisplayMoveEffectiveness'))
if idx < 0:
    raise SystemExit("Effectiveness BattlePutTextOnWindow tail not found")
text = text[:idx] + new_put + text[idx + len(old_put):]
p.write_text(text)

print("Type Hints patch applied successfully")
