import sys, re
from html.parser import HTMLParser
SKIPCLS = {'noprint','ws-noexport','numeropagina','metadata','mw-editsection','numeropaginaFile','reference','mw-references-wrap','quality-msg'}
BLOCK = {'p','div','br','li','h1','h2','h3','h4','h5','h6','tr','section','dd','dt','dl','center','table'}
VOID = {'br','img','hr','meta','link','input','wbr','col','source'}
class P(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True); s.out=[]; s.stack=[]; s.skip=0
    def handle_starttag(s,tag,attrs):
        a=dict(attrs); cls=set((a.get('class') or '').split())
        sk = bool(cls & SKIPCLS) or tag in ('style','script','sup') or a.get('style','').replace(' ','').find('display:none')>=0
        if tag in VOID:
            if not s.skip and tag=='br':
                inrole = any(r for _,_,r in s.stack)
                ital = any(t in ('i','em') for t,_,_ in s.stack)
                s.out.append(' ' if inrole else ('_\n_' if ital else '\n'))
            return
        s.stack.append((tag,sk,False))
        if sk: s.skip+=1
        ids = tag=='span' and any(c.startswith('ids') for c in cls)
        if ids and not s.skip: s.out.append('⟦')
        role = tag=='span' and ('position:absolute' in a.get('style','').replace(' ','') or 'personaggio' in cls)
        if role and not s.skip: s.out.append('\n<<')
        s.stack[-1]=(tag,sk,role or ('ids' if ids else False))
        if not s.skip:
            if tag in BLOCK: s.out.append('\n')
            if tag in ('i','em'): s.out.append('_')
            if tag=='span' and 'mw-poem-indented' in cls: s.out.append('\t')
    def handle_endtag(s,tag):
        while s.stack:
            t,sk,role=s.stack.pop()
            if role=='ids' and not s.skip: s.out.append('⟧')
            elif role and not s.skip: s.out.append('>>')
            if sk: s.skip-=1
            elif not s.skip:
                if t in BLOCK: s.out.append('\n')
                if t in ('i','em'): s.out.append('_')
            if t==tag: break
    def handle_data(s,d):
        if not s.skip: s.out.append(d.replace('\n',' '))
p=P(); p.feed(open(sys.argv[1],encoding='utf-8').read())
txt=''.join(p.out)
txt=re.sub(r'[  ]+',' ',txt)
txt=re.sub(r' *\n *','\n',txt)
txt=re.sub(r'\n{3,}','\n\n',txt)
print(txt.strip())
