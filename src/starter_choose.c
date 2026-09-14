#include "global.h"
#include "bg.h"
#include "data.h"
#include "decompress.h"
#include "event_data.h"
#include "gpu_regs.h"
#include "international_string_util.h"
#include "main.h"
#include "menu.h"
#include "palette.h"
#include "pokedex.h"
#include "pokemon.h"
#include "random.h"
#include "random_mon_generation.h"
#include "constants/random_mon_generation.h"
#include "scanline_effect.h"
#include "sound.h"
#include "sprite.h"
#include "starter_choose.h"
#include "strings.h"
#include "task.h"
#include "text.h"
#include "text_window.h"
#include "trainer_pokemon_sprites.h"
#include "trig.h"
#include "window.h"
#include "constants/songs.h"
#include "constants/rgb.h"
#include "run_settings.h"

#define STARTER_MON_COUNT   3
#define CUSTOM_STARTER_ROWS  8
#define CUSTOM_STARTER_TABS  6


// Position of the sprite of the selected starter Pokémon
#define STARTER_PKMN_POS_X (DISPLAY_WIDTH / 2)
#define STARTER_PKMN_POS_Y 64

#define TAG_POKEBALL_SELECT 0x1000
#define TAG_STARTER_CIRCLE  0x1001

static void CB2_StarterChoose(void);
static void ClearStarterLabel(void);
static void Task_StarterChoose(u8 taskId);
static void Task_HandleStarterChooseInput(u8 taskId);
static void Task_WaitForStarterSprite(u8 taskId);
static void Task_AskConfirmStarter(u8 taskId);
static void Task_HandleConfirmStarterInput(u8 taskId);
static void Task_DeclineStarter(u8 taskId);
static void Task_MoveStarterChooseCursor(u8 taskId);
static void Task_CreateStarterLabel(u8 taskId);
static void CreateStarterPokemonLabel(u8 selection);
static u8 CreatePokemonFrontSprite(enum Species species, u8 x, u8 y);
static void SpriteCB_SelectionHand(struct Sprite *sprite);
static void SpriteCB_Pokeball(struct Sprite *sprite);
static void SpriteCB_StarterPokemon(struct Sprite *sprite);
static void BeginCustomStarterSelection(void);
static void Task_CustomStarterInput(u8 taskId);
static void BuildCustomStarterList(void);
static bool32 IsCustomStarterEligible(enum Species species);
static u8 GetCustomStarterTab(enum Species species);
static void CustomStarterJumpToTab(u8 taskId, u8 tab);
static void CustomStarterDraw(u8 taskId);
static void CustomStarterUpdatePreview(u8 taskId);
static void CustomStarterDestroyPreview(void);

static u16 sStarterLabelWindowId;
EWRAM_DATA u16 gCustomStarterSpecies = SPECIES_NONE;
EWRAM_DATA bool8 gCustomStarterShiny = FALSE;
static EWRAM_DATA u16 sCustomStarterList[NUM_SPECIES];
static EWRAM_DATA u16 sCustomStarterCount;
static EWRAM_DATA u8 sCustomPreviewSpriteId = SPRITE_NONE;

const u16 gBirchBagGrass_Pal[] = INCGFX_U16("graphics/starter_choose/tiles.png", ".gbapal");
static const u16 sPokeballSelection_Pal[] = INCGFX_U16("graphics/starter_choose/pokeball_selection.png", ".gbapal");
static const u16 sStarterCircle_Pal[] = INCGFX_U16("graphics/starter_choose/starter_circle.png", ".gbapal");
const u32 gBirchBagTilemap[] = INCGFX_U32("graphics/starter_choose/birch_bag.bin", ".smolTM");
const u32 gBirchGrassTilemap[] = INCGFX_U32("graphics/starter_choose/birch_grass.bin", ".smolTM");
const u32 gBirchBagGrass_Gfx[] = INCGFX_U32("graphics/starter_choose/tiles.png", ".4bpp.smol");
const u32 gPokeballSelection_Gfx[] = INCGFX_U32("graphics/starter_choose/pokeball_selection.png", ".4bpp.smol");
static const u32 sStarterCircle_Gfx[] = INCGFX_U32("graphics/starter_choose/starter_circle.png", ".4bpp.smol");

