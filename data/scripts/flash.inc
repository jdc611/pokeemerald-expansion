EventScript_UseFlash::
	animateflash 1
	setflashlevel 1
	releaseall
	end

// Automatic HM-owned Flash, shown once on the first step in an unlit cave.
EventScript_AutoUseFlash::
	lockall
	setfieldeffectargument 0, PARTY_SIZE
	setfieldeffectargument 1, ITEM_HM_FLASH
	msgbox Text_AutoUsedFlash, MSGBOX_DEFAULT
	closemessage
	dofieldeffect FLDEFF_FIELD_MOVE_SHOW_MON_INIT
	waitstate
	// Flash level 0 is full brightness. Run the animation directly here and
	// let its native wait task re-enable the script when the transition ends.
	animateflash 0
	setflashlevel 0
	setflag FLAG_SYS_USE_FLASH
	releaseall
	end

Text_AutoUsedFlash:
	.string "{PLAYER} used FLASH!$"
