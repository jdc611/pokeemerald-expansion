#include "global.h"
#include "challenge_reset.h"
#include "battle_setup.h"
#include "event_data.h"
#include "run_settings.h"
#include "constants/flags.h"
#include "constants/map_types.h"

#define MAX_CHALLENGE_TRAINERS 64

EWRAM_DATA static u16 sChallengeTrainers[MAX_CHALLENGE_TRAINERS] = {0};
EWRAM_DATA static u8 sChallengeTrainerCount = 0;
EWRAM_DATA static u8 sChallengeBadgeCountAtStart = 0;
EWRAM_DATA static mapsec_u16_t sChallengeMapSection = 0;
EWRAM_DATA static bool8 sChallengeIsGym = FALSE;
EWRAM_DATA static bool8 sChallengeActive = FALSE;

static bool8 ChallengeResetEnabled(void)
{
    return gSaveBlock3Ptr->runDifficulty == RUN_DIFFICULTY_HARD
        || gSaveBlock3Ptr->runDifficulty == RUN_DIFFICULTY_NUZLOCKE;
}

static bool8 IsChallengeMap(const struct MapHeader *map)
{
    return map->cave || map->battleType == MAP_BATTLE_SCENE_GYM;
}

static u8 CountBadges(void)
{
    u8 count = 0;
    u16 flag;
    for (flag = FLAG_BADGE01_GET; flag <= FLAG_BADGE08_GET; flag++)
        if (FlagGet(flag))
            count++;
    return count;
}

static void ClearChallengeState(void)
{
    sChallengeTrainerCount = 0;
    sChallengeActive = FALSE;
    sChallengeIsGym = FALSE;
}

void ChallengeReset_RecordTrainer(u16 trainerId)
{
    u8 i;

    if (!ChallengeResetEnabled() || !IsChallengeMap(&gMapHeader))
        return;

    if (!sChallengeActive)
    {
        sChallengeActive = TRUE;
        sChallengeMapSection = gMapHeader.regionMapSectionId;
        sChallengeIsGym = (gMapHeader.battleType == MAP_BATTLE_SCENE_GYM);
        sChallengeBadgeCountAtStart = CountBadges();
        sChallengeTrainerCount = 0;
    }

    for (i = 0; i < sChallengeTrainerCount; i++)
        if (sChallengeTrainers[i] == trainerId)
            return;

    if (sChallengeTrainerCount < MAX_CHALLENGE_TRAINERS)
        sChallengeTrainers[sChallengeTrainerCount++] = trainerId;
}

void ChallengeReset_OnMapTransition(const struct MapHeader *from, const struct MapHeader *to)
{
    u8 i;
    bool8 stayingInChallenge;

    if (!sChallengeActive || !ChallengeResetEnabled())
    {
        if (!ChallengeResetEnabled())
            ClearChallengeState();
        return;
    }

    // Floors/maps that share the same named cave section are one challenge.
    // Gym rooms are likewise treated as one challenge while battleType remains GYM.
    stayingInChallenge = IsChallengeMap(to)
                      && to->regionMapSectionId == sChallengeMapSection
                      && ((sChallengeIsGym && to->battleType == MAP_BATTLE_SCENE_GYM)
                       || (!sChallengeIsGym && to->cave));

    if (stayingInChallenge)
        return;

    // If a badge was earned during this gym visit, the gym is complete and
    // its defeated trainers stay defeated. Otherwise leaving resets the visit.
    if (!(sChallengeIsGym && CountBadges() > sChallengeBadgeCountAtStart))
    {
        for (i = 0; i < sChallengeTrainerCount; i++)
            ClearTrainerFlag(sChallengeTrainers[i]);
    }

    ClearChallengeState();
}
