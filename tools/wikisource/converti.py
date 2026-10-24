import sys, re
# conv.py ROLEMAP_NAME header.txt act1.txt act2.txt ...
ROMAN = None
DG = {'gio':'DON GIOVANNI','gto':'DON GIOVANNI','glo':'DON GIOVANNI','lep':'LEPORELLO','l':'LEPORELLO',
      'zer':'ZERLINA','zar':'ZERLINA','z':'ZERLINA','elv':'DONNA ELVIRA','mas':'MASETTO',
      'ott':'DON OTTAVIO','ot':'DON OTTAVIO','o':'DON OTTAVIO','anna':'DONNA ANNA','ann':'DONNA ANNA',
      'an':'DONNA ANNA','a':'DONNA ANNA','com':'IL COMMENDATORE','tutti':'TUTTI','coro':'CORO',
      'gli altri':'GLI ALTRI'}
TR = {'i':'CORO I','ii':'CORO II','commission':'COMMISSIONARIO','gli altri':'GLI ALTRI'}
FIXES = {'dg': {
 # speeches whose singer the source names only in the scene heading, and
 # roles or directions the source's markup leaves out of place
 'Amico, per pietà, un po’d’acqua fresca,': '<<Lep.>> Amico, per pietà, un po’d’acqua fresca,',
 'Come mai creder deggio,': '<<Ott.>> Come mai creder deggio,',
 'Elv. L’ultima prova': '<<Elv.>> L’ultima prova',
 '_Anna, Ott., Elv. e Mas._': '<<Anna, Ott., Elv. e Mas.>>',
 'Questo pezzo di fagiano di ⟦nascosto)⟧': 'Questo pezzo di fagiano ⟦di nascosto)⟧',
 '<<Gio.>> Sì, vita mia, son io.⟦(Gio. si mette dietro a ⟧Lep. e parla ad Elv.)': '<<Gio.>> Sì, vita mia, son io.⟦(Gio. si mette dietro a Lep. e parla ad Elv.)⟧',
}, 'tr': {
 'È': '<<Violetta>> È strano!.. è strano!.. in core',
 'strano!.. è strano!.. in core': None,
 'Lunge da lei per me non v’ha diletto!... (_depone il fucile_)': '<<Alfredo>> Lunge da lei per me non v’ha diletto!... (_depone il fucile_)',
 'Oh mio rimorso!... Oh infamia!...': '<<Alfredo>> Oh mio rimorso!... Oh infamia!...',
 'Largo al quadrupede': '<<Coro>> Largo al quadrupede',
 # Germont's letter, read aloud by Violetta: printed in italics, but it is text
 '_Teneste la promessa... La disfida_': '<<Violetta>> Teneste la promessa... La disfida',
 '_Ebbe luogo; il barone fu ferito,_': 'Ebbe luogo; il barone fu ferito,',
 '_Però migliora... Alfredo_': 'Però migliora... Alfredo',
 '_È in stranio suolo; il vostro sagrifizio_': 'È in stranio suolo; il vostro sagrifizio',
 '_Io stesso gli ho svelato._': 'Io stesso gli ho svelato.',
 '_Egli a voi tornerà pel suo perdono;_': 'Egli a voi tornerà pel suo perdono;',
 '_Io pur verrò... Curatevi... mertate_': 'Io pur verrò... Curatevi... mertate',
 '_Un’avvenir migliore;_': 'Un’avvenir migliore;',
 '_Giorgio Germont_... È tardi!.. (_desolata_)': 'Giorgio Germont... È tardi!.. (_desolata_)',
 '<<Germont, >>Dottore,': '<<Germont, Dottore, Annina>>',
 'Annina Finché avrà il ciglio lacrime': 'Finché avrà il ciglio lacrime',
}}
mapname, header, acts = sys.argv[1], sys.argv[2], sys.argv[3:]
M = DG if mapname=='dg' else TR

def role(r):
    r = r.replace('_','').strip().rstrip('.').strip()
    low = r.lower()
    if re.fullmatch(r'a 2', low): return 'A DUE'
    if low in M: return M[low]
    if mapname=='dg':
        toks = [t for t in re.split(r'[ ,.]+|\be\b', low) if t]
        names = [M[t] for t in toks]
        return ', '.join(names[:-1]) + ' E ' + names[-1] if len(names)>1 else names[0]
    return r.upper()

FRAG = re.compile(r'\(\s*_[^_]+_[^()]*\)\.?|\(?⟦[^⟧]*⟧\)?\.?|\(?\s*_[^_]+_\s*\)?\.?')
def clean(s): return re.sub(r'\s+',' ',s.replace('_','')).strip()
def emit_dir(buf, d, merge=False, at=None):
    if not re.search(r'\w', d): return
    if at is not None and at < len(buf):
        buf.insert(at, d); return
    if merge and buf and buf[-1].startswith('(') and buf[-1].endswith(')') and not re.search(r'[.!?;:]\)$', buf[-1]) and d[1:2].islower():
        buf[-1] = buf[-1][:-1] + ' ' + d[1:]
    else:
        buf.append(d)
