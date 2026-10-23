"""Trova le parole dubbie e prepara la revisione.

Uso: python3 dubbi.py lavoro/aida-cairo [lavoro/aida-ricordi]

Una parola è dubbia se:
- ocr: Tesseract l'ha letta con confidenza bassa;
- dizionario: il dizionario italiano non la conosce (e non torna spesso nel testo);
- edizione: un'altra edizione dello stesso libretto, passata dallo stesso
  procedimento, ha lì una parola diversa. Le due scansioni sbagliano in punti
  diversi, quindi dove non coincidono c'è quasi sempre un errore di una delle
  due (oppure una vera differenza tra le edizioni).

Scrive in revisione/:
- dubbi.tsv: una riga per dubbio, con la colonna "correzione" da riempire;
- NNNN.png: il ritaglio della scansione con la riga in questione;
- index.html: tutto insieme, da sfogliare.
Chi rivede guarda il ritaglio e scrive nella colonna "correzione" la parola
come è stampata, oppure "=" se l'OCR ha letto bene. Poi si lancia applica.py.
"""
import base64
import csv
import html
import json
import os
import re
import subprocess
import sys
import unicodedata
from collections import Counter
from difflib import SequenceMatcher

from PIL import Image

CONF_BASSA = 75
# Scambi tipici di Tesseract sulla stampa dell'Ottocento: segnalati sempre,
# anche quando l'altra edizione sbaglia allo stesso modo.
SCAMBI = {'AI': 'Al', 'Jo': 'Io', 'll': 'Il', 'if': 'il', 'Jl': 'Il',
          'Ii': 'Il', 'tl': 'il'}
PAROLA = re.compile(r"[A-Za-zÀ-ÿ]+(?:'[A-Za-zÀ-ÿ]+)?'?")


