#ifndef GUARD_CHALLENGE_RESET_H
#define GUARD_CHALLENGE_RESET_H

void ChallengeReset_RecordTrainer(u16 trainerId);
void ChallengeReset_OnMapTransition(const struct MapHeader *from, const struct MapHeader *to);

#endif
