EventScript_PC::
	lockall
	setvar VAR_0x8004, PC_LOCATION_OTHER
	special DoPCTurnOnEffect
	playse SE_PC_ON
	msgbox Text_BootUpPC, MSGBOX_DEFAULT
	goto EventScript_PCMainMenu
	end

EventScript_PCMainMenu::
	message gText_WhichPCShouldBeAccessed
	waitmessage
	special ScriptMenu_CreatePCMultichoice
	goto EventScript_AccessPC
	end

EventScript_AccessPC::
	switch VAR_RESULT
	case 0, EventScript_AccessPokemonStorage
	case 1, EventScript_AccessPlayersPC
	case 2, EventScript_AccessHallOfFame
	case 3, EventScript_TurnOffPC
	case MULTI_B_PRESSED, EventScript_TurnOffPC
	end

EventScript_AccessPlayersPC::
	playse SE_PC_LOGIN
	msgbox gText_AccessedPlayersPC, MSGBOX_DEFAULT
	special PlayerPC
	goto EventScript_PCMainMenu
	end

EventScript_AccessPokemonStorage::
	playse SE_PC_LOGIN
	call_if_unset FLAG_SYS_PC_LANETTE, EventScript_AccessSomeonesPC
	call_if_set FLAG_SYS_PC_LANETTE, EventScript_AccessLanettesPC
	msgbox gText_StorageSystemOpened, MSGBOX_DEFAULT
	special ShowPokemonStorageSystemPC
	goto EventScript_PCMainMenu
	end

EventScript_AccessSomeonesPC::
	msgbox gText_AccessedSomeonesPC, MSGBOX_DEFAULT
	return

EventScript_AccessLanettesPC::
#if IS_FRLG
	msgbox gText_AccessedBillsPC, MSGBOX_DEFAULT
#else
	msgbox gText_AccessedLanettesPC, MSGBOX_DEFAULT
#endif
	return

EventScript_TurnOffPC::
	setvar VAR_0x8004, PC_LOCATION_OTHER
	playse SE_PC_OFF
	special DoPCTurnOffEffect
	releaseall
	end

EventScript_AccessHallOfFame::
	goto_if_unset FLAG_SYS_GAME_CLEAR, EventScript_TurnOffPC
	playse SE_PC_LOGIN
	special AccessHallOfFamePC
	goto EventScript_AccessPC
	end

EventScript_AccessPokemonBoxLink::
	playse SE_PC_LOGIN
	msgbox gText_StorageSystemOpened, MSGBOX_DEFAULT
	special ShowPokemonStorageSystemPC
	goto EventScript_TurnOffPC
	end

EventScript_UsePokeVial::
    lockall
    special HealPlayerParty
    playse SE_USE_ITEM
    msgbox gText_MonsHealed, MSGBOX_DEFAULT
    releaseall
    end