static const struct WindowTemplate sWindowTemplates[] =
{
    {
        .bg = 0,
        .tilemapLeft = 3,
        .tilemapTop = 15,
        .width = 24,
        .height = 4,
        .paletteNum = 14,
        .baseBlock = 0x0200
    },
    DUMMY_WIN_TEMPLATE,
};

static const struct WindowTemplate sCustomWindowTemplates[] =
{
    {
        .bg = 0,
        .tilemapLeft = 1,
        .tilemapTop = 1,
        .width = 28,
        .height = 16,
        .paletteNum = 14,
        .baseBlock = 0x0200
    },
    DUMMY_WIN_TEMPLATE,
};

static const struct WindowTemplate sWindowTemplate_ConfirmStarter =
{
    .bg = 0,
    .tilemapLeft = 24,
    .tilemapTop = 9,
    .width = 5,
    .height = 4,
    .paletteNum = 14,
    .baseBlock = 0x0260
};

static const struct WindowTemplate sWindowTemplate_StarterLabel =
{
    .bg = 0,
    .tilemapLeft = 0,
    .tilemapTop = 0,
    .width = 13,
    .height = 4,
    .paletteNum = 14,
    .baseBlock = 0x0274
};

static const u8 sPokeballCoords[STARTER_MON_COUNT][2] =
{
    {60, 64},
    {120, 88},
    {180, 64},
};

static const u8 sStarterLabelCoords[STARTER_MON_COUNT][2] =
{
    {0, 9},
    {16, 10},
    {8, 4},
};


static u16 sStarterMon[STARTER_MON_COUNT];

static void GenerateRandomStarters(void)
{
    bool8 filtered = gSaveBlock3Ptr->filterMode != RUN_FILTER_NONE;
    u32 generator = SPECIES_GENERATOR_NO_SUPERMONS;

    if (gSaveBlock3Ptr->starterMode == RUN_STARTER_NORMAL && !filtered)
    {
        sStarterMon[0] = SPECIES_TREECKO;
        sStarterMon[1] = SPECIES_TORCHIC;
        sStarterMon[2] = SPECIES_MUDKIP;
        return;
    }

    if (gSaveBlock3Ptr->starterMode != RUN_STARTER_RANDOM && !filtered)
        return;

    rng_value_t oldRngState = gRngValue;
    struct FilterFuncArgs filterArgs =
    {
        .arg1 = FILTER_FUNC_ARG_NONE,
        .arg2 = FILTER_FUNC_ARG_NONE,
    };

    if (filtered)
    {
        filterArgs.arg1 = gSaveBlock3Ptr->filterValue;
        if (gSaveBlock3Ptr->randomizerEnabled == RUN_WILD_SCALED)
            filterArgs.arg2 = 0;

        if (gSaveBlock3Ptr->filterMode == RUN_FILTER_TYPE)
            generator = gSaveBlock3Ptr->randomizerEnabled == RUN_WILD_SCALED ? SPECIES_GENERATOR_SCALED_TYPE_FILTERED : SPECIES_GENERATOR_TYPE_FILTERED;
        else if (gSaveBlock3Ptr->filterMode == RUN_FILTER_ABILITY)
            generator = gSaveBlock3Ptr->randomizerEnabled == RUN_WILD_SCALED ? SPECIES_GENERATOR_SCALED_ABILITY_FILTERED : SPECIES_GENERATOR_ABILITY_FILTERED;
        else
            generator = gSaveBlock3Ptr->randomizerEnabled == RUN_WILD_SCALED ? SPECIES_GENERATOR_SCALED_TYPE_ABILITY_FILTERED : SPECIES_GENERATOR_TYPE_ABILITY_FILTERED;
    }

    // Setup prevents pools smaller than three, but retain a safe fallback for
    // old/corrupt saves so the third Poké Ball can never become SPECIES_NONE.
    if (filtered && CountEligibleRandomSpecies(generator, &filterArgs, STARTER_MON_COUNT) < STARTER_MON_COUNT)
    {
        sStarterMon[0] = SPECIES_TREECKO;
        sStarterMon[1] = SPECIES_TORCHIC;
        sStarterMon[2] = SPECIES_MUDKIP;
        return;
    }

    SeedRng(gSaveBlock3Ptr->worldSeed);

    for (u32 i = 0; i < STARTER_MON_COUNT; i++)
    {
        do
        {
            sStarterMon[i] = GetRandomSpecies(generator, &filterArgs);
        }
        while ((i > 0 && sStarterMon[i] == sStarterMon[0])
            || (i > 1 && sStarterMon[i] == sStarterMon[1]));
    }

    gRngValue = oldRngState;
}

