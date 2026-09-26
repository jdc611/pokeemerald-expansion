EventScript_UseSurf::
	lockall
	@ Chaos QoL: A on fishable water gives one compact action menu.
	multichoice 0, 0, MULTI_SURF_FISH_BACK, FALSE
	switch VAR_RESULT
	case 0, EventScript_UseSurfSelected
	case 1, EventScript_UseFishSelected
	goto EventScript_ReleaseUseSurf

EventScript_UseSurfSelected::
	checkfieldmove FIELD_MOVE_SURF, TRUE
	goto_if_eq VAR_RESULT, PARTY_SIZE, EventScript_ReleaseUseSurf
	setfieldeffectargument 0, PARTY_SIZE
	setfieldeffectargument 1, ITEM_HM_SURF
	msgbox gText_PlayerUsedSurf, MSGBOX_DEFAULT
	dofieldeffect FLDEFF_USE_SURF
	goto EventScript_ReleaseUseSurf

EventScript_UseFishSelected::
	@ Fully tear down the water interaction before fishing takes ownership.
	@ StartFishingWithBestOwnedRod deliberately queues fishing for the next
	@ field frame so the multichoice window/script cannot overlap its dialog.
	closemessage
	releaseall
	callnative StartFishingWithSelectedRod
	end

EventScript_ReleaseUseSurf::
	releaseall
EventScript_EndUseSurf::
	end

EventScript_CurrentTooFast::
	lockall
	checkfieldmove FIELD_MOVE_SURF
	goto_if_eq VAR_RESULT, FALSE, EventScript_CurrentTooFastEndMsg
	playse SE_SELECT
	msgbox Text_CurrentTooFast
EventScript_CurrentTooFastEndMsg::
	releaseall
	end
