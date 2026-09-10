from pathlib import Path

p = Path('src/debug.c')
text = p.read_text()

if 'sDebugMenu_Actions_TestHub' in text:
    print('Test Hub already present')
    raise SystemExit(0)

anchor = '''static const struct DebugMenuOption sDebugMenu_Actions_Main[] =
{
'''

submenu = '''static const struct DebugMenuOption sDebugMenu_Actions_TestHub[] =
{
    { COMPOUND_STRING("Prepare Test Save"),    DebugAction_Util_CheatStart },
    { COMPOUND_STRING("Fly / Checkpoints…"),   DebugAction_Util_Fly },
    { COMPOUND_STRING("Set Full Party"),       DebugAction_Party_SetParty },
    { COMPOUND_STRING("Heal Party"),           DebugAction_Party_HealParty },
    { COMPOUND_STRING("Fill Bag…"),            DebugAction_OpenSubMenu, sDebugMenu_Actions_PCBag_Fill },
    { COMPOUND_STRING("Give X…"),              DebugAction_OpenSubMenu, sDebugMenu_Actions_Give },
    { COMPOUND_STRING("Progress / Flags…"),    DebugAction_OpenSubMenuFlagsVars, sDebugMenu_Actions_Flags },
    { COMPOUND_STRING("Starter Test"),         DebugAction_Util_StarterTest },
    { COMPOUND_STRING("Start Debug Battle"),   DebugAction_Party_BattleSingle },
    { NULL }
};

'''

if anchor not in text:
    raise SystemExit('Main debug menu anchor not found')

text = text.replace(anchor, submenu + anchor, 1)
text = text.replace(
    '''static const struct DebugMenuOption sDebugMenu_Actions_Main[] =
{
    { COMPOUND_STRING("Utilities…"),''',
    '''static const struct DebugMenuOption sDebugMenu_Actions_Main[] =
{
    { COMPOUND_STRING("TEST HUB…"),      DebugAction_OpenSubMenu, sDebugMenu_Actions_TestHub, },
    { COMPOUND_STRING("Utilities…"),''',
    1,
)

p.write_text(text)
print('Debug Test Hub patch applied')
