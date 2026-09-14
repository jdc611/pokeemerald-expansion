from pathlib import Path


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f"Missing patch anchor: {label}")
    return text.replace(old, new, 1)

# --- Run setup: NORMAL / RANDOM / CUSTOM starter mode ---
p = Path('src/main_menu.c')
s = p.read_text()
s = replace_once(s,
    'static EWRAM_DATA bool8 sRunSetupStarter;\n',
    'static EWRAM_DATA u8 sRunSetupStarter;\n',
    'starter mode storage')
s = replace_once(s,
    '        sRunSetupStarter = FALSE;\n',
    '        sRunSetupStarter = RUN_STARTER_NORMAL;\n',
    'starter init')
s = replace_once(s,
    '    const u8 *starters = sRunSetupStarter ? sText_RunSetupRandom : sText_RunSetupNormal;\n',
    '    const u8 *starters = sRunSetupStarter == RUN_STARTER_RANDOM ? sText_RunSetupRandom\n                         : sRunSetupStarter == RUN_STARTER_CHOOSE ? sText_RunSetupCustom\n                         : sText_RunSetupNormal;\n',
    'starter summary label')
s = replace_once(s,
    '        RunSetup_DrawChoice(sText_RunSetupNormal, 98, 56, !sRunSetupStarter);\n        RunSetup_DrawChoice(sText_RunSetupRandom, 151, 56, sRunSetupStarter);\n',
    '        RunSetup_DrawNarrowChoice(sText_RunSetupNormal, 82, 56, sRunSetupStarter == RUN_STARTER_NORMAL);\n        RunSetup_DrawNarrowChoice(sText_RunSetupRandom, 128, 56, sRunSetupStarter == RUN_STARTER_RANDOM);\n        RunSetup_DrawNarrowChoice(sText_RunSetupCustom, 174, 56, sRunSetupStarter == RUN_STARTER_CHOOSE);\n',
    'starter choices draw')
s = replace_once(s,
    '            gRunSetupStarterMode = sRunSetupStarter ? RUN_STARTER_RANDOM : RUN_STARTER_NORMAL;\n',
    '            gRunSetupStarterMode = sRunSetupStarter;\n',
    'starter confirm')
s = replace_once(s,
    '        else if (*cursor == 1)\n            sRunSetupStarter = FALSE;\n',
    '        else if (*cursor == 1)\n        {\n            if (sRunSetupStarter == RUN_STARTER_CHOOSE)\n                sRunSetupStarter = RUN_STARTER_RANDOM;\n            else if (sRunSetupStarter == RUN_STARTER_RANDOM)\n                sRunSetupStarter = RUN_STARTER_NORMAL;\n        }\n',
    'starter left')
s = replace_once(s,
    '        else if (*cursor == 1)\n            sRunSetupStarter = TRUE;\n',
    '        else if (*cursor == 1)\n        {\n            if (sRunSetupStarter == RUN_STARTER_NORMAL)\n                sRunSetupStarter = RUN_STARTER_RANDOM;\n            else if (sRunSetupStarter == RUN_STARTER_RANDOM)\n                sRunSetupStarter = RUN_STARTER_CHOOSE;\n        }\n',
    'starter right')
s = replace_once(s,
    '        else if (*cursor == 1)\n            sRunSetupStarter ^= 1;\n',
    '        else if (*cursor == 1)\n            sRunSetupStarter = sRunSetupStarter == RUN_STARTER_NORMAL ? RUN_STARTER_RANDOM\n                             : sRunSetupStarter == RUN_STARTER_RANDOM ? RUN_STARTER_CHOOSE\n                             : RUN_STARTER_NORMAL;\n',
    'starter A cycle')
p.write_text(s)

# --- Starter selector ---
p = Path('src/starter_choose.c')
s = p.read_text()

s = replace_once(s,
    '#define STARTER_MON_COUNT   3\n',
    '#define STARTER_MON_COUNT   3\n#define CUSTOM_STARTER_ROWS  8\n#define CUSTOM_STARTER_TABS  6\n\n',
    'custom constants')

