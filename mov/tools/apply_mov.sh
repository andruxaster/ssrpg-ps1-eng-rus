#!/bin/sh
# Russian calligraphy cards in MOV/OPEN_00.STR. Run after tools/disc.py on the built bin.
# Needs jPSXdec (https://github.com/m35/jpsxdec) built at $SSRPG_WORK/jpsx/src/jpsxdec/_ant/release/jpsxdec.jar
# (or set JPSXDEC=/path/to/jpsxdec.jar).
set -e
S=${SSRPG_WORK:-$(cd "$(dirname "$0")/../.." && pwd)}
BIN=${1:-$S/build_ru/SSRPG_RU.bin}
J=${JPSXDEC:-$S/jpsx/src/jpsxdec/_ant/release/jpsxdec.jar}
IDX=${TMPDIR:-/tmp}/ssrpg_mov.idx
python3 -I "$S/mov/tools/genframes.py" >/dev/null
cd "$S/mov/rep"
java -jar "$J" -f "$BIN" -x "$IDX" >/dev/null 2>&1
ITEM=$(grep -n "ID:MOV/OPEN_00.STR\[0\]|" "$IDX" | sed 's/.*#:\([0-9]*\)|.*/\1/')
java -jar "$J" -x "$IDX" -i $ITEM -replaceframes replace.xml >/dev/null 2>&1
echo "OPEN_00.STR patched (item $ITEM)"