static const struct BgTemplate sBgTemplates[] =
{
    {
        .bg = 0,
        .charBaseIndex = 2,
        .mapBaseIndex = 31,
        .screenSize = 0,
        .paletteMode = 0,
        .priority = 0,
        .baseTile = 0
    },
    {
        .bg = 2,
        .charBaseIndex = 0,
        .mapBaseIndex = 7,
        .screenSize = 0,
        .paletteMode = 0,
        .priority = 3,
        .baseTile = 0
    },
    {
        .bg = 3,
        .charBaseIndex = 0,
        .mapBaseIndex = 6,
        .screenSize = 0,
        .paletteMode = 0,
        .priority = 1,
        .baseTile = 0
    },
};

static const u8 sTextColors[] = {TEXT_COLOR_TRANSPARENT, TEXT_COLOR_WHITE, TEXT_COLOR_LIGHT_GRAY};
static const u8 sCustomTabs[CUSTOM_STARTER_TABS][5] =
{
    _("A-D"), _("E-H"), _("I-L"), _("M-P"), _("Q-T"), _("U-Z"),
};
static const u8 sText_CustomStarterTitle[] = _("CHOOSE YOUR STARTER");
static const u8 sText_CustomAppearance[] = _("CHOOSE APPEARANCE");
static const u8 sText_CustomNormal[] = _("NORMAL");
static const u8 sText_CustomShiny[] = _("SHINY");
static const u8 sText_CustomConfirm[] = _("USE THIS STARTER?");
static const u8 sText_CustomYes[] = _("YES");
static const u8 sText_CustomNo[] = _("NO");
static const u8 sText_CustomControls[] = _("L/R TABS   A SELECT");
static const u8 sText_CustomBack[] = _("A CONFIRM   B BACK");
static const u8 sLetterE[] = _("E");
static const u8 sLetterI[] = _("I");
static const u8 sLetterM[] = _("M");
static const u8 sLetterQ[] = _("Q");
static const u8 sLetterU[] = _("U");

static const struct OamData sOam_Hand =
{
    .y = DISPLAY_HEIGHT,
    .affineMode = ST_OAM_AFFINE_OFF,
    .objMode = ST_OAM_OBJ_NORMAL,
    .mosaic = FALSE,
    .bpp = ST_OAM_4BPP,
    .shape = SPRITE_SHAPE(32x32),
    .x = 0,
    .matrixNum = 0,
    .size = SPRITE_SIZE(32x32),
    .tileNum = 0,
    .priority = 1,
    .paletteNum = 0,
    .affineParam = 0,
};

static const struct OamData sOam_Pokeball =
{
    .y = DISPLAY_HEIGHT,
    .affineMode = ST_OAM_AFFINE_OFF,
    .objMode = ST_OAM_OBJ_NORMAL,
    .mosaic = FALSE,
    .bpp = ST_OAM_4BPP,
    .shape = SPRITE_SHAPE(32x32),
    .x = 0,
    .matrixNum = 0,
    .size = SPRITE_SIZE(32x32),
    .tileNum = 0,
    .priority = 1,
    .paletteNum = 0,
    .affineParam = 0,
};

