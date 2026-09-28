#include "global.h"
#include "challenge_reset.h"
#include "battle_setup.h"
#include "event_data.h"
#include "run_settings.h"
#include "constants/flags.h"
#include "constants/map_types.h"
#include "constants/maps.h"
#include "constants/trainers.h"

#define MAX_CHALLENGE_TRAINERS 64

EWRAM_DATA static u16 sChallengeTrainerFlags[MAX_CHALLENGE_TRAINERS] = {0};
EWRAM_DATA static u8 sChallengeTrainerCount = 0;
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

static bool8 IsHoennGymMap(u16 mapId)
{
    switch (mapId)
    {
    case MAP_RUSTBORO_CITY_GYM:
    case MAP_DEWFORD_TOWN_GYM:
    case MAP_MAUVILLE_CITY_GYM:
    case MAP_LAVARIDGE_TOWN_GYM_1F:
    case MAP_LAVARIDGE_TOWN_GYM_B1F:
    case MAP_PETALBURG_CITY_GYM:
    case MAP_FORTREE_CITY_GYM:
    case MAP_MOSSDEEP_CITY_GYM:
    case MAP_SOOTOPOLIS_CITY_GYM_1F:
    case MAP_SOOTOPOLIS_CITY_GYM_B1F:
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

static bool8 IsGymCompleted(mapsec_u16_t section)
{
    // Use the leader-defeated story flags, not badge ownership. Debug/test
    // helpers intentionally grant badges for obedience and field-move access,
    // so badge flags are not reliable evidence that a gym attempt is complete.
    switch (section)
    {
    case MAPSEC_RUSTBORO_CITY: return FlagGet(FLAG_DEFEATED_RUSTBORO_GYM);
    case MAPSEC_DEWFORD_TOWN: return FlagGet(FLAG_DEFEATED_DEWFORD_GYM);
    case MAPSEC_MAUVILLE_CITY: return FlagGet(FLAG_DEFEATED_MAUVILLE_GYM);
    case MAPSEC_LAVARIDGE_TOWN: return FlagGet(FLAG_DEFEATED_LAVARIDGE_GYM);
    case MAPSEC_PETALBURG_CITY: return FlagGet(FLAG_DEFEATED_PETALBURG_GYM);
    case MAPSEC_FORTREE_CITY: return FlagGet(FLAG_DEFEATED_FORTREE_GYM);
    case MAPSEC_MOSSDEEP_CITY: return FlagGet(FLAG_DEFEATED_MOSSDEEP_GYM);
    case MAPSEC_SOOTOPOLIS_CITY: return FlagGet(FLAG_DEFEATED_SOOTOPOLIS_GYM);
    default: return FALSE;
    }
}


static void ClearGymTrainerFlags(mapsec_u16_t section)
{
#define CLEAR_TRAINER(trainer) FlagClear(TRAINER_FLAGS_START + (trainer))
    switch (section)
    {
    case MAPSEC_RUSTBORO_CITY:
        CLEAR_TRAINER(TRAINER_JOSH); CLEAR_TRAINER(TRAINER_TOMMY); CLEAR_TRAINER(TRAINER_MARC); break;
    case MAPSEC_DEWFORD_TOWN:
        CLEAR_TRAINER(TRAINER_TAKAO); CLEAR_TRAINER(TRAINER_JOCELYN); CLEAR_TRAINER(TRAINER_LAURA); CLEAR_TRAINER(TRAINER_BRENDEN); CLEAR_TRAINER(TRAINER_CRISTIAN); CLEAR_TRAINER(TRAINER_LILITH); break;
    case MAPSEC_MAUVILLE_CITY:
        CLEAR_TRAINER(TRAINER_KIRK); CLEAR_TRAINER(TRAINER_SHAWN); CLEAR_TRAINER(TRAINER_BEN); CLEAR_TRAINER(TRAINER_VIVIAN); CLEAR_TRAINER(TRAINER_ANGELO); break;
    case MAPSEC_LAVARIDGE_TOWN:
        CLEAR_TRAINER(TRAINER_COLE); CLEAR_TRAINER(TRAINER_AXLE); CLEAR_TRAINER(TRAINER_KEEGAN); CLEAR_TRAINER(TRAINER_GERALD); CLEAR_TRAINER(TRAINER_DANIELLE); CLEAR_TRAINER(TRAINER_JACE); CLEAR_TRAINER(TRAINER_JEFF); CLEAR_TRAINER(TRAINER_ELI); break;
    case MAPSEC_PETALBURG_CITY:
        CLEAR_TRAINER(TRAINER_RANDALL); CLEAR_TRAINER(TRAINER_PARKER); CLEAR_TRAINER(TRAINER_GEORGE); CLEAR_TRAINER(TRAINER_BERKE); CLEAR_TRAINER(TRAINER_MARY); CLEAR_TRAINER(TRAINER_ALEXIA); CLEAR_TRAINER(TRAINER_JODY); break;
    case MAPSEC_FORTREE_CITY:
        CLEAR_TRAINER(TRAINER_JARED); CLEAR_TRAINER(TRAINER_FLINT); CLEAR_TRAINER(TRAINER_ASHLEY); CLEAR_TRAINER(TRAINER_EDWARDO); CLEAR_TRAINER(TRAINER_HUMBERTO); CLEAR_TRAINER(TRAINER_DARIUS); break;
    case MAPSEC_MOSSDEEP_CITY:
        CLEAR_TRAINER(TRAINER_PRESTON); CLEAR_TRAINER(TRAINER_VIRGIL); CLEAR_TRAINER(TRAINER_BLAKE); CLEAR_TRAINER(TRAINER_HANNAH); CLEAR_TRAINER(TRAINER_SAMANTHA); CLEAR_TRAINER(TRAINER_MAURA); CLEAR_TRAINER(TRAINER_SYLVIA); CLEAR_TRAINER(TRAINER_NATE); CLEAR_TRAINER(TRAINER_KATHLEEN); CLEAR_TRAINER(TRAINER_CLIFFORD); CLEAR_TRAINER(TRAINER_MACEY); CLEAR_TRAINER(TRAINER_NICHOLAS); break;
    case MAPSEC_SOOTOPOLIS_CITY:
        CLEAR_TRAINER(TRAINER_ANDREA); CLEAR_TRAINER(TRAINER_CRISSY); CLEAR_TRAINER(TRAINER_BRIANNA); CLEAR_TRAINER(TRAINER_CONNIE); CLEAR_TRAINER(TRAINER_BRIDGET); CLEAR_TRAINER(TRAINER_OLIVIA); CLEAR_TRAINER(TRAINER_TIFFANY); CLEAR_TRAINER(TRAINER_BETHANY); CLEAR_TRAINER(TRAINER_ANNIKA); CLEAR_TRAINER(TRAINER_DAPHNE); break;
    }
#undef CLEAR_TRAINER
}

static void ClearChallengeState(void)
{
    sChallengeTrainerCount = 0;
    sChallengeActive = FALSE;
    sChallengeIsGym = FALSE;
}

bool8 ChallengeReset_ShouldIgnoreTrainerFlag(u16 trainerFlag)
{
    u8 i;

    if (!ChallengeResetEnabled()
     || gMapHeader.battleType != MAP_BATTLE_SCENE_GYM
     || IsGymCompleted(gMapHeader.regionMapSectionId))
        return FALSE;

    // A defeated flag from a previous unfinished gym visit must not suppress
    // trainer sight. Trainers defeated during THIS visit remain defeated until
    // the player leaves, because RecordTrainerFlag stores them in this list.
    for (i = 0; i < sChallengeTrainerCount; i++)
        if (sChallengeTrainerFlags[i] == trainerFlag)
            return FALSE;

    return TRUE;
}

void ChallengeReset_RecordTrainerFlag(u16 trainerFlag)
{
    u8 i;

    if (!ChallengeResetEnabled() || !IsChallengeMap(&gMapHeader))
        return;

    if (!sChallengeActive)
    {
        sChallengeActive = TRUE;
        sChallengeMapSection = gMapHeader.regionMapSectionId;
        sChallengeIsGym = (gMapHeader.battleType == MAP_BATTLE_SCENE_GYM);
        sChallengeTrainerCount = 0;
    }

    for (i = 0; i < sChallengeTrainerCount; i++)
        if (sChallengeTrainerFlags[i] == trainerFlag)
            return;

    if (sChallengeTrainerCount < MAX_CHALLENGE_TRAINERS)
        sChallengeTrainerFlags[sChallengeTrainerCount++] = trainerFlag;
}

void ChallengeReset_ForceCurrentGymFresh(void)
{
    if (!ChallengeResetEnabled()
     || gMapHeader.battleType != MAP_BATTLE_SCENE_GYM
     || IsGymCompleted(gMapHeader.regionMapSectionId))
        return;

    // Script-level gym-entry fallback. MAP_SCRIPT_ON_TRANSITION runs on the
    // actual destination map before the player can move, so this does not
    // depend on the overworld warp lifecycle hooks that proved unreliable.
    ClearGymTrainerFlags(gMapHeader.regionMapSectionId);
    sChallengeTrainerCount = 0;
    sChallengeActive = TRUE;
    sChallengeMapSection = gMapHeader.regionMapSectionId;
    sChallengeIsGym = TRUE;
}

void ChallengeReset_OnMapLoaded(void)
{
    if (!ChallengeResetEnabled())
        return;

    // This is the authoritative gym reset point. LoadCurrentMapData has
    // already installed the destination as gMapHeader, so there is no
    // transition/destination ambiguity. Unfinished Hard/Nuzlocke gyms begin
    // every visit with their regular trainer flags clear; earned badges make
    // that completion permanent.
    if (gMapHeader.battleType == MAP_BATTLE_SCENE_GYM
     && !IsGymCompleted(gMapHeader.regionMapSectionId))
    {
        // Every physical gym load is a new unfinished attempt. Reset both the
        // persistent trainer flags and the in-memory per-visit list here,
        // after the destination map is authoritative and before field play.
        ClearGymTrainerFlags(gMapHeader.regionMapSectionId);
        sChallengeTrainerCount = 0;
        sChallengeActive = TRUE;
        sChallengeMapSection = gMapHeader.regionMapSectionId;
        sChallengeIsGym = TRUE;
    }
}

void ChallengeReset_OnMapTransition(const struct MapHeader *from, const struct MapHeader *to, u16 fromMap, s16 x, s16 y)
{
    u8 i;
    bool8 stayingInChallenge;

    if (!ChallengeResetEnabled())
    {
        ClearChallengeState();
        return;
    }

    // Make gym reset authoritative on ENTRY. If the player has not earned
    // this gym's badge, its regular trainers are fresh every time the gym is
    // entered. Once the badge exists, their defeated flags are preserved.
    if (to->battleType == MAP_BATTLE_SCENE_GYM
     && from->battleType != MAP_BATTLE_SCENE_GYM)
    {
        if (!IsGymCompleted(to->regionMapSectionId))
        {
            ClearGymTrainerFlags(to->regionMapSectionId);
        }

    }

    // Gym resets are intentionally stateless. Every transition directly from
    // a gym to a non-gym map is authoritative: without that gym's badge,
    // restore its regular trainers; with the badge, preserve completion.
    if (IsHoennGymMap(fromMap) && to->battleType != MAP_BATTLE_SCENE_GYM)
    {
        if (!IsGymCompleted(from->regionMapSectionId))
            ClearGymTrainerFlags(from->regionMapSectionId);
        ClearChallengeState();
        return;
    }

    // Start the challenge when the player ENTERS the gym/cave, not when a
    // trainer battle happens. This guarantees the later exit is authoritative
    // even if a battle-end path never registered a trainer.
    if (!sChallengeActive)
    {
        if (IsChallengeMap(to))
        {
            sChallengeActive = TRUE;
            sChallengeMapSection = to->regionMapSectionId;
            sChallengeIsGym = (to->battleType == MAP_BATTLE_SCENE_GYM);
            sChallengeTrainerCount = 0;
        }
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

    // Gym completion is authoritative: each gym's own badge flag is set by
    // the leader's post-battle script before the player can leave. Completed
    // gyms keep their trainer flags; unfinished gyms are reset below.
    if (sChallengeIsGym && IsGymCompleted(sChallengeMapSection))
    {
        ClearChallengeState();
        return;
    }

    if (sChallengeIsGym)
    {
        // Use the same canonical gym-trainer roster that the badge scripts
        // mark complete. This makes unfinished-gym resets independent of
        // which battle-end path recorded the trainer.
        ClearGymTrainerFlags(sChallengeMapSection);
    }
    else
    {
        for (i = 0; i < sChallengeTrainerCount; i++)
            FlagClear(sChallengeTrainerFlags[i]);
    }

    ClearChallengeState();
}
