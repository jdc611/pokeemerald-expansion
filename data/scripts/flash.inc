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
	setvar VAR_0x8004, 1
	animateflash 1
	setflashlevel VAR_0x8004
	setflag FLAG_SYS_USE_FLASH
	releaseall
	end

Text_AutoUsedFlash:
	.string "{PLAYER} used FLASH!$"
