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

    dynmultipush Debug_EventScript_ChangeNature_Text_Hardy, 0
    dynmultipush Debug_EventScript_ChangeNature_Text_Lonely, 1
    dynmultipush Debug_EventScript_ChangeNature_Text_Brave, 2
    dynmultipush Debug_EventScript_ChangeNature_Text_Adamant, 3
    dynmultipush Debug_EventScript_ChangeNature_Text_Naughty, 4
    dynmultipush Debug_EventScript_ChangeNature_Text_Bold, 5
    dynmultipush Debug_EventScript_ChangeNature_Text_Docile, 6
    dynmultipush Debug_EventScript_ChangeNature_Text_Relaxed, 7
    dynmultipush Debug_EventScript_ChangeNature_Text_Impish, 8
    dynmultipush Debug_EventScript_ChangeNature_Text_Lax, 9
    dynmultipush Debug_EventScript_ChangeNature_Text_Timid, 10
    dynmultipush Debug_EventScript_ChangeNature_Text_Hasty, 11
    dynmultipush Debug_EventScript_ChangeNature_Text_Serious, 12
    dynmultipush Debug_EventScript_ChangeNature_Text_Jolly, 13
    dynmultipush Debug_EventScript_ChangeNature_Text_Naive, 14
    dynmultipush Debug_EventScript_ChangeNature_Text_Modest, 15
    dynmultipush Debug_EventScript_ChangeNature_Text_Mild, 16
    dynmultipush Debug_EventScript_ChangeNature_Text_Quiet, 17
    dynmultipush Debug_EventScript_ChangeNature_Text_Bashful, 18
    dynmultipush Debug_EventScript_ChangeNature_Text_Rash, 19
    dynmultipush Debug_EventScript_ChangeNature_Text_Calm, 20
    dynmultipush Debug_EventScript_ChangeNature_Text_Gentle, 21
    dynmultipush Debug_EventScript_ChangeNature_Text_Sassy, 22
    dynmultipush Debug_EventScript_ChangeNature_Text_Careful, 23
    dynmultipush Debug_EventScript_ChangeNature_Text_Quirky, 24
    dynmultistack 0, 0, TRUE, 7, FALSE, 0, NULL

    switch VAR_RESULT
    case MULTI_B_PRESSED, EventScript_ChangeNature_Close
    special SetHiddenNature

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
        special SetSelectedMonGender
    goto_if_eq VAR_RESULT, 2, EventScript_ChangeGender_Genderless
    goto_if_eq VAR_RESULT, 3, EventScript_ChangeGender_MaleOnly
    goto_if_eq VAR_RESULT, 4, EventScript_ChangeGender_FemaleOnly
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

EventScript_Text_Genderless:
    .string "This Pokémon has no gender.$"

EventScript_Text_MaleOnly:
    .string "This Pokémon can only be male.$"

EventScript_Text_FemaleOnly:
    .string "This Pokémon can only be female.$"
