from pathlib import Path

path = Path('src/starter_choose.c')
text = path.read_text()
old = '''    if (gSpeciesInfo[species].isLegendary
     || gSpeciesInfo[species].isMythical
     || gSpeciesInfo[species].isUltraBeast
     || gSpeciesInfo[species].isParadox)'''
new = '''    if (gSpeciesInfo[species].isRestrictedLegendary
     || gSpeciesInfo[species].isSubLegendary
     || gSpeciesInfo[species].isMythical
     || gSpeciesInfo[species].isUltraBeast
     || gSpeciesInfo[species].isParadox)'''
if old not in text:
    raise SystemExit('Custom starter legendary eligibility block not found')
path.write_text(text.replace(old, new, 1))