def senza_accenti(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')


def norm(w):
    return senza_accenti(w.lower().replace('’', "'"))


def ruolo(riga):
    lettere = [c for c in riga if c.isalpha()]
    return len(lettere) >= 2 and all(c.isupper() for c in lettere) and not riga.startswith('#')


def struttura(riga):
    t = riga.strip()
    lettere = [c for c in t if c.isalpha()]
    return (not t or t.startswith(('#', '//')) or ':' in t[:12] and not t.startswith('(')
            or (lettere and all(c.isupper() for c in lettere)))


def leggi(cartella):
    with open(os.path.join(cartella, 'libretto.txt'), encoding='utf-8') as f:
        righe = f.read().split('\n')
    with open(os.path.join(cartella, 'righe.json'), encoding='utf-8') as f:
        fonti = json.load(f)
    return righe, fonti


def gettoni(righe, fonti):
    """Le parole del testo (non dei titoli) con la loro riga e posizione."""
    out = []
    for i, r in enumerate(righe):
        if i >= len(fonti) or not fonti[i] or struttura(r):
            continue
        for k, m in enumerate(PAROLA.finditer(r)):
            out.append((i, k, m.group()))
    return out


def conf_parola(fonte, parola):
    """Confidenza dell'OCR per una parola della riga (la più bassa tra quelle che la contengono)."""
    n = norm(parola).strip("'")
    best = None
    for f in fonte:
        for p in f['parole']:
            if n and n in norm(p['t']):
                best = p['conf'] if best is None else min(best, p['conf'])
    return best


def sconosciute(parole):
    r = subprocess.run(['hunspell', '-d', 'it_IT', '-l'], input='\n'.join(parole),
                       capture_output=True, text=True, check=True)
    return set(r.stdout.split())


def suggerimenti(parole):
    """Prime proposte di hunspell per le parole sconosciute."""
    if not parole:
        return {}
    r = subprocess.run(['hunspell', '-d', 'it_IT', '-a'], input='\n'.join(parole),
                       capture_output=True, text=True, check=True)
    out = {}
    for line in r.stdout.splitlines():
        m = re.match(r'& (\S+) \d+ \d+: (.*)', line)
        if m:
            out[m.group(1)] = ', '.join(m.group(2).split(', ')[:3])
    return out


def confronta(mie, altre):
    """Allinea le due edizioni parola per parola.

    Restituisce le parole confermate dall'altra edizione (stessa parola nello
    stesso punto), quelle diverse con la parola dell'altra edizione, e la
    somiglianza complessiva. Le differenze che si ripetono uguali almeno tre
    volte (Rhadamès / Radamès) sono scelte dell'edizione, non errori, e
    non vengono segnalate.
    """
    a = [norm(w) for _, _, w in mie]
    b = [norm(w) for _, _, w in altre]
    confermate, diverse = set(), {}
    sm = SequenceMatcher(None, a, b, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal':
            confermate.update(range(i1, i2))
        elif op == 'replace' and (i2 - i1) <= 3 and (j2 - j1) <= 3:
            proposta = ' '.join(w for _, _, w in altre[j1:j2])
            for t in range(i1, i2):
                diverse[t] = proposta
        elif op == 'replace' and max(i2 - i1, j2 - j1) <= 15:
            # blocco più lungo (righe in ordine diverso): ogni parola cerca
            # la più somigliante dell'altro blocco
            for t in range(i1, i2):
                j = max(range(j1, j2), key=lambda j: SequenceMatcher(None, a[t], b[j]).ratio())
                if a[t] == b[j]:
                    confermate.add(t)
                elif SequenceMatcher(None, a[t], b[j]).ratio() >= 0.6:
                    diverse[t] = altre[j][2]
    coppie = Counter((a[t], norm(p)) for t, p in diverse.items())
    diverse = {t: p for t, p in diverse.items() if coppie[(a[t], norm(p))] < 3}
    return confermate, diverse, sm.ratio()


def ritaglio(cartella, fonte, parola=None):
    """La riga stampata dove sta la parola (non tutta la didascalia)."""
    if parola and len(fonte) > 1:
        n = norm(parola).strip("'")
        con = [f for f in fonte if any(n and n in norm(p['t']) for p in f['parole'])]
        fonte = con[:1] or fonte[:2]
    pezzi = []
    for f in fonte:
        im = Image.open(os.path.join(cartella, 'ita', f['pagina'] + '.png'))
        x, y, w, h = f['box']
        m = 12
        pezzi.append(im.crop((max(0, x - m), max(0, y - m),
                              min(im.width, x + w + m), min(im.height, y + h + m))))
    larg = max(p.width for p in pezzi)
    tot = Image.new('L', (larg, sum(p.height for p in pezzi)), 255)
    y = 0
    for p in pezzi:
        tot.paste(p, (0, y))
        y += p.height
    if tot.width > 900:
        tot = tot.resize((900, round(tot.height * 900 / tot.width)))
    return tot


def main():
    cartella = sys.argv[1]
    righe, fonti = leggi(cartella)
    mie = gettoni(righe, fonti)

    frequenza = Counter(norm(w) for _, _, w in mie)
    ignote = sconosciute(sorted({w for _, _, w in mie}))
    confermate, diverse, somiglianza = set(), {}, None
    if len(sys.argv) > 2:
        confermate, diverse, somiglianza = confronta(mie, gettoni(*leggi(sys.argv[2])))

    dubbi = []
    for t, (i, k, w) in enumerate(mie):
        motivi = []
        if SCAMBI.get(w):
            motivi.append('scambio tipico')
        elif t in confermate:
            continue        # due scansioni diverse hanno letto la stessa parola
        c = conf_parola(fonti[i], w)
        if c is not None and c < CONF_BASSA:
            motivi.append(f'ocr {c:.0f}')
        if w in ignote and frequenza[norm(w)] < 3:
            motivi.append('dizionario')
        if t in diverse:
            motivi.append('edizione')
        if motivi:
            dubbi.append({'riga': i + 1, 'pos': k, 'parola': w, 'motivi': motivi,
                          'altra': diverse.get(t, '') or SCAMBI.get(w) or ''})
    # Nomi dei personaggi che compaiono una o due volte: spesso un'etichetta
    # letta male ("VECCNI") o un pezzo di didascalia preso per un nome.
    ruoli = Counter(r.strip() for i, r in enumerate(righe)
                    if i < len(fonti) and fonti[i] and ruolo(r))
    frequenti = [n for n, c in ruoli.items() if c >= 3]
    for i, r in enumerate(righe):
        r = r.strip()
        if i < len(fonti) and fonti[i] and ruolo(r) and ruoli[r] <= 2:
            vicino = max(frequenti, key=lambda n: SequenceMatcher(None, r, n).ratio(), default='')
            if not vicino or SequenceMatcher(None, r, vicino).ratio() < 0.6:
                vicino = ', '.join(sorted(frequenti))
            dubbi.append({'riga': i + 1, 'pos': 'nome', 'parola': r, 'motivi': ['personaggio raro'],
                          'altra': vicino})
    dubbi.sort(key=lambda d: d['riga'])
    sugg = suggerimenti(sorted({d['parola'] for d in dubbi if 'dizionario' in d['motivi']}))

    rev = os.path.join(cartella, 'revisione')
    os.makedirs(rev, exist_ok=True)
    for vecchio in os.listdir(rev):
        os.remove(os.path.join(rev, vecchio))
    with open(os.path.join(rev, 'dubbi.tsv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(['n', 'riga', 'pos', 'parola', 'motivi', 'altra_edizione',
                    'dizionario', 'ritaglio', 'correzione'])
        for n, d in enumerate(dubbi, 1):
            nome = f'{n:04d}.jpg'
            ritaglio(cartella, fonti[d['riga'] - 1],
                     None if d['pos'] == 'nome' else d['parola']).save(os.path.join(rev, nome), quality=80)
            w.writerow([n, d['riga'], d['pos'], d['parola'], ', '.join(d['motivi']),
                        d['altra'], sugg.get(d['parola'], ''), nome, ''])

    # Pagina da sfogliare: ritaglio, riga letta, parola evidenziata, proposte.
    blocchi = []
    for n, d in enumerate(dubbi, 1):
        with open(os.path.join(rev, f'{n:04d}.jpg'), 'rb') as f:
            src = 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode()
        riga = righe[d['riga'] - 1]
        if d['pos'] == 'nome':
            letta = '<mark>' + html.escape(riga) + '</mark>'
        else:
            m = list(PAROLA.finditer(riga))[d['pos']]
            letta = (html.escape(riga[:m.start()]) + '<mark>' + html.escape(m.group()) +
                     '</mark>' + html.escape(riga[m.end():]))
        prop = []
        if d['altra']:
            fonte = 'personaggi' if d['pos'] == 'nome' else 'altra edizione'
            prop.append(f'{fonte}: <b>{html.escape(d["altra"])}</b>')
        if sugg.get(d['parola']):
            prop.append(f'dizionario: {html.escape(sugg[d["parola"]])}')
        blocchi.append(
            f'<section><div class="n">{n} · riga {d["riga"]} · {", ".join(d["motivi"])}</div>'
            f'<img src="{src}" alt=""><p>{letta}</p><p class="p">{" · ".join(prop)}</p></section>')
    titolo = next((r[7:] for r in righe if r.startswith('title: ')), cartella)
    with open(os.path.join(rev, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(f'''<!doctype html><meta charset="utf-8"><title>Revisione {html.escape(titolo)}</title>
<style>body{{font:15px/1.5 system-ui,sans-serif;max-width:900px;margin:auto;padding:16px}}
section{{border-bottom:1px solid #ccc;padding:12px 0}}img{{max-width:100%;display:block}}
.n,.p{{color:#666;font-size:13px}}mark{{background:#ffe08a}}p{{margin:6px 0;font-family:ui-monospace,monospace}}</style>
<h1>Revisione: {html.escape(titolo)}</h1><p>{len(dubbi)} dubbi su {len(mie)} parole.</p>
{"".join(blocchi)}''')

    conte = Counter(m.split()[0] for d in dubbi for m in d['motivi'])
    print(f'{len(mie)} parole, {len(confermate)} confermate dall\'altra edizione, '
          f'{len(dubbi)} dubbi: ' +
          ', '.join(f'{k} {v}' for k, v in conte.items()) +
          (f'; somiglianza con l\'altra edizione {somiglianza:.0%}' if somiglianza else ''))


if __name__ == '__main__':
    main()