static const struct OamData sOam_StarterCircle =
{
    .y = DISPLAY_HEIGHT,
    .affineMode = ST_OAM_AFFINE_DOUBLE,
    .objMode = ST_OAM_OBJ_NORMAL,
    .mosaic = FALSE,
    .bpp = ST_OAM_4BPP,
    .shape = SPRITE_SHAPE(64x64),
    .x = 0,
    .matrixNum = 0,
    .size = SPRITE_SIZE(64x64),
    .tileNum = 0,
    .priority = 1,
    .paletteNum = 0,
    .affineParam = 0,
};

static const u8 sCursorCoords[][2] =
{
    {60, 32},
    {120, 56},
    {180, 32},
};

static const union AnimCmd sAnim_Hand[] =
{
    ANIMCMD_FRAME(48, 30),
    ANIMCMD_END,
};

static const union AnimCmd sAnim_Pokeball_Still[] =
{
    ANIMCMD_FRAME(0, 30),
    ANIMCMD_END,
};

static const union AnimCmd sAnim_Pokeball_Moving[] =
{
    ANIMCMD_FRAME(16, 4),
    ANIMCMD_FRAME(0, 4),
    ANIMCMD_FRAME(32, 4),
    ANIMCMD_FRAME(0, 4),
    ANIMCMD_FRAME(16, 4),
    ANIMCMD_FRAME(0, 4),
    ANIMCMD_FRAME(32, 4),
    ANIMCMD_FRAME(0, 4),
    ANIMCMD_FRAME(0, 32),
    ANIMCMD_FRAME(16, 8),
    ANIMCMD_FRAME(0, 8),
    ANIMCMD_FRAME(32, 8),
    ANIMCMD_FRAME(0, 8),
    ANIMCMD_FRAME(16, 8),
    ANIMCMD_FRAME(0, 8),
    ANIMCMD_FRAME(32, 8),
    ANIMCMD_FRAME(0, 8),
    ANIMCMD_JUMP(0),
};

static const union AnimCmd sAnim_StarterCircle[] =
{
    ANIMCMD_FRAME(0, 8),
    ANIMCMD_END,
};

static const union AnimCmd *const sAnims_Hand[] =
{
    sAnim_Hand,
};

static const union AnimCmd *const sAnims_Pokeball[] =
{
    sAnim_Pokeball_Still,
    sAnim_Pokeball_Moving,
};

static const union AnimCmd *const sAnims_StarterCircle[] =
{
    sAnim_StarterCircle,
};

static const union AffineAnimCmd sAffineAnim_StarterPokemon[] =
{
    AFFINEANIMCMD_FRAME(16, 16, 0, 0),
    AFFINEANIMCMD_FRAME(16, 16, 0, 15),
    AFFINEANIMCMD_END,
};

static const union AffineAnimCmd sAffineAnim_StarterCircle[] =
{
    AFFINEANIMCMD_FRAME(20, 20, 0, 0),
    AFFINEANIMCMD_FRAME(20, 20, 0, 15),
    AFFINEANIMCMD_END,
};

static const union AffineAnimCmd *const sAffineAnims_StarterPokemon = {sAffineAnim_StarterPokemon};
static const union AffineAnimCmd *const sAffineAnims_StarterCircle[] = {sAffineAnim_StarterCircle};

static const struct CompressedSpriteSheet sSpriteSheet_PokeballSelect[] =
{
    {
        .data = gPokeballSelection_Gfx,
        .size = 0x0800,
        .tag = TAG_POKEBALL_SELECT
    },
    {}
};

static const struct CompressedSpriteSheet sSpriteSheet_StarterCircle[] =
{
    {
        .data = sStarterCircle_Gfx,
        .size = 0x0800,
        .tag = TAG_STARTER_CIRCLE
    },
    {}
};

static const struct SpritePalette sSpritePalettes_StarterChoose[] =
{
    {
        .data = sPokeballSelection_Pal,
        .tag = TAG_POKEBALL_SELECT
    },
    {
        .data = sStarterCircle_Pal,
        .tag = TAG_STARTER_CIRCLE
    },
    {},
};

static const struct SpriteTemplate sSpriteTemplate_Hand =
{
    .tileTag = TAG_POKEBALL_SELECT,
    .paletteTag = TAG_POKEBALL_SELECT,
    .oam = &sOam_Hand,
    .anims = sAnims_Hand,
    .callback = SpriteCB_SelectionHand
};