EventScript_ChangeNature::
    special ChoosePartyMon
    waitstate
    goto_if_ge VAR_0x8004, PARTY_SIZE, EventScript_ChangeNature_Close
    specialvar VAR_RESULT, ScriptGetPartyMonSpecies
    goto_if_eq VAR_RESULT, SPECIES_EGG, EventScript_ChangeNature_Close

    dynmultipush EventScript_ChangeNature_Text_Hardy, 0
    dynmultipush EventScript_ChangeNature_Text_Lonely, 1
    dynmultipush EventScript_ChangeNature_Text_Brave, 2
    dynmultipush EventScript_ChangeNature_Text_Adamant, 3
    dynmultipush EventScript_ChangeNature_Text_Naughty, 4
    dynmultipush EventScript_ChangeNature_Text_Bold, 5
    dynmultipush EventScript_ChangeNature_Text_Docile, 6
    dynmultipush EventScript_ChangeNature_Text_Relaxed, 7
    dynmultipush EventScript_ChangeNature_Text_Impish, 8
    dynmultipush EventScript_ChangeNature_Text_Lax, 9
    dynmultipush EventScript_ChangeNature_Text_Timid, 10
    dynmultipush EventScript_ChangeNature_Text_Hasty, 11
    dynmultipush EventScript_ChangeNature_Text_Serious, 12
    dynmultipush EventScript_ChangeNature_Text_Jolly, 13
    dynmultipush EventScript_ChangeNature_Text_Naive, 14
    dynmultipush EventScript_ChangeNature_Text_Modest, 15
    dynmultipush EventScript_ChangeNature_Text_Mild, 16
    dynmultipush EventScript_ChangeNature_Text_Quiet, 17
    dynmultipush EventScript_ChangeNature_Text_Bashful, 18
    dynmultipush EventScript_ChangeNature_Text_Rash, 19
    dynmultipush EventScript_ChangeNature_Text_Calm, 20
    dynmultipush EventScript_ChangeNature_Text_Gentle, 21
    dynmultipush EventScript_ChangeNature_Text_Sassy, 22
    dynmultipush EventScript_ChangeNature_Text_Careful, 23
    dynmultipush EventScript_ChangeNature_Text_Quirky, 24
    dynmultistack 0, 0, FALSE, 7, FALSE, 0, NULL

    switch VAR_RESULT
    case MULTI_B_PRESSED, EventScript_ChangeNature_Close
    copyvar VAR_0x8005, VAR_RESULT
    special SetHiddenNature
    switch VAR_0x8005
    case 0, EventScript_ChangeNature_Confirm_Hardy
    case 1, EventScript_ChangeNature_Confirm_Lonely
    case 2, EventScript_ChangeNature_Confirm_Brave
    case 3, EventScript_ChangeNature_Confirm_Adamant
    case 4, EventScript_ChangeNature_Confirm_Naughty
    case 5, EventScript_ChangeNature_Confirm_Bold
    case 6, EventScript_ChangeNature_Confirm_Docile
    case 7, EventScript_ChangeNature_Confirm_Relaxed
    case 8, EventScript_ChangeNature_Confirm_Impish
    case 9, EventScript_ChangeNature_Confirm_Lax
    case 10, EventScript_ChangeNature_Confirm_Timid
    case 11, EventScript_ChangeNature_Confirm_Hasty
    case 12, EventScript_ChangeNature_Confirm_Serious
    case 13, EventScript_ChangeNature_Confirm_Jolly
    case 14, EventScript_ChangeNature_Confirm_Naive
    case 15, EventScript_ChangeNature_Confirm_Modest
    case 16, EventScript_ChangeNature_Confirm_Mild
    case 17, EventScript_ChangeNature_Confirm_Quiet
    case 18, EventScript_ChangeNature_Confirm_Bashful
    case 19, EventScript_ChangeNature_Confirm_Rash
    case 20, EventScript_ChangeNature_Confirm_Calm
    case 21, EventScript_ChangeNature_Confirm_Gentle
    case 22, EventScript_ChangeNature_Confirm_Sassy
    case 23, EventScript_ChangeNature_Confirm_Careful
    case 24, EventScript_ChangeNature_Confirm_Quirky
    goto EventScript_ChangeNature_Close

EventScript_ChangeNature_Confirm_Hardy::
    msgbox EventScript_Text_NatureChanged_Hardy, MSGBOX_DEFAULT
    goto EventScript_ChangeNature_Close
EventScript_ChangeNature_Confirm_Lonely::
    msgbox EventScript_Text_NatureChanged_Lonely, MSGBOX_DEFAULT
    goto EventScript_ChangeNature_Close
EventScript_ChangeNature_Confirm_Brave::
    msgbox EventScript_Text_NatureChanged_Brave, MSGBOX_DEFAULT
    goto EventScript_ChangeNature_Close
EventScript_ChangeNature_Confirm_Adamant::
    msgbox EventScript_Text_NatureChanged_Adamant, MSGBOX_DEFAULT
    goto EventScript_ChangeNature_Close
EventScript_ChangeNature_Confirm_Naughty::
    msgbox EventScript_Text_NatureChanged_Naughty, MSGBOX_DEFAULT
    goto EventScript_ChangeNature_Close
EventScript_ChangeNature_Confirm_Bold::
    msgbox EventScript_Text_NatureChanged_Bold, MSGBOX_DEFAULT
    goto EventScript_ChangeNature_Close
EventScript_ChangeNature_Confirm_Docile::
    msgbox EventScript_Text_NatureChanged_Docile, MSGBOX_DEFAULT
    goto EventScript_ChangeNature_Close
EventScript_ChangeNature_Confirm_Relaxed::
    msgbox EventScript_Text_NatureChanged_Relaxed, MSGBOX_DEFAULT
    goto EventScript_ChangeNature_Close
EventScript_ChangeNature_Confirm_Impish::
    msgbox EventScript_Text_NatureChanged_Impish, MSGBOX_DEFAULT
    goto EventScript_ChangeNature_Close
EventScript_ChangeNature_Confirm_Lax::
    msgbox EventScript_Text_NatureChanged_Lax, MSGBOX_DEFAULT
    goto EventScript_ChangeNature_Close
EventScript_ChangeNature_Confirm_Timid::
    msgbox EventScript_Text_NatureChanged_Timid, MSGBOX_DEFAULT
    goto EventScript_ChangeNature_Close
