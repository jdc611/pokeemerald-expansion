#include "global.h"
#include "challenge_reset.h"
#include "battle_setup.h"
#include "event_data.h"
#include "run_settings.h"
#include "constants/flags.h"
#include "constants/map_types.h"
#include "constants/maps.h"

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

static bool8 IsCaveCompleted(mapsec_u16_t section);
static bool8 IsSupportedChallengeCave(mapsec_u16_t section);

bool8 ChallengeReset_BlocksRecoveryTools(void)
{
    if (!ChallengeResetEnabled())
        return FALSE;

    // Recovery tools are unavailable throughout Hard/Nuzlocke gyms and active
    // cave challenges. Completed caves return to normal on later visits.
    if (gMapHeader.battleType == MAP_BATTLE_SCENE_GYM)
        return TRUE;

    return gMapHeader.cave
        && IsSupportedChallengeCave(gMapHeader.regionMapSectionId)
        && !IsCaveCompleted(gMapHeader.regionMapSectionId);
}

static bool8 IsCaveCompleted(mapsec_u16_t section)
{
    if (section >= 256)
        return FALSE;
    return (gSaveBlock3Ptr->challengeCaveCompleted[section >> 3] & (1 << (section & 7))) != 0;
}

static void MarkCaveCompleted(mapsec_u16_t section)
{
    if (section < 256)
        gSaveBlock3Ptr->challengeCaveCompleted[section >> 3] |= (1 << (section & 7));
}

static bool8 IsSupportedChallengeCave(mapsec_u16_t section)
{
    switch (section)
    {
    case MAPSEC_RUSTURF_TUNNEL:
    case MAPSEC_FIERY_PATH:
    case MAPSEC_METEOR_FALLS:
    case MAPSEC_VICTORY_ROAD:
        return TRUE;
    default:
        return FALSE;
    }
}

static bool8 IsChallengeMap(const struct MapHeader *map)
{
    if (map->battleType == MAP_BATTLE_SCENE_GYM)
        return TRUE;
    return map->cave
        && IsSupportedChallengeCave(map->regionMapSectionId)
        && !IsCaveCompleted(map->regionMapSectionId);
}

// Only the intended progression-side exit completes a cave challenge.
// Coordinates are the source warp tile, so backing out through the entrance,
// Escape Rope/Dig/whiteout, and alternate exits cannot accidentally complete it.
static bool8 IsCaveCompletionExit(mapsec_u16_t section, u16 fromMap, s16 x, s16 y)
{
    switch (section)
    {
    case MAPSEC_RUSTURF_TUNNEL:
        return fromMap == MAP_RUSTURF_TUNNEL && x == 29 && y == 16;
    case MAPSEC_FIERY_PATH:
        return fromMap == MAP_FIERY_PATH && x == 26 && y == 4;
    case MAPSEC_METEOR_FALLS:
        return fromMap == MAP_METEOR_FALLS_1F_1R && x == 6 && y == 39;
    case MAPSEC_VICTORY_ROAD:
        return fromMap == MAP_VICTORY_ROAD_1F && x == 39 && y == 5;
    default:
        return FALSE;
    }
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

void ChallengeReset_OnMapTransition(const struct MapHeader *from, const struct MapHeader *to, u16 fromMap, s16 x, s16 y)
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

    // A cave only becomes permanently complete through its designated
    // progression exit. Once complete, its trainer flags are left alone on
    // all future visits.
    if (!sChallengeIsGym && IsCaveCompletionExit(sChallengeMapSection, fromMap, x, y))
    {
        MarkCaveCompleted(sChallengeMapSection);
        ClearChallengeState();
        return;
    }

    // If a badge was earned during this gym visit, the gym is complete and
    // its defeated trainers stay defeated. If the badge script runs after the
    // exit transition, defer the decision until the next map transition so the
    // post-battle script has had a chance to award the badge.
    if (sChallengeIsGym)
    {
        if (CountBadges() > sChallengeBadgeCountAtStart)
        {
            ClearChallengeState();
            return;
        }

        // If the player leaves an unfinished gym, reset its defeated trainers
        // immediately. A legitimately completed gym already returned above
        // because its badge count increased before the player can exit.
    }

    for (i = 0; i < sChallengeTrainerCount; i++)
        ClearTrainerFlag(sChallengeTrainers[i]);

    ClearChallengeState();
}