static const struct SpriteTemplate sSpriteTemplate_Pokeball =
{
    .tileTag = TAG_POKEBALL_SELECT,
    .paletteTag = TAG_POKEBALL_SELECT,
    .oam = &sOam_Pokeball,
    .anims = sAnims_Pokeball,
    .callback = SpriteCB_Pokeball
};

static const struct SpriteTemplate sSpriteTemplate_StarterCircle =
{
    .tileTag = TAG_STARTER_CIRCLE,
    .paletteTag = TAG_STARTER_CIRCLE,
    .oam = &sOam_StarterCircle,
    .anims = sAnims_StarterCircle,
    .affineAnims = sAffineAnims_StarterCircle,
    .callback = SpriteCB_StarterPokemon
};

// .text
u16 GetStarterPokemon(u16 chosenStarterId)
{
    if (gSaveBlock3Ptr->starterMode == RUN_STARTER_CHOOSE && gCustomStarterSpecies != SPECIES_NONE)
        return gCustomStarterSpecies;
    if (chosenStarterId >= STARTER_MON_COUNT)
        chosenStarterId = 0;
    return sStarterMon[chosenStarterId];
}

static void VblankCB_StarterChoose(void)
{
    LoadOam();
    ProcessSpriteCopyRequests();
    TransferPlttBuffer();
}

// Data for Task_StarterChoose
#define tStarterSelection   data[0]
#define tPkmnSpriteId       data[1]
#define tCircleSpriteId     data[2]

// Data for sSpriteTemplate_Pokeball
#define sTaskId data[0]
#define sBallId data[1]