EventScript_ChangeNature_Confirm_Hasty::
    msgbox EventScript_Text_NatureChanged_Hasty, MSGBOX_DEFAULT
    goto EventScript_ChangeNature_Close
EventScript_ChangeNature_Confirm_Serious::
    msgbox EventScript_Text_NatureChanged_Serious, MSGBOX_DEFAULT
    goto EventScript_ChangeNature_Close
EventScript_ChangeNature_Confirm_Jolly::
    msgbox EventScript_Text_NatureChanged_Jolly, MSGBOX_DEFAULT
    goto EventScript_ChangeNature_Close
EventScript_ChangeNature_Confirm_Naive::
    msgbox EventScript_Text_NatureChanged_Naive, MSGBOX_DEFAULT
    goto EventScript_ChangeNature_Close
EventScript_ChangeNature_Confirm_Modest::
    msgbox EventScript_Text_NatureChanged_Modest, MSGBOX_DEFAULT
    goto EventScript_ChangeNature_Close
EventScript_ChangeNature_Confirm_Mild::
    msgbox EventScript_Text_NatureChanged_Mild, MSGBOX_DEFAULT
    goto EventScript_ChangeNature_Close
EventScript_ChangeNature_Confirm_Quiet::
    msgbox EventScript_Text_NatureChanged_Quiet, MSGBOX_DEFAULT
    goto EventScript_ChangeNature_Close
EventScript_ChangeNature_Confirm_Bashful::
    msgbox EventScript_Text_NatureChanged_Bashful, MSGBOX_DEFAULT
    goto EventScript_ChangeNature_Close
EventScript_ChangeNature_Confirm_Rash::
    msgbox EventScript_Text_NatureChanged_Rash, MSGBOX_DEFAULT
    goto EventScript_ChangeNature_Close
EventScript_ChangeNature_Confirm_Calm::
    msgbox EventScript_Text_NatureChanged_Calm, MSGBOX_DEFAULT
    goto EventScript_ChangeNature_Close
EventScript_ChangeNature_Confirm_Gentle::
    msgbox EventScript_Text_NatureChanged_Gentle, MSGBOX_DEFAULT
    goto EventScript_ChangeNature_Close
EventScript_ChangeNature_Confirm_Sassy::
    msgbox EventScript_Text_NatureChanged_Sassy, MSGBOX_DEFAULT
    goto EventScript_ChangeNature_Close
EventScript_ChangeNature_Confirm_Careful::
    msgbox EventScript_Text_NatureChanged_Careful, MSGBOX_DEFAULT
    goto EventScript_ChangeNature_Close
EventScript_ChangeNature_Confirm_Quirky::
    msgbox EventScript_Text_NatureChanged_Quirky, MSGBOX_DEFAULT
    goto EventScript_ChangeNature_Close

EventScript_ChangeNature_Close::
    releaseall
    end

EventScript_ChangeGender::
    special ChoosePartyMon
    waitstate
    goto_if_ge VAR_0x8004, PARTY_SIZE, EventScript_ChangeGender_Close
    specialvar VAR_RESULT, ScriptGetPartyMonSpecies
    goto_if_eq VAR_RESULT, SPECIES_EGG, EventScript_ChangeGender_Close
    multichoice 0, 0, MULTI_GENDER, FALSE
    switch VAR_RESULT
    case MULTI_B_PRESSED, EventScript_ChangeGender_Close
    copyvar VAR_0x8005, VAR_RESULT
    special SetSelectedMonGender
    goto_if_eq VAR_RESULT, 2, EventScript_ChangeGender_Genderless
    goto_if_eq VAR_RESULT, 3, EventScript_ChangeGender_MaleOnly
    goto_if_eq VAR_RESULT, 4, EventScript_ChangeGender_FemaleOnly
    goto_if_eq VAR_0x8005, 0, EventScript_ChangeGender_ConfirmMale
    goto EventScript_ChangeGender_ConfirmFemale

EventScript_ChangeGender_ConfirmMale::
    msgbox EventScript_Text_GenderChangedMale, MSGBOX_DEFAULT
    goto EventScript_ChangeGender_Close

EventScript_ChangeGender_ConfirmFemale::
    msgbox EventScript_Text_GenderChangedFemale, MSGBOX_DEFAULT
    goto EventScript_ChangeGender_Close

EventScript_ChangeGender_Genderless::
    msgbox EventScript_Text_Genderless, MSGBOX_DEFAULT
    goto EventScript_ChangeGender_Close

