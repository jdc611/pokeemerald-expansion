#ifndef GUARD_CHALLENGE_RESET_H
#define GUARD_CHALLENGE_RESET_H

bool8 ChallengeReset_BlocksRecoveryTools(void);
void ChallengeReset_RecordTrainer(u16 trainerId);
void ChallengeReset_OnMapTransition(const struct MapHeader *from, const struct MapHeader *to, u16 fromMap, s16 x, s16 y);

#endif
