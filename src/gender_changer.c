#include "global.h"
#include "event_data.h"
#include "pokemon.h"
#include "constants/battle.h"
#include "constants/pokemon.h"

// Changes the selected party Pokemon's gender while preserving its nature.
// gSpecialVar_0x8004 = party slot; gSpecialVar_Result = requested gender
// (0 = male, nonzero = female). On return, Result is 0 on success,
// 2 for genderless, 3 for male-only requested female, 4 for female-only
// requested male.
void SetSelectedMonGender(void)
{
    struct Pokemon *mon = &gParties[B_TRAINER_PLAYER][gSpecialVar_0x8004];
    enum Species species = GetMonData(mon, MON_DATA_SPECIES);
    u8 genderRatio = gSpeciesInfo[species].genderRatio;
    u8 requestedGender = (gSpecialVar_Result == 0) ? MON_MALE : MON_FEMALE;
    u8 nature = GetNature(mon);
    u32 personality;

    if (genderRatio == MON_GENDERLESS)
    {
        gSpecialVar_Result = 2;
        return;
    }

    if (genderRatio == MON_MALE && requestedGender == MON_FEMALE)
    {
        gSpecialVar_Result = 3;
        return;
    }

    if (genderRatio == MON_FEMALE && requestedGender == MON_MALE)
    {
        gSpecialVar_Result = 4;
        return;
    }

    // Single-gender species already have the requested gender. For mixed-gender
    // species, use the expansion's personality generator so the new PID has the
    // requested gender while retaining the Pokemon's current nature.
    if (genderRatio != MON_MALE && genderRatio != MON_FEMALE)
    {
        personality = GetMonPersonality(species, requestedGender, nature, RANDOM_UNOWN_LETTER);
        SetMonData(mon, MON_DATA_PERSONALITY, &personality);
        CalculateMonStats(mon);
    }

    gSpecialVar_Result = 0;
}
