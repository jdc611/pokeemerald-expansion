from pathlib import Path

# Runtime playtest patch.
# Keep the status-details screen, remove the experimental healthbox arrows,
# make positive stage text vivid green, and clamp hard-cap EXP to exactly 1.

controller = Path("src/battle_controller_player.c")
text = controller.read_text()

# Stat detail palette: transparent / foreground / shadow.
text = text.replace(
    "static const u8 sStageUpColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_GREEN, TEXT_COLOR_DARK_GRAY };",
    "static const u8 sStageUpColors[] = { TEXT_COLOR_TRANSPARENT, TEXT_COLOR_LIGHT_GREEN, TEXT_COLOR_DARK_GRAY };"
)
# Some branches/builds already contain numeric colors from earlier patches.
text = text.replace(
    "static const u8 sStageUpColors[] = { 14, 5, 15 };",
    "static const u8 sStageUpColors[] = { 14, 6, 15 };"
)
controller.write_text(text)

interface = Path("src/battle_interface.c")
text = interface.read_text()

# Remove all experimental stat-stage arrow drawing added to healthboxes.  The
# detailed stage view remains available through the battle command-page tab.
# The previous patch used this helper/name; neutralize it at the call sites so
# status badges and the name/level row return to stock rendering.
for call in (
    "UpdateStatStageArrowsInHealthbox(healthboxSpriteId);",
    "UpdateStatStageArrowsInHealthbox(gHealthboxSpriteIds[battler]);",
    "UpdateStatStageArrowsInHealthbox(gHealthboxSpriteIds[i]);",
    "DrawStatStageArrows(healthboxSpriteId);",
    "DrawStatStageArrows(gHealthboxSpriteIds[battler]);",
    "DrawStatStageArrows(gHealthboxSpriteIds[i]);",
):
    text = text.replace(call, "/* Stat arrows intentionally disabled; use Status Details. */")

interface.write_text(text)

script = Path("src/battle_script_commands.c")
text = script.read_text()

# Hard cap should still award one EXP.  Handle both the stock zero branch and
# any previous patched form.
text = text.replace(
    "if (GetMonData(&gPlayerParty[*expMonId], MON_DATA_LEVEL) >= levelCap)\n            gBattleStruct->battlerExpReward = 0;",
    "if (GetMonData(&gPlayerParty[*expMonId], MON_DATA_LEVEL) >= levelCap)\n            gBattleStruct->battlerExpReward = 1;"
)

# Clamp immediately before the displayed EXP number is prepared. This catches
# rewards recomputed by multipliers/Exp Share after the earlier cap branch.
needle = "PREPARE_WORD_NUMBER_BUFFER(gBattleTextBuff3, 5, gBattleStruct->battlerExpReward);"
clamp = """if (B_EXP_CAP_TYPE == EXP_CAP_HARD\n     && GetMonData(&gPlayerParty[*expMonId], MON_DATA_LEVEL) >= GetCurrentLevelCap())\n        gBattleStruct->battlerExpReward = 1;\n\n    PREPARE_WORD_NUMBER_BUFFER(gBattleTextBuff3, 5, gBattleStruct->battlerExpReward);"""
if needle in text and clamp not in text:
    text = text.replace(needle, clamp)

# Clamp again at the controller handoff: this is the authoritative amount that
# actually gets applied to the Pokemon.
emit = "BtlController_EmitExpUpdate(0, B_COMM_TO_CONTROLLER, *expMonId, gBattleStruct->battlerExpReward);"
emit_clamp = """if (B_EXP_CAP_TYPE == EXP_CAP_HARD\n     && GetMonData(&gPlayerParty[*expMonId], MON_DATA_LEVEL) >= GetCurrentLevelCap())\n        gBattleStruct->battlerExpReward = 1;\n    BtlController_EmitExpUpdate(0, B_COMM_TO_CONTROLLER, *expMonId, gBattleStruct->battlerExpReward);"""
if emit in text and emit_clamp not in text:
    text = text.replace(emit, emit_clamp)

script.write_text(text)
