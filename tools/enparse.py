import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
# Parse an NGCD English message (list of words) into segments / choices
import sys,re
sys.path.insert(0,_W+'/tools')
import endec
NAME='\x01'   # placeholder for leader name
PARAM1={6,7,9,0xb,0xd}
def parse(words):
    segs=[[]]   # list of segments, each a list of text pieces
    spk=[None]
    choice=None # ('yn', [opts]) or ('menu',[opts])
    mode='text'; buf=''
    i=0
    cur=''
    def flush_seg():
        nonlocal cur
        if cur.strip(): segs[-1].append(cur)
        cur=''
    ctext=''
    col=0
    while i<len(words):
        v=words[i]
        if 0x2100<=v<0x2900:
            t=endec.code_text(v)
            if mode=='text':
                if col==16: cur+=' '; col=0
                cur+=t; col+=1
            else: ctext+=t
            i+=1; continue
        if v not in (1,0xd,0xb): col=0
        if v==0xffff: break
        if v in PARAM1:
            if v in (6,7,9):
                if mode=='text':
                    flush_seg()
                    if segs[-1]: segs.append([]); spk.append(None)
                    spk[-1]=(v,words[i+1] if i+1<len(words) else 0)
            i+=2; continue
        if v==0:
            if mode=='text': cur+=' '
            i+=1; continue
        if v==4:
            if mode=='text': cur+=NAME
            i+=1; continue
        if v==8:
            if mode=='text':
                flush_seg()
                if segs[-1]: segs.append([]); spk.append(spk[-1])
            i+=1; continue
        if v==2:
            flush_seg(); mode='yn'; ctext=''; i+=1; continue
        if v==0xa:
            flush_seg(); mode='menu'; ctext=''; i+=1; continue
        if v==3:
            if mode in ('yn','menu'):
                ctext+='\x02'
            i+=1; continue
        i+=1   # <1> etc
    flush_seg()
    segs=[' '.join(' '.join(s).split()) for s in segs]
    pairs=[(a,b) for a,b in zip(segs,spk) if a]
    segs=[a for a,b in pairs]; parse.spk=[b for a,b in pairs]
    if mode=='yn':
        opts=[o.strip() for o in ctext.split('\x02') if o.strip()]
        choice=('yn',opts)
    elif mode=='menu':
        raw=ctext.replace('\x02','  ')
        parts=re.split(r'(?:^|\s{2,})[A-F]\s{2,}',' '+raw if not raw.startswith('A') else raw)
        opts=[p.strip() for p in re.split(r'(?:^|\s+)[A-F]\s{2,}',raw) if p.strip()]
        choice=('menu',opts)
    return segs,choice
