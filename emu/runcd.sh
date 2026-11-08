#!/bin/bash
S=${SSRPG_WORK:-$(cd "$(dirname "$0")/.." && pwd)}
cd $S/emu && NEOBIOS="${NEOBIOS:-neocd.bin (CDZ)}" timeout 1800 ./fe $S/neocd_libretro/neocd_libretro.so "$1" $S/ru/sys 2>$S/emu/errcd.log
