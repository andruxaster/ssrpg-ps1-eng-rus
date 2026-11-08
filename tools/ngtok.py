import os as _os
def _ssrpg_work():
    d=_os.path.dirname(_os.path.abspath(globals().get("__file__",".")))
    while not _os.path.exists(_os.path.join(d,"SSRPG_ROOT")) and _os.path.dirname(d)!=d: d=_os.path.dirname(d)
    return _os.environ.get("SSRPG_WORK",d)
_W=_ssrpg_work()  # project work dir (repo root + game data, see README)
# tokenise NGCD EN message into pages with codes
import sys
sys.path.insert(0,_W+'/tools')
import endec
NT=1793
PARAM1={5,6,7,9,0xb,0xd}
PAGESTART={6,7,9}
def is_text(v): return 0x212a<=v<0x212a+NT
def tokens(words):
    out=[];i=0
    while i<len(words):
        v=words[i]
        if is_text(v): out.append(('t',v)); i+=1; continue
        if v==0xffff: out.append(('end',[v])); break
        if v in PARAM1 and i+1<len(words): out.append(('c',[v,words[i+1]])); i+=2; continue
        out.append(('c',[v])); i+=1
    return out
def structure(words):
    """returns dict(pages=[{pre:[codes], items:[('t',str)|('c',codes)], }], choice=None|{kind,opts_raw}, tail=[codes])"""
    toks=tokens(words)
    pages=[]; cur=None; choice=None; ctext=None; mode='text'; col=0
    def newpage():
        p={'pre':[],'items':[]}; pages.append(p); return p
    cur=newpage()
    for kind,val in toks:
        if kind=='end': break
        if mode!='text':
            if kind=='t': choice['raw'][-1]+=endec.code_text(val)
            elif val==[3]: choice['raw'].append('')
            else: choice['codes'].append(val)
            continue
        if kind=='c' and val[0] in (2,0xa):
            mode='choice'; choice={'kind':'yn' if val[0]==2 else 'menu','raw':[''],'codes':[]}; continue
        if kind=='c' and (val[0] in PAGESTART or val==[8]):
            if val==[8]:
                cur['items'].append(('c',val)); cur=newpage(); col=0; continue
            if any(k=='t' for k,_ in cur['items']): cur=newpage(); col=0
            cur['pre'].append(val) if not cur['items'] else cur['items'].append(('c',val)); continue
        if kind=='t':
            if col==16: cur['items'].append(('ws',None)); col=0
            cur['items'].append(('t',endec.code_text(val))); col+=1
        else:
            if val[0] not in (1,0xd,0xb): col=0
            if not any(k=='t' for k,_ in cur['items']) and val[0]!=0 and val[0]!=4: cur['pre'].append(val)
            else: cur['items'].append(('c',val))
    pages=[p for p in pages if p['items'] or p['pre']]
    if choice: choice['opts']=[o for o in choice['raw'] if o.strip()]
    return pages,choice
def page_text(p):
    s=''
    for k,v in p['items']:
        if k=='t': s+=v
        elif k=='ws': s+=' '
        elif v==[0]: s+=' '
        elif v==[4]: s+='{NAME}'
    return ' '.join(s.split())