s = replace_once(s,
    'static void SpriteCB_StarterPokemon(struct Sprite *sprite);\n',
    '''static void SpriteCB_StarterPokemon(struct Sprite *sprite);\nstatic void BeginCustomStarterSelection(void);\nstatic void Task_CustomStarterInput(u8 taskId);\nstatic void BuildCustomStarterList(void);\nstatic bool32 IsCustomStarterEligible(enum Species species);\nstatic u8 GetCustomStarterTab(enum Species species);\nstatic void CustomStarterJumpToTab(u8 taskId, u8 tab);\nstatic void CustomStarterDraw(u8 taskId);\nstatic void CustomStarterUpdatePreview(u8 taskId);\nstatic void CustomStarterDestroyPreview(void);\n''',
    'custom prototypes')

s = replace_once(s,
    'static u16 sStarterLabelWindowId;\n',
    '''static u16 sStarterLabelWindowId;\nEWRAM_DATA u16 gCustomStarterSpecies = SPECIES_NONE;\nEWRAM_DATA bool8 gCustomStarterShiny = FALSE;\nstatic EWRAM_DATA u16 sCustomStarterList[NUM_SPECIES];\nstatic EWRAM_DATA u16 sCustomStarterCount;\nstatic EWRAM_DATA u8 sCustomPreviewSpriteId = SPRITE_NONE;\n''',
    'custom ewram')

s = replace_once(s,
    'static const struct WindowTemplate sWindowTemplate_ConfirmStarter =\n',
    '''static const struct WindowTemplate sCustomWindowTemplates[] =\n{\n    {\n        .bg = 0,\n        .tilemapLeft = 1,\n        .tilemapTop = 1,\n        .width = 28,\n        .height = 16,\n        .paletteNum = 14,\n        .baseBlock = 0x0200\n    },\n    DUMMY_WIN_TEMPLATE,\n};\n\nstatic const struct WindowTemplate sWindowTemplate_ConfirmStarter =\n''',
    'custom window')

s = replace_once(s,
    'static const u8 sTextColors[] = {TEXT_COLOR_TRANSPARENT, TEXT_COLOR_WHITE, TEXT_COLOR_LIGHT_GRAY};\n',
    '''static const u8 sTextColors[] = {TEXT_COLOR_TRANSPARENT, TEXT_COLOR_WHITE, TEXT_COLOR_LIGHT_GRAY};\nstatic const u8 sCustomTabs[CUSTOM_STARTER_TABS][5] =\n{\n    _("A-D"), _("E-H"), _("I-L"), _("M-P"), _("Q-T"), _("U-Z"),\n};\nstatic const u8 sText_CustomStarterTitle[] = _("CHOOSE YOUR STARTER");\nstatic const u8 sText_CustomAppearance[] = _("CHOOSE APPEARANCE");\nstatic const u8 sText_CustomNormal[] = _("NORMAL");\nstatic const u8 sText_CustomShiny[] = _("SHINY");\nstatic const u8 sText_CustomConfirm[] = _("USE THIS STARTER?");\nstatic const u8 sText_CustomYes[] = _("YES");\nstatic const u8 sText_CustomNo[] = _("NO");\nstatic const u8 sText_CustomControls[] = _("L/R TABS   A SELECT");\nstatic const u8 sText_CustomBack[] = _("A CONFIRM   B BACK");\nstatic const u8 sLetterE[] = _("E");\nstatic const u8 sLetterI[] = _("I");\nstatic const u8 sLetterM[] = _("M");\nstatic const u8 sLetterQ[] = _("Q");\nstatic const u8 sLetterU[] = _("U");\n''',
    'custom strings')

s = replace_once(s,
    'u16 GetStarterPokemon(u16 chosenStarterId)\n{\n    if (chosenStarterId > STARTER_MON_COUNT)\n        chosenStarterId = 0;\n    return sStarterMon[chosenStarterId];\n}\n',
    '''u16 GetStarterPokemon(u16 chosenStarterId)\n{\n    if (gSaveBlock3Ptr->starterMode == RUN_STARTER_CHOOSE && gCustomStarterSpecies != SPECIES_NONE)\n        return gCustomStarterSpecies;\n    if (chosenStarterId >= STARTER_MON_COUNT)\n        chosenStarterId = 0;\n    return sStarterMon[chosenStarterId];\n}\n''',
    'get custom starter')

