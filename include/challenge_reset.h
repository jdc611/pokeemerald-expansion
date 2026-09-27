#ifndef GUARD_CHALLENGE_RESET_H
#define GUARD_CHALLENGE_RESET_H

bool8 ChallengeReset_BlocksRecoveryTools(void);
bool8 ChallengeReset_ShouldIgnoreTrainerFlag(u16 trainerFlag);
void ChallengeReset_RecordTrainerFlag(u16 trainerFlag);
void ChallengeReset_OnMapLoaded(void);
void ChallengeReset_OnMapTransition(const struct MapHeader *from, const struct MapHeader *to, u16 fromMap, s16 x, s16 y);

#endif