void CB2_ChooseStarter(void)
{
    u8 taskId;
    u8 spriteId;

    GenerateRandomStarters();

    SetVBlankCallback(NULL);

    SetGpuReg(REG_OFFSET_DISPCNT, 0);
    SetGpuReg(REG_OFFSET_BG3CNT, 0);
    SetGpuReg(REG_OFFSET_BG2CNT, 0);
    SetGpuReg(REG_OFFSET_BG1CNT, 0);
    SetGpuReg(REG_OFFSET_BG0CNT, 0);

    ChangeBgX(0, 0, BG_COORD_SET);
    ChangeBgY(0, 0, BG_COORD_SET);
    ChangeBgX(1, 0, BG_COORD_SET);
    ChangeBgY(1, 0, BG_COORD_SET);
    ChangeBgX(2, 0, BG_COORD_SET);
    ChangeBgY(2, 0, BG_COORD_SET);
    ChangeBgX(3, 0, BG_COORD_SET);
    ChangeBgY(3, 0, BG_COORD_SET);

    DmaFill16(3, 0, VRAM, VRAM_SIZE);
    DmaFill32(3, 0, OAM, OAM_SIZE);
    DmaFill16(3, 0, PLTT, PLTT_SIZE);

    DecompressDataWithHeaderVram(gBirchBagGrass_Gfx, (void *)VRAM);
    DecompressDataWithHeaderVram(gBirchBagTilemap, (void *)(BG_SCREEN_ADDR(6)));
    DecompressDataWithHeaderVram(gBirchGrassTilemap, (void *)(BG_SCREEN_ADDR(7)));

    ResetBgsAndClearDma3BusyFlags(0);
    InitBgsFromTemplates(0, sBgTemplates, ARRAY_COUNT(sBgTemplates));
    InitWindows(gSaveBlock3Ptr->starterMode == RUN_STARTER_CHOOSE ? sCustomWindowTemplates : sWindowTemplates);

    DeactivateAllTextPrinters();
    LoadUserWindowBorderGfx(0, 0x2A8, BG_PLTT_ID(13));
    ClearScheduledBgCopiesToVram();
    ScanlineEffect_Stop();
    ResetTasks();
    ResetSpriteData();
    ResetPaletteFade();
    FreeAllSpritePalettes();
    ResetAllPicSprites();

    LoadPalette(GetOverworldTextboxPalettePtr(), BG_PLTT_ID(14), PLTT_SIZE_4BPP);
    LoadPalette(gBirchBagGrass_Pal, BG_PLTT_ID(0), sizeof(gBirchBagGrass_Pal));
    LoadCompressedSpriteSheet(&sSpriteSheet_PokeballSelect[0]);
    LoadCompressedSpriteSheet(&sSpriteSheet_StarterCircle[0]);
    LoadSpritePalettes(sSpritePalettes_StarterChoose);
    BeginNormalPaletteFade(PALETTES_ALL, 0, 0x10, 0, RGB_BLACK);

    EnableInterrupts(DISPSTAT_VBLANK);
    SetVBlankCallback(VblankCB_StarterChoose);
    SetMainCallback2(CB2_StarterChoose);

    SetGpuReg(REG_OFFSET_WININ, WININ_WIN0_BG_ALL | WININ_WIN0_OBJ | WININ_WIN0_CLR);
    SetGpuReg(REG_OFFSET_WINOUT, WINOUT_WIN01_BG_ALL | WINOUT_WIN01_OBJ);
    SetGpuReg(REG_OFFSET_WIN0H, 0);
    SetGpuReg(REG_OFFSET_WIN0V, 0);
    SetGpuReg(REG_OFFSET_BLDCNT, BLDCNT_TGT1_BG1 | BLDCNT_TGT1_BG2 | BLDCNT_TGT1_BG3 | BLDCNT_TGT1_OBJ | BLDCNT_TGT1_BD | BLDCNT_EFFECT_DARKEN);
    SetGpuReg(REG_OFFSET_BLDALPHA, 0);
    SetGpuReg(REG_OFFSET_BLDY, 7);
    SetGpuReg(REG_OFFSET_DISPCNT, DISPCNT_WIN0_ON | DISPCNT_OBJ_ON | DISPCNT_OBJ_1D_MAP);

    ShowBg(0);
    ShowBg(2);
    ShowBg(3);

    if (gSaveBlock3Ptr->starterMode == RUN_STARTER_CHOOSE)
    {
        BeginCustomStarterSelection();
        return;
    }

    taskId = CreateTask(Task_StarterChoose, 0);
    gTasks[taskId].tStarterSelection = 1;

    // Create hand sprite
    spriteId = CreateSprite(&sSpriteTemplate_Hand, 120, 56, 2);
    gSprites[spriteId].data[0] = taskId;

    // Create three Poké Ball sprites
    spriteId = CreateSprite(&sSpriteTemplate_Pokeball, sPokeballCoords[0][0], sPokeballCoords[0][1], 2);
    gSprites[spriteId].sTaskId = taskId;
    gSprites[spriteId].sBallId = 0;

    spriteId = CreateSprite(&sSpriteTemplate_Pokeball, sPokeballCoords[1][0], sPokeballCoords[1][1], 2);
    gSprites[spriteId].sTaskId = taskId;
    gSprites[spriteId].sBallId = 1;

    spriteId = CreateSprite(&sSpriteTemplate_Pokeball, sPokeballCoords[2][0], sPokeballCoords[2][1], 2);
    gSprites[spriteId].sTaskId = taskId;
    gSprites[spriteId].sBallId = 2;

    sStarterLabelWindowId = WINDOW_NONE;
}

static void CB2_StarterChoose(void)
{
    RunTasks();
    AnimateSprites();
    BuildOamBuffer();
    DoScheduledBgTilemapCopiesToVram();
    UpdatePaletteFade();
}

static void Task_StarterChoose(u8 taskId)
{
    CreateStarterPokemonLabel(gTasks[taskId].tStarterSelection);
    DrawStdFrameWithCustomTileAndPalette(0, FALSE, 0x2A8, 0xD);
    AddTextPrinterParameterized(0, FONT_NORMAL, gText_BirchInTrouble, 0, 1, 0, NULL);
    PutWindowTilemap(0);
    ScheduleBgCopyTilemapToVram(0);
    gTasks[taskId].func = Task_HandleStarterChooseInput;
}