s = replace_once(s,
    '    InitWindows(sWindowTemplates);\n',
    '    InitWindows(gSaveBlock3Ptr->starterMode == RUN_STARTER_CHOOSE ? sCustomWindowTemplates : sWindowTemplates);\n',
    'custom windows init')

s = replace_once(s,
    '    ShowBg(0);\n    ShowBg(2);\n    ShowBg(3);\n\n    taskId = CreateTask(Task_StarterChoose, 0);\n',
    '''    ShowBg(0);\n    ShowBg(2);\n    ShowBg(3);\n\n    if (gSaveBlock3Ptr->starterMode == RUN_STARTER_CHOOSE)\n    {\n        BeginCustomStarterSelection();\n        return;\n    }\n\n    taskId = CreateTask(Task_StarterChoose, 0);\n''',
    'custom branch')

insert_anchor = 'static u8 CreatePokemonFrontSprite(enum Species species, u8 x, u8 y)\n'
custom_code = r'''// Custom starter task data
#define tCustomIndex         data[0]
#define tCustomTab           data[1]
#define tCustomState         data[2]
#define tCustomShiny         data[3]
#define tCustomConfirmChoice data[4]

static bool32 IsCustomStarterEligible(enum Species species)
{
    if (species <= SPECIES_NONE || species >= NUM_SPECIES || species == SPECIES_EGG)
        return FALSE;
    if (!IsSpeciesEnabled(species))
        return FALSE;
    if (gSpeciesInfo[species].isMegaEvolution)
        return FALSE;

    // Legendary-class species are intentionally available even when they are
    // technically a later stage (for example Solgaleo/Lunala or Urshifu).
    if (gSpeciesInfo[species].isLegendary
     || gSpeciesInfo[species].isMythical
     || gSpeciesInfo[species].isUltraBeast
     || gSpeciesInfo[species].isParadox)
        return TRUE;

    // Ordinary custom starters must begin at the start of their evolution line.
    return GetSpeciesPreEvolution(species) == SPECIES_NONE;
}

static void BuildCustomStarterList(void)
{
    enum Species species;
    u16 i;

    sCustomStarterCount = 0;
    for (species = SPECIES_BULBASAUR; species < NUM_SPECIES; species++)
    {
        if (IsCustomStarterEligible(species))
            sCustomStarterList[sCustomStarterCount++] = species;
    }

    // Insertion sort keeps this one-time startup pass small and deterministic.
    for (i = 1; i < sCustomStarterCount; i++)
    {
        u16 key = sCustomStarterList[i];
        s16 j = i - 1;
        while (j >= 0 && StringCompare(GetSpeciesName(sCustomStarterList[j]), GetSpeciesName(key)) > 0)
        {
            sCustomStarterList[j + 1] = sCustomStarterList[j];
            j--;
        }
        sCustomStarterList[j + 1] = key;
    }
}

static u8 GetCustomStarterTab(enum Species species)
{
    u8 first = GetSpeciesName(species)[0];
    if (first < sLetterE[0]) return 0;
    if (first < sLetterI[0]) return 1;
    if (first < sLetterM[0]) return 2;
    if (first < sLetterQ[0]) return 3;
    if (first < sLetterU[0]) return 4;
    return 5;
}

static void CustomStarterDestroyPreview(void)
{
    if (sCustomPreviewSpriteId != SPRITE_NONE)
    {
        FreeAndDestroyMonPicSprite(sCustomPreviewSpriteId);
        sCustomPreviewSpriteId = SPRITE_NONE;
    }
}

static void CustomStarterUpdatePreview(u8 taskId)
{
    enum Species species;
    bool8 shiny;

    CustomStarterDestroyPreview();
    if (sCustomStarterCount == 0)
        return;

    species = sCustomStarterList[gTasks[taskId].tCustomIndex];
    shiny = gTasks[taskId].tCustomState == 0 ? FALSE : gTasks[taskId].tCustomShiny;
    sCustomPreviewSpriteId = CreateMonPicSprite_Affine(species, shiny, 0, MON_PIC_AFFINE_FRONT, 188, 72, 14, TAG_NONE);
    if (sCustomPreviewSpriteId != SPRITE_NONE)
        gSprites[sCustomPreviewSpriteId].oam.priority = 0;
}

static void CustomStarterDraw(u8 taskId)
{
    u16 i, start;
    u8 tab;
    enum Species species;

    FillWindowPixelBuffer(0, PIXEL_FILL(1));

    if (sCustomStarterCount == 0)
    {
        AddTextPrinterParameterized(0, FONT_NORMAL, _("NO ELIGIBLE POKéMON"), 8, 8, TEXT_SKIP_DRAW, NULL);
        CopyWindowToVram(0, COPYWIN_FULL);
        return;
    }

    species = sCustomStarterList[gTasks[taskId].tCustomIndex];

    if (gTasks[taskId].tCustomState == 0)
    {
        AddTextPrinterParameterized(0, FONT_SMALL, sText_CustomStarterTitle, 4, 1, TEXT_SKIP_DRAW, NULL);
        for (tab = 0; tab < CUSTOM_STARTER_TABS; tab++)
        {
            u8 x = 4 + tab * 35;
            if (tab == gTasks[taskId].tCustomTab)
                AddTextPrinterParameterized(0, FONT_SMALL, gText_SelectorArrow2, x, 13, TEXT_SKIP_DRAW, NULL);
            AddTextPrinterParameterized(0, FONT_SMALL, sCustomTabs[tab], x + 8, 13, TEXT_SKIP_DRAW, NULL);
        }

        start = (gTasks[taskId].tCustomIndex / CUSTOM_STARTER_ROWS) * CUSTOM_STARTER_ROWS;
        for (i = 0; i < CUSTOM_STARTER_ROWS && start + i < sCustomStarterCount; i++)
        {
            u8 y = 29 + i * 12;
            if (start + i == gTasks[taskId].tCustomIndex)
                AddTextPrinterParameterized(0, FONT_SMALL, gText_SelectorArrow2, 4, y, TEXT_SKIP_DRAW, NULL);
            AddTextPrinterParameterized(0, FONT_SMALL, GetSpeciesName(sCustomStarterList[start + i]), 15, y, TEXT_SKIP_DRAW, NULL);
        }

        AddTextPrinterParameterized(0, FONT_SMALL, GetSpeciesName(species), 145, 101, TEXT_SKIP_DRAW, NULL);
        AddTextPrinterParameterized(0, FONT_SMALL, gTypesInfo[gSpeciesInfo[species].types[0]].name, 145, 113, TEXT_SKIP_DRAW, NULL);
        if (gSpeciesInfo[species].types[1] != gSpeciesInfo[species].types[0])
            AddTextPrinterParameterized(0, FONT_SMALL, gTypesInfo[gSpeciesInfo[species].types[1]].name, 181, 113, TEXT_SKIP_DRAW, NULL);
        AddTextPrinterParameterized(0, FONT_SMALL, sText_CustomControls, 4, 119, TEXT_SKIP_DRAW, NULL);
    }
    else if (gTasks[taskId].tCustomState == 1)
    {
        AddTextPrinterParameterized(0, FONT_NORMAL, sText_CustomAppearance, 8, 8, TEXT_SKIP_DRAW, NULL);
        AddTextPrinterParameterized(0, FONT_NORMAL, GetSpeciesName(species), 8, 30, TEXT_SKIP_DRAW, NULL);
        if (!gTasks[taskId].tCustomShiny)
            AddTextPrinterParameterized(0, FONT_NORMAL, gText_SelectorArrow2, 16, 82, TEXT_SKIP_DRAW, NULL);
        else
            AddTextPrinterParameterized(0, FONT_NORMAL, gText_SelectorArrow2, 112, 82, TEXT_SKIP_DRAW, NULL);
        AddTextPrinterParameterized(0, FONT_NORMAL, sText_CustomNormal, 32, 82, TEXT_SKIP_DRAW, NULL);
        AddTextPrinterParameterized(0, FONT_NORMAL, sText_CustomShiny, 128, 82, TEXT_SKIP_DRAW, NULL);
        AddTextPrinterParameterized(0, FONT_SMALL, sText_CustomBack, 8, 112, TEXT_SKIP_DRAW, NULL);
    }
    else
    {
        AddTextPrinterParameterized(0, FONT_NORMAL, sText_CustomConfirm, 8, 8, TEXT_SKIP_DRAW, NULL);
        AddTextPrinterParameterized(0, FONT_NORMAL, GetSpeciesName(species), 8, 30, TEXT_SKIP_DRAW, NULL);
        AddTextPrinterParameterized(0, FONT_NORMAL, gTasks[taskId].tCustomShiny ? sText_CustomShiny : sText_CustomNormal, 8, 50, TEXT_SKIP_DRAW, NULL);
        if (gTasks[taskId].tCustomConfirmChoice == 0)
            AddTextPrinterParameterized(0, FONT_NORMAL, gText_SelectorArrow2, 24, 88, TEXT_SKIP_DRAW, NULL);
        else
            AddTextPrinterParameterized(0, FONT_NORMAL, gText_SelectorArrow2, 112, 88, TEXT_SKIP_DRAW, NULL);
        AddTextPrinterParameterized(0, FONT_NORMAL, sText_CustomYes, 40, 88, TEXT_SKIP_DRAW, NULL);
        AddTextPrinterParameterized(0, FONT_NORMAL, sText_CustomNo, 128, 88, TEXT_SKIP_DRAW, NULL);
        AddTextPrinterParameterized(0, FONT_SMALL, sText_CustomBack, 8, 112, TEXT_SKIP_DRAW, NULL);
    }

    PutWindowTilemap(0);
    CopyWindowToVram(0, COPYWIN_FULL);
}

static void CustomStarterJumpToTab(u8 taskId, u8 tab)
{
    u16 i;
    gTasks[taskId].tCustomTab = tab;
    for (i = 0; i < sCustomStarterCount; i++)
    {
        if (GetCustomStarterTab(sCustomStarterList[i]) == tab)
        {
            gTasks[taskId].tCustomIndex = i;
            CustomStarterUpdatePreview(taskId);
            CustomStarterDraw(taskId);
            return;
        }
    }
}

static void Task_CustomStarterInput(u8 taskId)
{
    if (sCustomStarterCount == 0)
        return;

    if (gTasks[taskId].tCustomState == 0)
    {
        if (JOY_NEW(DPAD_UP))
        {
            if (gTasks[taskId].tCustomIndex == 0)
                gTasks[taskId].tCustomIndex = sCustomStarterCount - 1;
            else
                gTasks[taskId].tCustomIndex--;
            gTasks[taskId].tCustomTab = GetCustomStarterTab(sCustomStarterList[gTasks[taskId].tCustomIndex]);
            CustomStarterUpdatePreview(taskId);
            CustomStarterDraw(taskId);
        }
        else if (JOY_NEW(DPAD_DOWN))
        {
            gTasks[taskId].tCustomIndex = (gTasks[taskId].tCustomIndex + 1) % sCustomStarterCount;
            gTasks[taskId].tCustomTab = GetCustomStarterTab(sCustomStarterList[gTasks[taskId].tCustomIndex]);
            CustomStarterUpdatePreview(taskId);
            CustomStarterDraw(taskId);
        }
        else if (JOY_NEW(L_BUTTON))
        {
            u8 tab = gTasks[taskId].tCustomTab == 0 ? CUSTOM_STARTER_TABS - 1 : gTasks[taskId].tCustomTab - 1;
            CustomStarterJumpToTab(taskId, tab);
        }
        else if (JOY_NEW(R_BUTTON))
        {
            u8 tab = (gTasks[taskId].tCustomTab + 1) % CUSTOM_STARTER_TABS;
            CustomStarterJumpToTab(taskId, tab);
        }
        else if (JOY_NEW(A_BUTTON))
        {
            PlaySE(SE_SELECT);
            gTasks[taskId].tCustomState = 1;
            gTasks[taskId].tCustomShiny = FALSE;
            CustomStarterUpdatePreview(taskId);
            CustomStarterDraw(taskId);
        }
    }
    else if (gTasks[taskId].tCustomState == 1)
    {
        if (JOY_NEW(DPAD_LEFT) || JOY_NEW(DPAD_RIGHT))
        {
            gTasks[taskId].tCustomShiny ^= 1;
            CustomStarterUpdatePreview(taskId);
            CustomStarterDraw(taskId);
        }
        else if (JOY_NEW(B_BUTTON))
        {
            gTasks[taskId].tCustomState = 0;
            CustomStarterUpdatePreview(taskId);
            CustomStarterDraw(taskId);
        }
        else if (JOY_NEW(A_BUTTON))
        {
            gTasks[taskId].tCustomState = 2;
            gTasks[taskId].tCustomConfirmChoice = 0;
            CustomStarterDraw(taskId);
        }
    }
    else
    {
        if (JOY_NEW(DPAD_LEFT) || JOY_NEW(DPAD_RIGHT))
        {
            gTasks[taskId].tCustomConfirmChoice ^= 1;
            CustomStarterDraw(taskId);
        }
        else if (JOY_NEW(B_BUTTON))
        {
            gTasks[taskId].tCustomState = 1;
            CustomStarterDraw(taskId);
        }
        else if (JOY_NEW(A_BUTTON))
        {
            if (gTasks[taskId].tCustomConfirmChoice == 0)
            {
                gCustomStarterSpecies = sCustomStarterList[gTasks[taskId].tCustomIndex];
                gCustomStarterShiny = gTasks[taskId].tCustomShiny;
                gSpecialVar_Result = 0;
                CustomStarterDestroyPreview();
                ResetAllPicSprites();
                SetMainCallback2(gMain.savedCallback);
            }
            else
            {
                gTasks[taskId].tCustomState = 1;
                CustomStarterDraw(taskId);
            }
        }
    }
}

static void BeginCustomStarterSelection(void)
{
    u8 taskId;

    BuildCustomStarterList();
    gCustomStarterSpecies = SPECIES_NONE;
    gCustomStarterShiny = FALSE;
    sCustomPreviewSpriteId = SPRITE_NONE;

    taskId = CreateTask(Task_CustomStarterInput, 0);
    gTasks[taskId].tCustomIndex = 0;
    gTasks[taskId].tCustomTab = sCustomStarterCount ? GetCustomStarterTab(sCustomStarterList[0]) : 0;
    gTasks[taskId].tCustomState = 0;
    gTasks[taskId].tCustomShiny = FALSE;
    gTasks[taskId].tCustomConfirmChoice = 0;

    CustomStarterUpdatePreview(taskId);
    CustomStarterDraw(taskId);
}

'''
s = replace_once(s, insert_anchor, custom_code + insert_anchor, 'custom selector functions')
p.write_text(s)

