from pathlib import Path

# Battle stage panel: use explicit green/red text palettes per stat instead of a single neutral palette.
p = Path('src/battle_controller_player.c')
s = p.read_text()
old = '''            AppendBattleStatStage(line, battler, i);\n            AddTextPrinterParameterized3(B_WIN_STAGE_PANEL, FONT_SMALL,\n                                         12 + (i % 4) * 58, 4 + (i / 4) * 18,\n                                         sPanelColors, 0, line);\n'''
new = '''            static const u8 sStageUpColors[] = { 14, 5, 15 };\n            static const u8 sStageDownColors[] = { 14, 4, 15 };\n            s8 stage = gBattleMons[battler].statStages[sStagePanelStats[i]] - DEFAULT_STAT_STAGE;\n            const u8 *stageColors = stage > 0 ? sStageUpColors : (stage < 0 ? sStageDownColors : sPanelColors);\n\n            AppendBattleStatStage(line, battler, i);\n            AddTextPrinterParameterized3(B_WIN_STAGE_PANEL, FONT_SMALL,\n                                         12 + (i % 4) * 58, 4 + (i / 4) * 18,\n                                         stageColors, 0, line);\n'''
if old not in s:
    raise SystemExit('Missing stat panel print block')
s = s.replace(old, new, 1)
p.write_text(s)

# Test-party generation: normalize generated mons to current cap and clear accidental statuses.
p = Path('src/debug.c')
s = p.read_text()
# Add caps include if absent.
if '#include "caps.h"' not in s:
    s = s.replace('#include "starter_choose.h"\n', '#include "starter_choose.h"\n#include "caps.h"\n', 1)

# Patch the standard debug Set Party completion path. We do this at the function body anchor used by expansion.
anchor = 'static void DebugAction_Party_SetParty(u8 taskId)\n'
pos = s.find(anchor)
if pos < 0:
    raise SystemExit('Missing DebugAction_Party_SetParty')
brace = s.find('{', pos)
depth = 0
end = None
for i in range(brace, len(s)):
    if s[i] == '{': depth += 1
    elif s[i] == '}':
        depth -= 1
        if depth == 0:
            end = i + 1
            break
body = s[pos:end]
# Only add cleanup once; preserve existing party-generation logic.
if 'TEST_TEAM_CAP_CLEANUP' not in body:
    insert = '''\n    // TEST_TEAM_CAP_CLEANUP: test parties should enter battles healthy and at the active cap.\n    {\n        u8 i;\n        u8 cap = GetCurrentLevelCap();\n        for (i = 0; i < gPlayerPartyCount; i++)\n        {\n            struct Pokemon *mon = &gPlayerParty[i];\n            enum Species species = GetMonData(mon, MON_DATA_SPECIES);\n            u32 status = 0;\n            u32 exp;\n            if (species == SPECIES_NONE || GetMonData(mon, MON_DATA_IS_EGG))\n                continue;\n            exp = gExperienceTables[gSpeciesInfo[species].growthRate][cap];\n            SetMonData(mon, MON_DATA_EXP, &exp);\n            SetMonData(mon, MON_DATA_LEVEL, &cap);\n            SetMonData(mon, MON_DATA_STATUS, &status);\n            CalculateMonStats(mon);\n            SetMonData(mon, MON_DATA_HP, &mon->hp);\n        }\n    }\n'''
    # Insert immediately before final closing brace.
    body = body[:-1] + insert + '}'
    s = s[:pos] + body + s[end:]
p.write_text(s)
print('Battle UI + Test Team Cleanup applied')
