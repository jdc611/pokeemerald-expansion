from pathlib import Path


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f"Missing patch anchor: {label}")
    return text.replace(old, new, 1)

# --- Shiny custom starter: create it shiny from the start instead of mutating personality after creation. ---
p = Path('src/battle_setup.c')
s = p.read_text()
old = '''    ScriptGiveMon(starterMon, 5, ITEM_NONE);\n    if (gSaveBlock3Ptr->starterMode == RUN_STARTER_CHOOSE && gCustomStarterShiny)\n    {\n        struct Pokemon *starter = &gParties[B_TRAINER_PLAYER][0];\n        u32 otId = GetMonData(starter, MON_DATA_OT_ID);\n        u32 personality = GetMonData(starter, MON_DATA_PERSONALITY);\n        u16 shinyLow = (u16)otId ^ (u16)(otId >> 16) ^ (u16)(personality >> 16);\n        personality = (personality & 0xFFFF0000) | shinyLow;\n        UpdateMonPersonality(&starter->box, personality);\n        CalculateMonStats(starter);\n    }\n'''
new = '''    if (gSaveBlock3Ptr->starterMode == RUN_STARTER_CHOOSE && gCustomStarterShiny)\n    {\n        struct PokemonTemplate starterTemplate = {0};\n        u32 i;\n\n        starterTemplate.species = starterMon;\n        starterTemplate.level = 5;\n        starterTemplate.heldItem = ITEM_NONE;\n        starterTemplate.nature = NATURE_RANDOM;\n        starterTemplate.gender = MON_GENDER_RANDOM;\n        starterTemplate.isShiny = TRUE;\n        starterTemplate.doNotUseDefaultShinyness = TRUE;\n        starterTemplate.origin = GIFTMON_ORIGIN;\n        for (i = 0; i < NUM_STATS; i++)\n            starterTemplate.ivs[i] = USE_RANDOM_IVS;\n        for (i = 0; i < MAX_MON_MOVES; i++)\n            starterTemplate.moves[i] = MOVE_DEFAULT;\n        ScriptGiveMonParameterized(B_SIDE_PLAYER, PARTY_SIZE, &starterTemplate);\n    }\n    else\n    {\n        ScriptGiveMon(starterMon, 5, ITEM_NONE);\n    }\n'''
s = replace_once(s, old, new, 'starter shiny creation')
p.write_text(s)

# --- Native party-screen Train to Cap. ---
p = Path('include/party_menu.h')
s = p.read_text()
s = replace_once(s,
    'void ChoosePartyMon(void);\n',
    'void ChoosePartyMon(void);\nvoid ChooseMonForTrainToCap(void);\n',
    'party menu declaration')
p.write_text(s)

p = Path('src/party_menu.c')
s = p.read_text()
anchor = '''void ChooseMonForMoveRelearner(void)\n{\n'''
impl = r'''static EWRAM_DATA bool8 sTrainEntireParty = FALSE;

static void TrainPartyMonToCurrentCap(struct Pokemon *mon)
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

static void CB2_TrainMonToCapReturn(void)
{
    u8 slot = GetCursorSelectionMonId();

    if (!sTrainEntireParty && slot < PARTY_SIZE)
        TrainPartyMonToCurrentCap(&gParties[B_TRAINER_PLAYER][slot]);

    PlaySE(SE_EXP_MAX);
    gFieldCallback2 = CB2_FadeFromPartyMenu;
    SetMainCallback2(CB2_ReturnToField);
}

static void Task_HandleTrainToCapInput(u8 taskId)
{
    if (JOY_NEW(START_BUTTON))
    {
        u8 i;
        sTrainEntireParty = TRUE;
        for (i = 0; i < gPartiesCount[B_TRAINER_PLAYER]; i++)
            TrainPartyMonToCurrentCap(&gParties[B_TRAINER_PLAYER][i]);
        PlaySE(SE_SELECT);
        Task_ClosePartyMenu(taskId);
        return;
    }

    Task_HandleChooseMonInput(taskId);
}

static void Task_ChooseMonForTrainToCap(u8 taskId)
{
    if (!gPaletteFade.active)
    {
        CleanupOverworldWindowsAndTilemaps();
        sTrainEntireParty = FALSE;
        InitPartyMenu(PARTY_MENU_TYPE_CHOOSE_MON, PARTY_LAYOUT_SINGLE, PARTY_ACTION_CHOOSE_AND_CLOSE, FALSE, PARTY_MSG_CHOOSE_MON, Task_HandleTrainToCapInput, CB2_TrainMonToCapReturn);
        DestroyTask(taskId);
    }
}

void ChooseMonForTrainToCap(void)
{
    LockPlayerFieldControls();
    FadeScreen(FADE_TO_BLACK, 0);
    CreateTask(Task_ChooseMonForTrainToCap, 10);
}

'''
s = replace_once(s, anchor, impl + anchor, 'train-to-cap native party implementation')
p.write_text(s)

p = Path('src/start_menu.c')
s = p.read_text()
s = s.replace('static bool8 HandleTrainToCapInput(void);\n', '', 1)
start = s.find('static void TrainMonToCurrentCap(struct Pokemon *mon)\n')
end = s.find('static bool8 StartMenuMGM(void)\n', start)
if start < 0 or end < 0:
    raise SystemExit('Missing old Train to Cap block')
replacement = '''static bool8 StartMenuTrainToCap(void)\n{\n    if (!gPaletteFade.active)\n    {\n        RemoveExtraStartMenuWindows();\n        HideStartMenu();\n        ChooseMonForTrainToCap();\n        return TRUE;\n    }\n    return FALSE;\n}\n\n'''
s = s[:start] + replacement + s[end:]
p.write_text(s)

print('Applied shiny starter + native Train to Cap party screen fix')
