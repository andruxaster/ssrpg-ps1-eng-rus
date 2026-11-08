Shinsetsu Samurai Spirits Bushido Retsuden (PS1) — English dialogue, v2
=======================================================================
* Dialogue that exists in the Neo Geo CD version: English text from
  MoriyaMug's NGCD translation v1.10 (https://ko-fi.com/moriyamug).
* Dialogue that exists only in the PS1 version (rewritten / new lines):
  new translation made for this port, using the NGCD translation's names
  and terminology (translation/GLOSSARY.md, translation/out_*.json).
* Menus, items, techniques, enemy names, character profiles, graphics and
  system messages are untouched (Japanese).
Ask the original author before distributing anything based on his work.

Apply
-----
Base: Redump PS1 dump, single BIN, CRC32 6A001A89
  xdelta3 -d -s "Shinsetsu Samurai Spirits - Bushidou Retsuden (Japan).bin" \
     SSRPG_PS1_EN_v2.xdelta \
     "Shinsetsu Samurai Spirits - Bushidou Retsuden (Japan) [EN].bin"
Result CRC32: 73768FCF. Use the included .cue (data track is longer, audio
track times moved).

Coverage (unique PS1 messages, see script_report.tsv)
------------------------------------------------------
  NGCD exact ........ 5197
  NGCD close ........ 1855   (PS1 reworded line, NGCD English used)
  NGCD context ...... 320    (looser match by neighbouring lines)
  new translation ... 3154
  Japanese .......... 13 in F_IZU/F_TYU (message buffer limit 0x5C00)
                      + 18 in the debug area F_TEST

Technical notes
---------------
* 1260 two-letter glyphs are appended to FONT.PS (loaded into RAM at
  0x801F2600-0x801FC380, above the largest field-scene load and below
  the stack); free SJIS codes 0x85xx.. map to glyph indices >= 1859 via
  the exe's SJIS->glyph table. Hooks: 0x80023CC0 (glyph pointer),
  0x80029220 (font loader); patch code sits in dead functions 0x80023C44
  and 0x80023368.
* FLD archives repacked; 7 FLD files and FONT.PS moved past the old end of
  the data track; exe file/scene tables and ISO9660 directory updated;
  EDC/ECC regenerated.
* The leader's name is inserted by the game in Japanese (kanji/kana).
* Tested in PCSX-ReARMed (HLE BIOS): chapter 1 and 2 openings, town,
  world map, random battles, menu prompt (0800), name insertion.
  Yes/No prompts (0700) not verified in-game. Not tested on hardware.