# --- Expose custom choice to the first-battle giver ---
p = Path('include/starter_choose.h')
s = p.read_text()
s = replace_once(s,
    'u16 GetStarterPokemon(u16 chosenStarterId);\nvoid CB2_ChooseStarter(void);\n',
    'extern EWRAM_DATA u16 gCustomStarterSpecies;\nextern EWRAM_DATA bool8 gCustomStarterShiny;\n\nu16 GetStarterPokemon(u16 chosenStarterId);\nvoid CB2_ChooseStarter(void);\n',
    'custom externs')
p.write_text(s)

# --- Force the selected custom starter shiny when requested ---
p = Path('src/battle_setup.c')
s = p.read_text()
s = replace_once(s,
    '#include "starter_choose.h"\n',
    '#include "starter_choose.h"\n#include "run_settings.h"\n',
    'run settings include')
s = replace_once(s,
    '    ScriptGiveMon(starterMon, 5, ITEM_NONE);\n    ResetTasks();\n',
    '''    ScriptGiveMon(starterMon, 5, ITEM_NONE);\n    if (gSaveBlock3Ptr->starterMode == RUN_STARTER_CHOOSE && gCustomStarterShiny)\n    {\n        struct Pokemon *starter = &gParties[B_TRAINER_PLAYER][0];\n        u32 otId = GetMonData(starter, MON_DATA_OT_ID);\n        u32 personality = GetMonData(starter, MON_DATA_PERSONALITY);\n        u16 shinyLow = (u16)otId ^ (u16)(otId >> 16) ^ (u16)(personality >> 16);\n        personality = (personality & 0xFFFF0000) | shinyLow;\n        UpdateMonPersonality(&starter->box, personality);\n        CalculateMonStats(starter);\n    }\n    ResetTasks();\n''',
    'force shiny custom starter')
p.write_text(s)

print('Custom starter patch applied successfully.')
