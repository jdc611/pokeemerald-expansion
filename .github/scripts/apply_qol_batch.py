from pathlib import Path


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f"Missing patch anchor: {label}")
    return text.replace(old, new, 1)


def replace_function_body(text, func_name, transform, label):
    start = text.find(func_name)
    if start < 0:
        raise SystemExit(f"Missing function: {label}")
    brace = text.find('{', start)
    if brace < 0:
        raise SystemExit(f"Missing opening brace: {label}")
    depth = 0
    end = None
    for i in range(brace, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        raise SystemExit(f"Missing closing brace: {label}")
    old = text[start:end]
    new = transform(old)
    return text[:start] + new + text[end:]


# Persistent Minimal Grinding Mode toggle.
p = Path('include/global.h')
s = p.read_text()
s = replace_once(
    s,
    '    u8 futureEvolutionEligible;\n}; /* max size 1624 bytes */',
    '    u8 futureEvolutionEligible;\n    u8 minimalGrindingMode;\n}; /* max size 1624 bytes */',
    'SaveBlock3 MGM flag')
p.write_text(s)


# Cap/MGM helpers. 31 IVs everywhere plus a legal 510-EV balanced spread
# removes IV/EV grinding while avoiding an illegal six-stat 252 EV spread.
p = Path('include/caps.h')
s = p.read_text()
s = replace_once(
    s,
    'u32 GetCurrentEVCap(void);\n',
    'u32 GetCurrentEVCap(void);\nbool32 IsMinimalGrindingMode(void);\nvoid ApplyMinimalGrindingModeToMon(struct Pokemon *mon);\nvoid ApplyMinimalGrindingModeToParty(void);\n',
    'caps declarations')
p.write_text(s)

p = Path('src/caps.c')
s = p.read_text()
s = replace_once(
    s,
    '#include "pokemon.h"\n',
    '#include "pokemon.h"\n#include "constants/pokemon.h"\n',
    'caps pokemon constants include')
s += r'''

bool32 IsMinimalGrindingMode(void)
{
    return gSaveBlock3Ptr != NULL && gSaveBlock3Ptr->minimalGrindingMode;
}

void ApplyMinimalGrindingModeToMon(struct Pokemon *mon)
{
    u8 perfectIv = MAX_PER_STAT_IVS;
    u8 neutralEv = 85; // 85 * 6 = 510, the legal total EV maximum.

    if (mon == NULL || GetMonData(mon, MON_DATA_SPECIES) == SPECIES_NONE || GetMonData(mon, MON_DATA_IS_EGG))
        return;

    SetMonData(mon, MON_DATA_HP_IV, &perfectIv);
    SetMonData(mon, MON_DATA_ATK_IV, &perfectIv);
    SetMonData(mon, MON_DATA_DEF_IV, &perfectIv);
    SetMonData(mon, MON_DATA_SPEED_IV, &perfectIv);
    SetMonData(mon, MON_DATA_SPATK_IV, &perfectIv);
    SetMonData(mon, MON_DATA_SPDEF_IV, &perfectIv);

    SetMonData(mon, MON_DATA_HP_EV, &neutralEv);
    SetMonData(mon, MON_DATA_ATK_EV, &neutralEv);
    SetMonData(mon, MON_DATA_DEF_EV, &neutralEv);
    SetMonData(mon, MON_DATA_SPEED_EV, &neutralEv);
    SetMonData(mon, MON_DATA_SPATK_EV, &neutralEv);
    SetMonData(mon, MON_DATA_SPDEF_EV, &neutralEv);
    CalculateMonStats(mon);
}

void ApplyMinimalGrindingModeToParty(void)
{
    u32 i;

    if (!IsMinimalGrindingMode())
        return;

    for (i = 0; i < gPlayerPartyCount; i++)
        ApplyMinimalGrindingModeToMon(&gPlayerParty[i]);
}
'''
p.write_text(s)


# Infinite Rare Candy. The existing callback already checks normal evolution at
# the level cap; only suppress consumption so one candy can be reused forever.
p = Path('src/party_menu.c')
s = p.read_text()

def make_rare_candy_infinite(func):
    func = func.replace('RemoveBagItem(gSpecialVar_ItemId, 1);', '/* Infinite Rare Candy: intentionally not consumed. */')
    return func

s = replace_function_body(s, 'void ItemUseCB_RareCandy(u8 taskId, TaskFunc task)', make_rare_candy_infinite, 'Rare Candy callback')
p.write_text(s)


# Start menu QoL: PokéRider, one-tap party cap training, MGM toggle, Game Info.
p = Path('src/start_menu.c')
s = p.read_text()
s = replace_once(
    s,
    '#include "run_settings.h"\n',
    '#include "run_settings.h"\n#include "caps.h"\n#include "region_map.h"\n#include "pokemon.h"\n#include "data.h"\n',
    'start menu QoL includes')

s = replace_once(
    s,
    '    MENU_ACTION_GAME_INFO,\n    MENU_ACTION_DEXNAV_INFO,',
    '    MENU_ACTION_GAME_INFO,\n    MENU_ACTION_POKERIDER,\n    MENU_ACTION_TRAIN_TO_CAP,\n    MENU_ACTION_MGM,\n    MENU_ACTION_DEXNAV_INFO,',
    'menu action enum')

s = replace_once(
    s,
    'static bool8 StartMenuGameInfo(void);\nstatic bool8 StartMenuDexNavInfo(void);',
    'static bool8 StartMenuGameInfo(void);\nstatic bool8 StartMenuPokeRider(void);\nstatic bool8 StartMenuTrainToCap(void);\nstatic bool8 StartMenuMGM(void);\nstatic bool8 StartMenuDexNavInfo(void);',
    'menu action prototypes')

s = replace_once(
    s,
    'static const u8 sText_GameInfoUnknown[] = _("UNKNOWN");\n',
    'static const u8 sText_GameInfoUnknown[] = _("UNKNOWN");\nstatic const u8 sText_GameInfoCap[] = _("LEVEL CAP: {STR_VAR_1}");\nstatic const u8 sText_GameInfoMgmOn[] = _("MGM: ON");\nstatic const u8 sText_GameInfoMgmOff[] = _("MGM: OFF");\nstatic const u8 sText_MgmOn[] = _("MGM: ON");\nstatic const u8 sText_MgmOff[] = _("MGM: OFF");\n',
    'QoL menu strings')

s = replace_once(
    s,
    '    [MENU_ACTION_GAME_INFO] = {COMPOUND_STRING("GAME INFO"), {.u8_void = StartMenuGameInfo}},\n    [MENU_ACTION_DEXNAV_INFO]',
    '    [MENU_ACTION_GAME_INFO] = {COMPOUND_STRING("GAME INFO"), {.u8_void = StartMenuGameInfo}},\n    [MENU_ACTION_POKERIDER] = {COMPOUND_STRING("POKéRIDER"), {.u8_void = StartMenuPokeRider}},\n    [MENU_ACTION_TRAIN_TO_CAP] = {COMPOUND_STRING("TRAIN TO CAP"), {.u8_void = StartMenuTrainToCap}},\n    [MENU_ACTION_MGM] = {COMPOUND_STRING("MGM"), {.u8_void = StartMenuMGM}},\n    [MENU_ACTION_DEXNAV_INFO]',
    'QoL menu actions')

s = replace_once(
    s,
    '        AddStartMenuAction(MENU_ACTION_MOVE_RELEARNER);\n        AddStartMenuAction(MENU_ACTION_GAME_OPTIONS);\n        AddStartMenuAction(MENU_ACTION_GAME_INFO);\n        // Reserved for level caps and future rules tools.\n        AddStartMenuAction(MENU_ACTION_EXIT);',
    '        AddStartMenuAction(MENU_ACTION_POKERIDER);\n        AddStartMenuAction(MENU_ACTION_TRAIN_TO_CAP);\n        AddStartMenuAction(MENU_ACTION_MOVE_RELEARNER);\n        AddStartMenuAction(MENU_ACTION_GAME_OPTIONS);\n        AddStartMenuAction(MENU_ACTION_MGM);\n        AddStartMenuAction(MENU_ACTION_GAME_INFO);\n        AddStartMenuAction(MENU_ACTION_EXIT);',
    'page 2 QoL actions')

# MGM label is live ON/OFF text, inserted immediately before the existing
# DexNav dynamic label so this survives the current menu formatting.
s = replace_once(
    s,
    '            else if (sCurrentStartMenuActions[index] == MENU_ACTION_DEXNAV_INFO)\n',
    '            else if (sCurrentStartMenuActions[index] == MENU_ACTION_MGM)\n            {\n                StringCopy(gStringVar4, IsMinimalGrindingMode() ? sText_MgmOn : sText_MgmOff);\n            }\n            else if (sCurrentStartMenuActions[index] == MENU_ACTION_DEXNAV_INFO)\n',
    'dynamic MGM text')

# Expand Game Info with current cap and MGM state.
s = replace_once(s, '    windowId = AddGameOptionsWindow(7);\n', '    windowId = AddGameOptionsWindow(9);\n', 'Game Info window height')
s = replace_once(
    s,
    '    ConvertIntToDecimalStringN(gStringVar1, gSaveBlock3Ptr->worldSeed, STR_CONV_MODE_LEFT_ALIGN, 8);\n    StringExpandPlaceholders(gStringVar4, sText_GameInfoValue);\n    PrintGameInfoLine(gStringVar4, 89);\n    PrintGameInfoLine(sText_GameInfoBack, 105);',
    '    ConvertIntToDecimalStringN(gStringVar1, gSaveBlock3Ptr->worldSeed, STR_CONV_MODE_LEFT_ALIGN, 8);\n    StringExpandPlaceholders(gStringVar4, sText_GameInfoValue);\n    PrintGameInfoLine(gStringVar4, 89);\n\n    ConvertIntToDecimalStringN(gStringVar1, GetCurrentLevelCap(), STR_CONV_MODE_LEFT_ALIGN, 3);\n    StringExpandPlaceholders(gStringVar4, sText_GameInfoCap);\n    PrintGameInfoLine(gStringVar4, 105);\n    PrintGameInfoLine(IsMinimalGrindingMode() ? sText_GameInfoMgmOn : sText_GameInfoMgmOff, 121);\n    PrintGameInfoLine(sText_GameInfoBack, 137);',
    'Game Info cap/MGM')

insert_before = 'static bool8 StartMenuBackGameOptions(void)\n'
if insert_before not in s:
    raise SystemExit('Missing patch anchor: QoL callbacks insertion')
qol_callbacks = r'''static bool8 StartMenuPokeRider(void)
{
    if (!gPaletteFade.active)
    {
        RemoveExtraStartMenuWindows();
        HideStartMenu();
        gMain.savedCallback = CB2_ReturnToField;
        SetMainCallback2(CB2_OpenFlyMap);
        return TRUE;
    }
    return FALSE;
}

static bool8 StartMenuTrainToCap(void)
{
    u32 i;
    u8 cap = GetCurrentLevelCap();

    for (i = 0; i < gPlayerPartyCount; i++)
    {
        struct Pokemon *mon = &gPlayerParty[i];
        enum Species species = GetMonData(mon, MON_DATA_SPECIES);
        u8 level = GetMonData(mon, MON_DATA_LEVEL);
        u32 exp;

        if (species == SPECIES_NONE || GetMonData(mon, MON_DATA_IS_EGG) || level >= cap)
            continue;

        exp = gExperienceTables[gSpeciesInfo[species].growthRate][cap];
        SetMonData(mon, MON_DATA_EXP, &exp);
        SetMonData(mon, MON_DATA_LEVEL, &cap);
        CalculateMonStats(mon);
        if (IsMinimalGrindingMode())
            ApplyMinimalGrindingModeToMon(mon);
    }

    PlaySE(SE_EXP_MAX);
    ClearStdWindowAndFrame(GetStartMenuWindowId(), TRUE);
    RemoveStartMenuWindow();
    InitStartMenu();
    gMenuCallback = HandleStartMenuInput;
    return FALSE;
}

static bool8 StartMenuMGM(void)
{
    gSaveBlock3Ptr->minimalGrindingMode ^= 1;
    if (IsMinimalGrindingMode())
        ApplyMinimalGrindingModeToParty();

    ClearStdWindowAndFrame(GetStartMenuWindowId(), TRUE);
    RemoveStartMenuWindow();
    InitStartMenu();
    gMenuCallback = HandleStartMenuInput;
    return FALSE;
}

'''
s = s.replace(insert_before, qol_callbacks + insert_before, 1)
p.write_text(s)


# PokéRider cancellation should return to field rather than a nonexistent Party
# menu. Using savedCallback keeps the patch small and localized for this build.
p = Path('src/region_map.c')
s = p.read_text()
s = replace_once(
    s,
    '                SetMainCallback2(CB2_ReturnToPartyMenuFromFlyMap);\n',
    '                if (gMain.savedCallback == CB2_ReturnToField)\n                    SetMainCallback2(CB2_ReturnToField);\n                else\n                    SetMainCallback2(CB2_ReturnToPartyMenuFromFlyMap);\n',
    'PokéRider Fly cancel return')
p.write_text(s)


print('QoL batch patch applied successfully.')