EventScript_ChangeGender_MaleOnly::
    msgbox EventScript_Text_MaleOnly, MSGBOX_DEFAULT
    goto EventScript_ChangeGender_Close

EventScript_ChangeGender_FemaleOnly::
    msgbox EventScript_Text_FemaleOnly, MSGBOX_DEFAULT
    goto EventScript_ChangeGender_Close

EventScript_ChangeGender_Close::
    releaseall
    end

@ Nature picker: red = increased stat, blue = decreased stat.
EventScript_ChangeNature_Text_Hardy:
    .string "Hardy  Neutral$"
EventScript_ChangeNature_Text_Lonely:
    .string "Lonely  {COLOR RED}ATK {UP_ARROW}{COLOR DARK_GRAY} {COLOR BLUE}DEF {DOWN_ARROW}{COLOR DARK_GRAY}$"
EventScript_ChangeNature_Text_Brave:
    .string "Brave  {COLOR RED}ATK {UP_ARROW}{COLOR DARK_GRAY} {COLOR BLUE}SPE {DOWN_ARROW}{COLOR DARK_GRAY}$"
EventScript_ChangeNature_Text_Adamant:
    .string "Adamant  {COLOR RED}ATK {UP_ARROW}{COLOR DARK_GRAY} {COLOR BLUE}SpA {DOWN_ARROW}{COLOR DARK_GRAY}$"
EventScript_ChangeNature_Text_Naughty:
    .string "Naughty  {COLOR RED}ATK {UP_ARROW}{COLOR DARK_GRAY} {COLOR BLUE}SpD {DOWN_ARROW}{COLOR DARK_GRAY}$"
EventScript_ChangeNature_Text_Bold:
    .string "Bold  {COLOR RED}DEF {UP_ARROW}{COLOR DARK_GRAY} {COLOR BLUE}ATK {DOWN_ARROW}{COLOR DARK_GRAY}$"
EventScript_ChangeNature_Text_Docile:
    .string "Docile  Neutral$"
EventScript_ChangeNature_Text_Relaxed:
    .string "Relaxed  {COLOR RED}DEF {UP_ARROW}{COLOR DARK_GRAY} {COLOR BLUE}SPE {DOWN_ARROW}{COLOR DARK_GRAY}$"
EventScript_ChangeNature_Text_Impish:
    .string "Impish  {COLOR RED}DEF {UP_ARROW}{COLOR DARK_GRAY} {COLOR BLUE}SpA {DOWN_ARROW}{COLOR DARK_GRAY}$"
EventScript_ChangeNature_Text_Lax:
    .string "Lax  {COLOR RED}DEF {UP_ARROW}{COLOR DARK_GRAY} {COLOR BLUE}SpD {DOWN_ARROW}{COLOR DARK_GRAY}$"
EventScript_ChangeNature_Text_Timid:
    .string "Timid  {COLOR RED}SPE {UP_ARROW}{COLOR DARK_GRAY} {COLOR BLUE}ATK {DOWN_ARROW}{COLOR DARK_GRAY}$"
EventScript_ChangeNature_Text_Hasty:
    .string "Hasty  {COLOR RED}SPE {UP_ARROW}{COLOR DARK_GRAY} {COLOR BLUE}DEF {DOWN_ARROW}{COLOR DARK_GRAY}$"
EventScript_ChangeNature_Text_Serious:
    .string "Serious  Neutral$"
EventScript_ChangeNature_Text_Jolly:
    .string "Jolly  {COLOR RED}SPE {UP_ARROW}{COLOR DARK_GRAY} {COLOR BLUE}SpA {DOWN_ARROW}{COLOR DARK_GRAY}$"
EventScript_ChangeNature_Text_Naive:
    .string "Naive  {COLOR RED}SPE {UP_ARROW}{COLOR DARK_GRAY} {COLOR BLUE}SpD {DOWN_ARROW}{COLOR DARK_GRAY}$"
EventScript_ChangeNature_Text_Modest:
    .string "Modest  {COLOR RED}SpA {UP_ARROW}{COLOR DARK_GRAY} {COLOR BLUE}ATK {DOWN_ARROW}{COLOR DARK_GRAY}$"
EventScript_ChangeNature_Text_Mild:
    .string "Mild  {COLOR RED}SpA {UP_ARROW}{COLOR DARK_GRAY} {COLOR BLUE}DEF {DOWN_ARROW}{COLOR DARK_GRAY}$"
EventScript_ChangeNature_Text_Quiet:
    .string "Quiet  {COLOR RED}SpA {UP_ARROW}{COLOR DARK_GRAY} {COLOR BLUE}SPE {DOWN_ARROW}{COLOR DARK_GRAY}$"