static void Task_HandleStarterChooseInput(u8 taskId)
{
    u8 selection = gTasks[taskId].tStarterSelection;

    if (JOY_NEW(A_BUTTON))
    {
        u8 spriteId;

        ClearStarterLabel();

        // Create white circle background
        spriteId = CreateSprite(&sSpriteTemplate_StarterCircle, sPokeballCoords[selection][0], sPokeballCoords[selection][1], 1);
        gTasks[taskId].tCircleSpriteId = spriteId;

        // Create Pokémon sprite
        spriteId = CreatePokemonFrontSprite(GetStarterPokemon(gTasks[taskId].tStarterSelection), sPokeballCoords[selection][0], sPokeballCoords[selection][1]);
        gSprites[spriteId].affineAnims = &sAffineAnims_StarterPokemon;
        gSprites[spriteId].callback = SpriteCB_StarterPokemon;

        gTasks[taskId].tPkmnSpriteId = spriteId;
        gTasks[taskId].func = Task_WaitForStarterSprite;
    }
    else if (JOY_NEW(DPAD_LEFT) && selection > 0)
    {
        gTasks[taskId].tStarterSelection--;
        gTasks[taskId].func = Task_MoveStarterChooseCursor;
    }
    else if (JOY_NEW(DPAD_RIGHT) && selection < STARTER_MON_COUNT - 1)
    {
        gTasks[taskId].tStarterSelection++;
        gTasks[taskId].func = Task_MoveStarterChooseCursor;
    }
}

static void Task_WaitForStarterSprite(u8 taskId)
{
    if (gSprites[gTasks[taskId].tCircleSpriteId].affineAnimEnded &&
        gSprites[gTasks[taskId].tCircleSpriteId].x == STARTER_PKMN_POS_X &&
        gSprites[gTasks[taskId].tCircleSpriteId].y == STARTER_PKMN_POS_Y)
    {
        gTasks[taskId].func = Task_AskConfirmStarter;
    }
}

static void Task_AskConfirmStarter(u8 taskId)
{
    PlayCry_Normal(GetStarterPokemon(gTasks[taskId].tStarterSelection), 0);
    FillWindowPixelBuffer(0, PIXEL_FILL(1));
    AddTextPrinterParameterized(0, FONT_NORMAL, gText_ConfirmStarterChoice, 0, 1, 0, NULL);
    ScheduleBgCopyTilemapToVram(0);
    CreateYesNoMenu(&sWindowTemplate_ConfirmStarter, 0x2A8, 0xD, 0);
    gTasks[taskId].func = Task_HandleConfirmStarterInput;
}

static void Task_HandleConfirmStarterInput(u8 taskId)
{
    u8 spriteId;

    switch (Menu_ProcessInputNoWrapClearOnChoose())
    {
    case 0:  // YES
        // Return the starter choice and exit.
        gSpecialVar_Result = gTasks[taskId].tStarterSelection;
        ResetAllPicSprites();
        SetMainCallback2(gMain.savedCallback);
        break;
    case 1:  // NO
    case MENU_B_PRESSED:
        PlaySE(SE_SELECT);
        spriteId = gTasks[taskId].tPkmnSpriteId;
        FreeOamMatrix(gSprites[spriteId].oam.matrixNum);
        FreeAndDestroyMonPicSprite(spriteId);

        spriteId = gTasks[taskId].tCircleSpriteId;
        FreeOamMatrix(gSprites[spriteId].oam.matrixNum);
        DestroySprite(&gSprites[spriteId]);
        gTasks[taskId].func = Task_DeclineStarter;
        break;
    }
}

static void Task_DeclineStarter(u8 taskId)
{
    gTasks[taskId].func = Task_StarterChoose;
}

