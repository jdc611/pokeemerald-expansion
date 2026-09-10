#include "global.h"
#include "data.h"
#include "pokemon.h"
#include "script.h"
#include "trainer_util.h"
#include "constants/pokemon.h"

// Safely changes the selected party Pokemon's gender by updating its
// personality through UpdateMonPersonality, which preserves/re-encrypts the
// BoxPokemon substructures instead of corrupting them with a direct PID write.
void SetSelectedMonGender(void)
{
    struct Pokemon *mon = &gPlayerParty[gSpecialVar_0x8004];
    enum Species species = GetMonData(mon, MON_DATA_SPECIES);
    u32 requestedGender;
    u32 personality;
    u8 genderRatio = gSpeciesInfo[species].genderRatio;

    if (genderRatio == MON_GENDERLESS)
    {
        gSpecialVar_Result = 2;
        return;
    }

    requestedGender = (gSpecialVar_Result == 0) ? MON_MALE : MON_FEMALE;

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

    // Single-gender species are already the requested gender here, so no PID
    // change is necessary. Mixed-gender species receive a gender-valid PID.
    if (genderRatio != MON_MALE && genderRatio != MON_FEMALE)
    {
        personality = GeneratePersonalityForGender(requestedGender, species);
        UpdateMonPersonality(&mon->box, personality);
        CalculateMonStats(mon);
    }

    gSpecialVar_Result = 0;
}
