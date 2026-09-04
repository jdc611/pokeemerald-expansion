// Pool settings for random mon generation via scripts. For more info on options, check out
// struct RandomSpeciesGeneratorOptions and struct RandomItemGeneratorOptions in src/random_mon_generation.c.

#include "constants/random_mon_generation.h"

static const struct RandomSpeciesGeneratorOptions sRandomSpeciesGeneratorOptions[RANDOM_SPECIES_OPTIONS_COUNT] =
{
    [SPECIES_GENERATOR_NO_SUPERMONS] =
    {
        .banLegendary = TRUE,
        .banMythical = TRUE,
        .banSubLegendary = TRUE,
        .banUltraBeast = TRUE,
        .banParadox = TRUE,
        .randomizeForms = FALSE,
        .dexMode = RANDOM_MON_DEX_NATIONAL,
    },
};

static const struct RandomItemGeneratorOptions sRandomItemGeneratorOptions[RANDOM_ITEM_OPTIONS_COUNT] =
{
};