static void CreateStarterPokemonLabel(u8 selection)
{
    u8 categoryText[32];
    struct WindowTemplate winTemplate;
    const u8 *speciesName;
    s32 width;
    u8 labelLeft, labelRight, labelTop, labelBottom;

    enum Species species = GetStarterPokemon(selection);
    CopyMonCategoryText(species, categoryText);
    speciesName = GetSpeciesName(species);

    winTemplate = sWindowTemplate_StarterLabel;
    winTemplate.tilemapLeft = sStarterLabelCoords[selection][0];
    winTemplate.tilemapTop = sStarterLabelCoords[selection][1];

    sStarterLabelWindowId = AddWindow(&winTemplate);
    FillWindowPixelBuffer(sStarterLabelWindowId, PIXEL_FILL(0));

    width = GetStringCenterAlignXOffset(FONT_NARROW, categoryText, 0x68);
    AddTextPrinterParameterized3(sStarterLabelWindowId, FONT_NARROW, width, 1, sTextColors, 0, categoryText);

    width = GetStringCenterAlignXOffset(FONT_NORMAL, speciesName, 0x68);
    AddTextPrinterParameterized3(sStarterLabelWindowId, FONT_NORMAL, width, 17, sTextColors, 0, speciesName);

    PutWindowTilemap(sStarterLabelWindowId);
    ScheduleBgCopyTilemapToVram(0);

    labelLeft = sStarterLabelCoords[selection][0] * 8 - 4;
    labelRight = (sStarterLabelCoords[selection][0] + 13) * 8 + 4;
    labelTop = sStarterLabelCoords[selection][1] * 8;
    labelBottom = (sStarterLabelCoords[selection][1] + 4) * 8;
    SetGpuReg(REG_OFFSET_WIN0H, WIN_RANGE(labelLeft, labelRight));
    SetGpuReg(REG_OFFSET_WIN0V, WIN_RANGE(labelTop, labelBottom));
}

static void ClearStarterLabel(void)
{
    FillWindowPixelBuffer(sStarterLabelWindowId, PIXEL_FILL(0));
    ClearWindowTilemap(sStarterLabelWindowId);
    RemoveWindow(sStarterLabelWindowId);
    sStarterLabelWindowId = WINDOW_NONE;
    SetGpuReg(REG_OFFSET_WIN0H, 0);
    SetGpuReg(REG_OFFSET_WIN0V, 0);
    ScheduleBgCopyTilemapToVram(0);
}

static void Task_MoveStarterChooseCursor(u8 taskId)
{
    ClearStarterLabel();
    gTasks[taskId].func = Task_CreateStarterLabel;
}

static void Task_CreateStarterLabel(u8 taskId)
{
    CreateStarterPokemonLabel(gTasks[taskId].tStarterSelection);
    gTasks[taskId].func = Task_HandleStarterChooseInput;
}

// Custom starter task data
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

static u8 CreatePokemonFrontSprite(enum Species species, u8 x, u8 y)
{
    u8 spriteId;

    spriteId = CreateMonPicSprite_Affine(species, FALSE, 0, MON_PIC_AFFINE_FRONT, x, y, 14, TAG_NONE);
    gSprites[spriteId].oam.priority = 0;
    return spriteId;
}

static void SpriteCB_SelectionHand(struct Sprite *sprite)
{
    // Float up and down above selected Poké Ball
    sprite->x = sCursorCoords[gTasks[sprite->data[0]].tStarterSelection][0];
    sprite->y = sCursorCoords[gTasks[sprite->data[0]].tStarterSelection][1];
    sprite->y2 = Sin(sprite->data[1], 8);
    sprite->data[1] = (u8)(sprite->data[1]) + 4;
}

static void SpriteCB_Pokeball(struct Sprite *sprite)
{
    // Animate Poké Ball if currently selected
    if (gTasks[sprite->sTaskId].tStarterSelection == sprite->sBallId)
        StartSpriteAnimIfDifferent(sprite, 1);
    else
        StartSpriteAnimIfDifferent(sprite, 0);
}

static void SpriteCB_StarterPokemon(struct Sprite *sprite)
{
    // Move sprite to upper center of screen
    if (sprite->x > STARTER_PKMN_POS_X)
        sprite->x -= 4;
    if (sprite->x < STARTER_PKMN_POS_X)
        sprite->x += 4;
    if (sprite->y > STARTER_PKMN_POS_Y)
        sprite->y -= 2;
    if (sprite->y < STARTER_PKMN_POS_Y)
        sprite->y += 2;
}
