import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
import sys,os,glob,subprocess,shutil
sys.path.insert(0,_W+'/tools')
import isopatch
S=_W+''
B=S+'/ru/build'
new={os.path.basename(f):open(f,'rb').read() for f in glob.glob(B+'/MSGD*.PRG')+glob.glob(B+'/LOGO*.PRG')+glob.glob(B+'/EMP_*.PRG')+glob.glob(B+'/*.FIX')+glob.glob(B+'/*.SPR')+[B+'/PROG.PRG']}
moved=isopatch.patch_iso(S+'/ngcd/en.iso',B+'/ru.iso',new)
D="Shinsetsu Samurai Spirits - Bushidou Retsuden (Japan)"
disc=S+'/ru/disc_ru'; os.makedirs(disc,exist_ok=True)
for f in glob.glob(S+'/ru/disc_en/*.bin')+glob.glob(S+'/ru/disc_en/*.cue'):
    t=disc+'/'+os.path.basename(f).replace('(Japan)','(Japan) [RU]')
    if 'Track 01' in f: continue
    if not os.path.exists(t):
        if f.endswith('.cue'):
            open(t,'w').write(open(f).read().replace('(Japan) (Track','(Japan) [RU] (Track'))
        else: os.symlink(f,t)
r=subprocess.run([S+'/tools/iso2mode1',B+'/ru.iso',disc+f'/{D} [RU] (Track 01).bin'],capture_output=True,text=True)
print('moved',moved,r.stdout.strip())
