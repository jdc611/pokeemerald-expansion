#ifndef GUARD_CAPS_H
#define GUARD_CAPS_H

#if B_EXP_CAP_TYPE != EXP_CAP_NONE && B_EXP_CAP_TYPE != EXP_CAP_HARD && B_EXP_CAP_TYPE != EXP_CAP_SOFT
#error "Invalid choice for B_EXP_CAP_TYPE, must be of [EXP_CAP_NONE, EXP_CAP_HARD, EXP_CAP_SOFT]"
#endif

#if B_EXP_CAP_TYPE == EXP_CAP_HARD || B_EXP_CAP_TYPE == EXP_CAP_SOFT
#if B_LEVEL_CAP_TYPE != LEVEL_CAP_FLAG_LIST && B_LEVEL_CAP_TYPE != LEVEL_CAP_VARIABLE
#error "Invalid choice for B_LEVEL_CAP_TYPE, must be of [LEVEL_CAP_FLAG_LIST, LEVEL_CAP_VARIABLE]"
#endif
#if B_LEVEL_CAP_TYPE == LEVEL_CAP_VARIABLE && B_LEVEL_CAP_VARIABLE == 0
#error "B_LEVEL_CAP_TYPE set to LEVEL_CAP_VARIABLE, but no variable chosen for B_LEVEL_CAP_VARIABLE, set B_LEVEL_CAP_VARIABLE to a valid event variable"
#endif
#endif

#if B_EV_CAP_TYPE != EV_CAP_NONE && B_EV_CAP_TYPE != EV_CAP_FLAG_LIST && B_EV_CAP_TYPE != EV_CAP_VARIABLE && B_EV_CAP_TYPE != EV_CAP_NO_GAIN
#error "Invalid choice for B_EV_CAP_TYPE, must be one of [EV_CAP_NONE, EV_CAP_FLAG_LIST, EV_CAP_VARIABLE, EV_CAP_NO_GAIN]"
#endif

// start_menu.c currently uses the expansion's legacy player-party aliases for
// Train to Cap. They are still functional, but marked deprecated upstream.
// Keep that warning from becoming a -Werror build failure until the helper is
// migrated fully to gParties[B_TRAINER_PLAYER].
#pragma GCC diagnostic ignored "-Wdeprecated-declarations"

u32 GetCurrentLevelCap(void);
u32 GetSoftLevelCapExpValue(u32 level, u32 expValue);
u32 GetCurrentEVCap(void);

// Player-facing level-cap and Minimal Grinding Mode helpers.
bool32 IsMinimalGrindingMode(void);
void ApplyMinimalGrindingModeToMon(struct Pokemon *mon);
void ApplyMinimalGrindingModeToParty(void);

#endif /* GUARD_CAPS_H */
