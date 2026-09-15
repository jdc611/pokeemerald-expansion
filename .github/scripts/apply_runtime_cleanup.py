from pathlib import Path


def rep(s, old, new, label):
    if old not in s:
        raise SystemExit(f'Missing anchor: {label}')
    return s.replace(old, new, 1)

# Keep the badge-based cap progression locked in.
p=Path('src/caps.c'); s=p.read_text()
start=s.index('u32 GetCurrentLevelCap(void)')
end=s.index('\nu32 GetSoftLevelCapExpValue', start)
new='''u32 GetCurrentLevelCap(void)\n{\n    static const u32 sLevelCapFlagMap[][2] =\n    {\n        {FLAG_BADGE01_GET, 15},\n        {FLAG_BADGE02_GET, 19},\n        {FLAG_BADGE03_GET, 24},\n        {FLAG_BADGE04_GET, 29},\n        {FLAG_BADGE05_GET, 31},\n        {FLAG_BADGE06_GET, 33},\n        {FLAG_BADGE07_GET, 42},\n        {FLAG_BADGE08_GET, 46},\n        {FLAG_IS_CHAMPION, 58},\n    };\n    u32 i;\n    for (i = 0; i < ARRAY_COUNT(sLevelCapFlagMap); i++)\n        if (!FlagGet(sLevelCapFlagMap[i][0]))\n            return sLevelCapFlagMap[i][1];\n    return 58;\n}\n'''
s=s[:start]+new+s[end:]; p.write_text(s)

p=Path('src/start_menu.c'); s=p.read_text()

# MGM is display-only in Game Info, not a page-2 action.
s=s.replace('        AddStartMenuAction(MENU_ACTION_MGM);\n','',1)
# PokéRider belongs in the R-button quick tools menu.
s=s.replace('        AddStartMenuAction(MENU_ACTION_POKERIDER);\n','',1)
quick='''        AddStartMenuAction(MENU_ACTION_POKEVIAL);\n        AddStartMenuAction(MENU_ACTION_PC_STORAGE);\n'''
if '        AddStartMenuAction(MENU_ACTION_POKERIDER);\n' not in s[s.index('if (sQuickToolsMode)'):s.index('if (sStartMenuPage == 0)')]:
    s=rep(s, quick, quick + '        AddStartMenuAction(MENU_ACTION_POKERIDER);\n', 'quick tools PokéRider')

# Train-to-Cap gets its own lightweight selector: each party member, Entire Party, Back.
# This avoids silently training the whole party and keeps the action fast in the field.
if 'static bool8 HandleTrainToCapInput(void);' not in s:
    s=rep(s, 'static bool8 HandleGameInfoInput(void);\n', 'static bool8 HandleGameInfoInput(void);\nstatic bool8 HandleTrainToCapInput(void);\n', 'train handler declaration')

start=s.index('static bool8 StartMenuTrainToCap(void)\n{')
end=s.index('\nstatic bool8 StartMenuMGM(void)', start)
replacement=r'''static void TrainMonToCurrentCap(struct Pokemon *mon)
{
    enum Species species = GetMonData(mon, MON_DATA_SPECIES);
    u8 level = GetMonData(mon, MON_DATA_LEVEL);
    u8 cap = GetCurrentLevelCap();
    u32 exp;

    if (species == SPECIES_NONE || GetMonData(mon, MON_DATA_IS_EGG) || level >= cap)
        return;

    exp = gExperienceTables[gSpeciesInfo[species].growthRate][cap];
    SetMonData(mon, MON_DATA_EXP, &exp);
    SetMonData(mon, MON_DATA_LEVEL, &cap);
    CalculateMonStats(mon);
    if (IsMinimalGrindingMode())
        ApplyMinimalGrindingModeToMon(mon);
}

static bool8 StartMenuTrainToCap(void)
{
    u8 i;
    u8 windowId;

    ClearStdWindowAndFrame(GetStartMenuWindowId(), TRUE);
    RemoveStartMenuWindow();
    windowId = AddGameOptionsWindow(gPlayerPartyCount + 2);
    DrawStdWindowFrame(windowId, FALSE);
    FillWindowPixelBuffer(windowId, PIXEL_FILL(1));

    for (i = 0; i < gPlayerPartyCount; i++)
    {
        GetMonNickname(&gPlayerParty[i], gStringVar4);
        AddTextPrinterParameterized(windowId, FONT_NORMAL, gStringVar4, 8, (i << 4) + 9, TEXT_SKIP_DRAW, NULL);
    }
    AddTextPrinterParameterized(windowId, FONT_NORMAL, COMPOUND_STRING("ENTIRE PARTY"), 8, (gPlayerPartyCount << 4) + 9, TEXT_SKIP_DRAW, NULL);
    AddTextPrinterParameterized(windowId, FONT_NORMAL, COMPOUND_STRING("BACK"), 8, ((gPlayerPartyCount + 1) << 4) + 9, TEXT_SKIP_DRAW, NULL);
    InitMenuNormal(windowId, FONT_NORMAL, 0, 9, 16, gPlayerPartyCount + 2, 0);
    PutWindowTilemap(windowId);
    CopyWindowToVram(windowId, COPYWIN_FULL);
    gMenuCallback = HandleTrainToCapInput;
    return FALSE;
}

static bool8 HandleTrainToCapInput(void)
{
    s8 input;
    u8 i;

    if (JOY_NEW(DPAD_UP))
    {
        PlaySE(SE_SELECT);
        Menu_MoveCursor(-1);
        return FALSE;
    }
    if (JOY_NEW(DPAD_DOWN))
    {
        PlaySE(SE_SELECT);
        Menu_MoveCursor(1);
        return FALSE;
    }
    if (JOY_NEW(B_BUTTON))
        input = gPlayerPartyCount + 1;
    else if (JOY_NEW(A_BUTTON))
        input = Menu_GetCursorPos();
    else
        return FALSE;

    PlaySE(SE_SELECT);
    if (input < gPlayerPartyCount)
    {
        TrainMonToCurrentCap(&gPlayerParty[input]);
        PlaySE(SE_EXP_MAX);
    }
    else if (input == gPlayerPartyCount)
    {
        for (i = 0; i < gPlayerPartyCount; i++)
            TrainMonToCurrentCap(&gPlayerParty[i]);
        PlaySE(SE_EXP_MAX);
    }

    ClearStdWindowAndFrame(GetStartMenuWindowId(), TRUE);
    RemoveStartMenuWindow();
    sStartMenuCursorPos = 0;
    InitStartMenu();
    gMenuCallback = HandleStartMenuInput;
    return FALSE;
}
'''
s=s[:start]+replacement+s[end:]
p.write_text(s)

print('runtime cleanup applied')
