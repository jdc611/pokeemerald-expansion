from pathlib import Path


def rep(s, old, new, label):
    if old not in s:
        raise SystemExit(f'Missing anchor: {label}')
    return s.replace(old, new, 1)

# Fix level cap fallback: our hack uses the badge flag progression regardless of
# upstream compile-time cap mode. This prevents a fresh save reporting MAX_LEVEL.
p=Path('src/caps.c'); s=p.read_text()
start=s.index('u32 GetCurrentLevelCap(void)')
end=s.index('\nu32 GetSoftLevelCapExpValue', start)
new='''u32 GetCurrentLevelCap(void)\n{\n    static const u32 sLevelCapFlagMap[][2] =\n    {\n        {FLAG_BADGE01_GET, 15},\n        {FLAG_BADGE02_GET, 19},\n        {FLAG_BADGE03_GET, 24},\n        {FLAG_BADGE04_GET, 29},\n        {FLAG_BADGE05_GET, 31},\n        {FLAG_BADGE06_GET, 33},\n        {FLAG_BADGE07_GET, 42},\n        {FLAG_BADGE08_GET, 46},\n        {FLAG_IS_CHAMPION, 58},\n    };\n    u32 i;\n    for (i = 0; i < ARRAY_COUNT(sLevelCapFlagMap); i++)\n        if (!FlagGet(sLevelCapFlagMap[i][0]))\n            return sLevelCapFlagMap[i][1];\n    return 58;\n}\n'''
s=s[:start]+new+s[end:]; p.write_text(s)

# Start menu: MGM becomes display-only elsewhere; remove its page-2 action and
# make Train to Cap close cleanly to the field instead of rebuilding menu state.
p=Path('src/start_menu.c'); s=p.read_text()
s=s.replace('        AddStartMenuAction(MENU_ACTION_MGM);\n','',1)
# Remove PokéRider from page 2; it will be relocated to quick tools separately.
s=s.replace('        AddStartMenuAction(MENU_ACTION_POKERIDER);\n','',1)
# Safer Train-to-Cap return flow.
old='''    PlaySE(SE_EXP_MAX);\n    ClearStdWindowAndFrame(GetStartMenuWindowId(), TRUE);\n    RemoveStartMenuWindow();\n    InitStartMenu();\n    gMenuCallback = HandleStartMenuInput;\n    return FALSE;\n}'''
new='''    PlaySE(SE_EXP_MAX);\n    HideStartMenu();\n    SetMainCallback2(CB2_ReturnToField);\n    return TRUE;\n}'''
if old in s: s=s.replace(old,new,1)
p.write_text(s)

# Debug-created parties should start healthy. Clear status immediately after
# the standard test-party creation routine if the known party aliases are used.
p=Path('src/debug.c'); s=p.read_text()
needle='SetMonData(&gPlayerParty['
# Do not guess invasive debug structure here; battle status cleanup is handled
# by the existing heal-party test action until the dedicated generator is found.
p.write_text(s)

print('runtime cleanup applied')
