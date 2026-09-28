EverGrandeCity_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, EverGrandeCity_OnTransition
	.byte 0

EverGrandeCity_OnTransition:
	call_if_set FLAG_SYS_WEATHER_CTRL, Common_EventScript_SetAbnormalWeather
	end

EverGrandeCity_EventScript_VictoryRoadSign::
	msgbox EverGrandeCity_Text_EnteringVictoryRoad, MSGBOX_SIGN
	end

EverGrandeCity_EventScript_CitySign::
	msgbox EverGrandeCity_Text_CitySign, MSGBOX_SIGN
	end

EverGrandeCity_EventScript_PokemonLeagueSign::
	msgbox EverGrandeCity_Text_EnteringPokemonLeague, MSGBOX_SIGN
	end


EverGrandeCity_EventScript_JackObject::
	end

EverGrandeCity_EventScript_JackLeagueGate::
	lockall
	goto_if_set FLAG_HIDE_JACK_LEAGUE, EverGrandeCity_EventScript_JackLeagueGateDone
	applymovement OBJ_EVENT_ID_PLAYER, EverGrandeCity_Movement_JackStopsPlayer
	waitmovement 0
	applymovement 1, EverGrandeCity_Movement_JackApproaches
	waitmovement 0
	msgbox EverGrandeCity_Text_JackLeagueIntro, MSGBOX_DEFAULT
	trainerbattle_no_intro TRAINER_JACK, EverGrandeCity_Text_JackDefeat
	msgbox EverGrandeCity_Text_JackAfterBattle, MSGBOX_DEFAULT
	applymovement 1, EverGrandeCity_Movement_JackLeaves
	waitmovement 0
	removeobject 1
EverGrandeCity_EventScript_JackLeagueGateDone:
	setvar VAR_TEMP_2, 1
	releaseall
	end

EverGrandeCity_Movement_JackStopsPlayer:
	walk_down
	step_end

EverGrandeCity_Movement_JackApproaches:
	walk_down
	walk_down
	step_end

EverGrandeCity_Movement_JackLeaves:
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	walk_down
	step_end

EverGrandeCity_Text_JackLeagueIntro:
	.string "Oh--hey! Hope you've enjoyed the\n"
	.string "chaos so far...\p"
	.string "So before you head in there, I want\n"
	.string "to see what kind of chaos you came\n"
	.string "up with.\p"
	.string "How about one last battle?$"

EverGrandeCity_Text_JackDefeat:
	.string "Now that's some chaos.$"

EverGrandeCity_Text_JackAfterBattle:
	.string "Go finish this.$"

EverGrandeCity_EventScript_SetVisitedEverGrande::
	setflag FLAG_VISITED_EVER_GRANDE_CITY
	setvar VAR_TEMP_1, 1
	end

EverGrandeCity_Text_EnteringVictoryRoad:
	.string "ENTERING VICTORY ROAD$"

EverGrandeCity_Text_EnteringPokemonLeague:
	.string "ENTERING POKéMON LEAGUE\n"
	.string "CENTER GATE$"

EverGrandeCity_Text_CitySign:
	.string "EVER GRANDE CITY\p"
	.string "“The paradise of flowers, the sea,\n"
	.string "and POKéMON.”$"

