#ifndef GUARD_RUN_SETTINGS_H
#define GUARD_RUN_SETTINGS_H

enum RunWildMode
{
    RUN_WILD_NORMAL,
    RUN_WILD_RANDOM,
    RUN_WILD_SCALED,
};

enum RunStarterMode
{
    RUN_STARTER_NORMAL,
    RUN_STARTER_CHOOSE,
    RUN_STARTER_RANDOM,
};

enum RunRivalMode
{
    RUN_RIVAL_NORMAL,
    RUN_RIVAL_CHOOSE,
    RUN_RIVAL_RANDOM,
    RUN_RIVAL_COUNTER,
};

enum RunFilterMode
{
    RUN_FILTER_NONE,
    RUN_FILTER_TYPE,
    RUN_FILTER_ABILITY,
    RUN_FILTER_GENERATION,
};

// Run setup needs lightweight species-data access while validating filters.
// pokeemerald-expansion stores the normal abilities in slots 0/1 and the
// hidden ability in slot 2.
#ifndef ABILITY_SLOT_HIDDEN
#define ABILITY_SLOT_HIDDEN 2
#endif

static inline enum Type GetSpeciesType(enum Species species, u32 slot)
{
    return gSpeciesInfo[species].types[slot];
}

static inline enum Ability GetSpeciesAbility(enum Species species, u32 slot)
{
    return gSpeciesInfo[species].abilities[slot];
}

#endif // GUARD_RUN_SETTINGS_H