def dirline(s):
    s = clean(s.replace('⟦','').replace('⟧','')).strip()
    if s.startswith('(') and s.endswith(')'): s = s[1:-1].strip()
    s = s.replace('(','').replace(')','') if s.count('(')!=s.count(')') else s
    return '(' + s + ')'

out = [l.rstrip('\n') for l in open(header, encoding='utf-8')]
for path in acts:
    lines = open(path, encoding='utf-8').read().split('\n')
    FIX = FIXES[mapname]
    lines = [FIX.get(l.strip(), l) for l in lines]
    lines = [l for l in lines if l is not None]
    # join stray ')' lines
    j=[]
    for l in lines:
        if re.fullmatch(r'\)\.?', l.strip()) and j:
            k=len(j)-1
            while k>=0 and not j[k].strip(): k-=1
            j[k]=j[k].rstrip()+')'; continue
        j.append(l)
    lines=j
    in_scene=False; spoke=False; buf=[]; pending=['',0,None]
    def emit(x): buf.append(x)
    def flush():
        if pending[0]: emit_dir(buf, dirline(pending[0]), at=pending[2]); pending[0]=''
    for l in lines:
        s=l.strip()
        if not s or s.startswith('Questo testo è'): continue
        if pending[0]:
            pending[1]+=1
            if pending[1]>3 or (s.startswith('<<') and '⟦' not in s) or re.match(r'(scena|ATTO)\b', s, re.I): flush()
        if re.fullmatch(r'[—\- ]*fine[—\- .]*', s, re.I) or s.startswith('FINE DEL'): continue
        m=re.fullmatch(r'ATTO (\w+)', s)
        if m:
            emit(''); emit('# Atto '+m.group(1).lower()); in_scene=False; continue
        m=re.fullmatch(r'scena\.? ?(.+?)\.?', s, re.I)
        if m and len(s)<20:
            w=m.group(1); w = w.upper() if re.fullmatch(r'[ivxlIVXL]+', w) else w.lower()
            emit(''); emit('## Scena '+w); in_scene=True; spoke=False; continue
        r=None
        m=re.match(r'<<(.*?)>>\s*(.*)', s)
        if m:
            rr=m.group(1)
            if rr.strip().startswith('('):  # misplaced direction
                s=rr+' '+m.group(2)
            else:
                r=role(rr); s=m.group(2).strip()
        if r:
            if r.startswith('E ') or rr.strip().startswith('e '):
                # role split over two lines, e.g. "Anna, Ott." / "e Elv."
                k=len(buf)-1
                while k>=0 and buf[k]=='' : k-=1
                # find previous role line
                p=k
                while p>=0 and not (buf[p].isupper() and buf[p]==buf[p].upper() and re.search('[A-Z]{2}',buf[p])): p-=1
                if p>=0:
                    buf[p]=buf[p].replace(' E ',', ')+' E '+(r[2:] if r.startswith('E ') else r)
                    r=None
            if r:
                emit(''); emit(r); spoke=True
        if not s: continue
        if not spoke and not r:
            sys.stderr.write('PRE: '+s[:90]+'\n')
            emit_dir(buf, dirline(s), True); continue
        frags=[]
        def take(m):
            frags.append(m.group(0)); return ' '
        v = FRAG.sub(take, s)
        v = clean(v)
        if re.fullmatch(r'[().,;: ]*', v): v=''
        if v:
            if v.startswith('(') and v.endswith(')') and v.count('(')==1:
                sys.stderr.write('ASIDE: '+v+'\n'); v='\\'+v
            elif re.search(r'[A-Za-zÀ-ÿ]{2}', v) and v==v.upper():
                sys.stderr.write('CAPS: '+v+'\n'); v='\\'+v
            emit(v)
        for f in frags:
            t = clean(f.replace('⟦','').replace('⟧',''))
            if not re.search(r'\w', t): 
                if pending[0] and ')' in t: pass
                else: continue
            if not pending[0]: pending[1]=0; pending[2]=len(buf)
            pending[0] = (pending[0]+' '+t).strip() if pending[0] else t
            p = pending[0]
            if p.count('(') <= p.count(')') or not p.startswith('('):
                emit_dir(buf, dirline(p), at=pending[2]); pending[0]=''
    flush()
    out += buf
txt='\n'.join(out)
txt=re.sub(r'\n{3,}','\n\n',txt).strip()+'\n'
sys.stdout.write(txt)
