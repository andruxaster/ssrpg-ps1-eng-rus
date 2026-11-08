#!/bin/bash
# usage: run.sh cue  (commands on stdin)
S=${SSRPG_WORK:-$(cd "$(dirname "$0")/.." && pwd)}
cd $S/emu && timeout 1200 ./fe $S/pcsx_rearmed/pcsx_rearmed_libretro.so "$1" $S/emu/sys 2>$S/emu/err.log