EventScript_ChangeNature_Text_Bashful:
    .string "Bashful  Neutral$"
EventScript_ChangeNature_Text_Rash:
    .string "Rash  {COLOR RED}SpA {UP_ARROW}{COLOR DARK_GRAY} {COLOR BLUE}SpD {DOWN_ARROW}{COLOR DARK_GRAY}$"
EventScript_ChangeNature_Text_Calm:
    .string "Calm  {COLOR RED}SpD {UP_ARROW}{COLOR DARK_GRAY} {COLOR BLUE}ATK {DOWN_ARROW}{COLOR DARK_GRAY}$"
EventScript_ChangeNature_Text_Gentle:
    .string "Gentle  {COLOR RED}SpD {UP_ARROW}{COLOR DARK_GRAY} {COLOR BLUE}DEF {DOWN_ARROW}{COLOR DARK_GRAY}$"
EventScript_ChangeNature_Text_Sassy:
    .string "Sassy  {COLOR RED}SpD {UP_ARROW}{COLOR DARK_GRAY} {COLOR BLUE}SPE {DOWN_ARROW}{COLOR DARK_GRAY}$"
EventScript_ChangeNature_Text_Careful:
    .string "Careful  {COLOR RED}SpD {UP_ARROW}{COLOR DARK_GRAY} {COLOR BLUE}SpA {DOWN_ARROW}{COLOR DARK_GRAY}$"
EventScript_ChangeNature_Text_Quirky:
    .string "Quirky  Neutral$"

EventScript_Text_NatureChanged_Hardy:
    .string "Nature successfully changed to Hardy!$"
EventScript_Text_NatureChanged_Lonely:
    .string "Nature successfully changed to Lonely!$"
EventScript_Text_NatureChanged_Brave:
    .string "Nature successfully changed to Brave!$"
EventScript_Text_NatureChanged_Adamant:
    .string "Nature successfully changed to Adamant!$"
EventScript_Text_NatureChanged_Naughty:
    .string "Nature successfully changed to Naughty!$"
EventScript_Text_NatureChanged_Bold:
    .string "Nature successfully changed to Bold!$"
EventScript_Text_NatureChanged_Docile:
    .string "Nature successfully changed to Docile!$"
EventScript_Text_NatureChanged_Relaxed:
    .string "Nature successfully changed to Relaxed!$"
EventScript_Text_NatureChanged_Impish:
    .string "Nature successfully changed to Impish!$"
EventScript_Text_NatureChanged_Lax:
    .string "Nature successfully changed to Lax!$"
EventScript_Text_NatureChanged_Timid:
    .string "Nature successfully changed to Timid!$"
EventScript_Text_NatureChanged_Hasty:
    .string "Nature successfully changed to Hasty!$"
EventScript_Text_NatureChanged_Serious:
    .string "Nature successfully changed to Serious!$"
EventScript_Text_NatureChanged_Jolly:
    .string "Nature successfully changed to Jolly!$"
EventScript_Text_NatureChanged_Naive:
    .string "Nature successfully changed to Naive!$"
EventScript_Text_NatureChanged_Modest:
    .string "Nature successfully changed to Modest!$"
EventScript_Text_NatureChanged_Mild:
    .string "Nature successfully changed to Mild!$"
EventScript_Text_NatureChanged_Quiet:
    .string "Nature successfully changed to Quiet!$"
EventScript_Text_NatureChanged_Bashful:
    .string "Nature successfully changed to Bashful!$"
EventScript_Text_NatureChanged_Rash:
    .string "Nature successfully changed to Rash!$"
EventScript_Text_NatureChanged_Calm:
    .string "Nature successfully changed to Calm!$"
EventScript_Text_NatureChanged_Gentle:
    .string "Nature successfully changed to Gentle!$"
EventScript_Text_NatureChanged_Sassy:
    .string "Nature successfully changed to Sassy!$"
EventScript_Text_NatureChanged_Careful:
    .string "Nature successfully changed to Careful!$"
EventScript_Text_NatureChanged_Quirky:
    .string "Nature successfully changed to Quirky!$"

EventScript_Text_GenderChangedMale:
    .string "Gender successfully changed to male!$"

EventScript_Text_GenderChangedFemale:
    .string "Gender successfully changed to female!$"

EventScript_Text_Genderless:
    .string "This Pokémon has no gender.$"

EventScript_Text_MaleOnly:
    .string "This Pokémon can only be male.$"

EventScript_Text_FemaleOnly:
    .string "This Pokémon can only be female.$"
