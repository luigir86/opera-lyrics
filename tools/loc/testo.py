"""Dall'OCR al formato dell'app (docs/formato-libretti.md).

Uso: python3 testo.py lavoro/aida-cairo intestazione.txt

Legge ocr/*.tsv nell'ordine delle pagine e scrive:
- libretto.txt: intestazione + testo nel formato dell'app;
- righe.json: per ogni riga di libretto.txt, da quale pagina e da quali
  parole dell'OCR viene (serve a dubbi.py per ritagliare la scansione).

Le regole sono meccaniche e prudenti: nessuna parola viene cambiata, si
toglie solo il rumore (numeri di pagina, macchie) e si sistemano spaziatura,
maiuscole dei titoli e nomi dei personaggi.
"""
import csv
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher

ORDINALI = ['primo', 'secondo', 'terzo', 'quarto', 'quinto']
ORDINALI_F = ['prima', 'seconda', 'terza', 'quarta', 'quinta', 'sesta', 'settima',
              'ottava', 'nona', 'decima', 'undecima', 'duodecima', 'decimaterza',
              'decimaquarta', 'decimaquinta']
CONF_RUMORE = 45   # sotto questa confidenza media una riga non da personaggio è rumore


class Riga:
    def __init__(self, pagina, parole):
        self.pagina = pagina
        self.parole = parole          # [{'t', 'conf', 'box': [x, y, w, h]}]
        self.testo = ' '.join(p['t'] for p in parole)
        self.conf = sum(p['conf'] for p in parole) / len(parole)
        self.x = min(p['box'][0] for p in parole)

    def box(self):
        x0 = min(p['box'][0] for p in self.parole)
        y0 = min(p['box'][1] for p in self.parole)
        x1 = max(p['box'][0] + p['box'][2] for p in self.parole)
        y1 = max(p['box'][1] + p['box'][3] for p in self.parole)
        return [x0, y0, x1 - x0, y1 - y0]


def leggi_righe(cartella):
    nomi = sorted(f for f in os.listdir(os.path.join(cartella, 'ocr')) if f.endswith('.tsv'))
    for nome in nomi:
        per_riga = defaultdict(list)
        with open(os.path.join(cartella, 'ocr', nome), encoding='utf-8') as f:
            for r in csv.DictReader(f, delimiter='\t', quoting=csv.QUOTE_NONE):
                if r['level'] == '5' and (r['text'] or '').strip():
                    k = (int(r['block_num']), int(r['par_num']), int(r['line_num']))
                    per_riga[k].append({'t': r['text'], 'conf': float(r['conf']),
                                        'box': [int(r['left']), int(r['top']),
                                                int(r['width']), int(r['height'])]})
        # Tesseract a volte spezza una riga stampata in due blocchi: si
        # riuniscono i pezzi che stanno alla stessa altezza, da sinistra a destra.
        def centro(ps):
            cs = sorted(p['box'][1] + p['box'][3] / 2 for p in ps)
            hs = sorted(p['box'][3] for p in ps)
            return cs[len(cs) // 2], hs[len(hs) // 2]
        pezzi = sorted(per_riga.values(), key=lambda ps: centro(ps)[0])
        righe = []
        for ps in pezzi:
            c, h = centro(ps)
            if righe:
                qc, qh, qs = righe[-1]
                if abs(c - qc) < 0.4 * min(h, qh):
                    righe[-1] = (qc, qh, sorted(qs + ps, key=lambda p: p['box'][0]))
                    continue
            righe.append((c, h, ps))
        for _, _, ps in righe:
            yield Riga(nome[:-4], ps)


def senza_accenti(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')


def chiave_nome(s):
    return re.sub(r'(.)\1+', r'\1', senza_accenti(s).upper())


def maiuscola(s):
    lettere = [c for c in s if c.isalpha()]
    return len(lettere) >= 2 and all(c.isupper() for c in lettere)


def romano(s):
    """Numero romano letto male dall'OCR (| e l al posto di I) -> intero."""
    s = s.upper().replace('|', 'I').replace('L', 'I').replace('1', 'I').rstrip('.:,;')
    valori = {'I': 1, 'V': 5, 'X': 10}
    if not s or any(c not in valori for c in s):
        return None
    tot = 0
    for a, b in zip(s, s[1:] + ' '):
        v = valori[a]
        tot += -v if b in valori and valori[b] > v else v
    return tot


def numero(parola, lista):
    parola = parola.lower().strip('.:,;')
    if parola in lista:
        return lista.index(parola) + 1
    return romano(parola)


def rumore(r):
    t = r.testo.strip()
    if re.fullmatch(r'[—\-–_\s.]*\d+\w?[—\-–_\s.]*', t):        # numero di pagina
        return True
    if not re.search(r'[A-Za-zÀ-ÿ]{2}', t):
        return True
    if re.fullmatch(r'FINE\W*', t):
        return True
    if re.match(r'(ATTO|SCENA|PROLOGO)\b', t) and len(t) < 25:
        return False
    if maiuscola(t) and sum(c.isalpha() for c in t) <= 3:          # frammenti: MER, BR
        return r.conf < 90
    if maiuscola(t) and r.conf >= 15:                             # nome di personaggio
        return False
    return r.conf < CONF_RUMORE


def tipografia(s):
    s = re.sub(r'\.?\s*:,\s*$', '.', s)
    s = s.replace('’', "'").replace('‘', "'").replace('«', '"').replace('»', '"')
    s = re.sub(r"(\w)' +(?=\w)", r"\1'", s)            # l’ Etiope -> l'Etiope
    s = re.sub(r"\b(\w+) '(\w)", r"\1'\2", s)           # Ch 'io -> Ch'io
    s = re.sub(r'\. ?\. ?\.', '...', s)
    s = re.sub(r'\.\s\.\.|\.\.\s\.', '...', s)
    s = re.sub(r'\s+([?!:;,.)])', r'\1', s)             # spaziatura alla francese
    s = re.sub(r'\(\s+', '(', s)
    s = re.sub(r'([,;:])(?=[^\s\d)])', r'\1 ', s)
    return re.sub(r'\s{2,}', ' ', s).strip()


def main():
    cartella, intestazione = sys.argv[1], sys.argv[2]
    tutte = []
    for r in leggi_righe(cartella):
        # macchie in testa alla riga: "; SCENA SETTIMA.", "Ò ATTO III."
        r.testo = re.sub(r'^(?:[^\w(«"]+|[A-ZÀ-Ý]\s+(?=[A-Z]{3}))', '', r.testo.strip())
        if rumore(r):
            continue
        if tutte and tutte[-1].testo.endswith('-') and r.testo[:1].isalpha():
            tutte[-1].testo = tutte[-1].testo[:-1] + r.testo     # parola divisa a fine riga
            tutte[-1].parole += r.parole
            continue
        tutte.append(r)

    # Il libretto comincia al primo atto (o prologo): prima ci sono frontespizio,
    # avvertenze e personaggi.
    inizio = next(i for i, r in enumerate(tutte)
                  if re.match(r'(ATTO|PROLOGO)\b', r.testo.strip().upper()))
    righe = tutte[inizio:]

    # Nomi dei personaggi: la grafia più frequente (con gli accenti) vince.
    varianti = defaultdict(Counter)
    alias = {}
    for r in righe:
        testa = re.split(r'[,.;]', r.testo)[0].strip()
        if maiuscola(testa) and not re.match(r'(ATTO|SCENA|PROLOGO)\b', testa):
            for nome in re.split(r'\s+E\s+|,\s*', testa):
                nome = nome.strip(' .,;:')
                if len(nome) > 2:
                    varianti[chiave_nome(nome)][nome] += 1

    # Le grafie storpiate dall'OCR (RIADAMÈS, RAMPIIIS) vanno al nome più vicino
    # tra quelli che compaiono almeno tre volte.
    gruppi = []
    for k in sorted(varianti, key=lambda k: -sum(varianti[k].values())):
        vicino = max(gruppi, key=lambda g: SequenceMatcher(None, k, g).ratio(), default=None)
        if vicino and SequenceMatcher(None, k, vicino).ratio() >= 0.7:
            varianti[vicino].update(varianti.pop(k))
            alias[k] = vicino
        else:
            gruppi.append(k)

    def canonico(nome):
        nome = nome.strip(' .,;:')
        k = chiave_nome(nome)
        c = varianti.get(alias.get(k, k))
        if not c:
            return nome
        # la lettura più frequente decide le lettere, poi si preferisce la
        # variante con gli accenti (RHADAMES -> RHADAMÈS)
        lettere = Counter()
        for n, v in c.items():
            lettere[senza_accenti(n)] += v
        base = lettere.most_common(1)[0][0]
        stesse = [n for n in c if senza_accenti(n) == base]
        con_accento = [n for n in stesse if n != base]
        return max(con_accento or stesse, key=lambda n: c[n])

    # Nomi propri (Re, Menfi, Egitto) per scrivere bene i titoli in maiuscolo.
    # Valgono le parole che a metà verso sono più spesso maiuscole che minuscole.
    propri, maiuscole, minuscole = {}, Counter(), Counter()
    for r in righe:
        for i, w in enumerate(r.testo.split()):
            w = w.strip('.,;:!?()')
            if w.islower():
                minuscole[w] += 1
            elif i and len(w) > 1 and w[0].isupper() and not maiuscola(w):
                propri[w.lower()] = w
                maiuscole[w.lower()] += 1
    propri = {k: v for k, v in propri.items() if maiuscole[k] > minuscole[k]}

    def frase(s):
        s = re.sub(r'[a-zà-ÿ]+', lambda m: propri.get(m.group(), m.group()), s.lower())
        return s[:1].upper() + s[1:]

    def elenco_nomi(s):
        s = re.sub(r'\bE\b', 'e', s)
        s = re.sub(r'\bDETT([OI])\b', lambda m: 'dett' + m.group(1).lower(), s)
        return re.sub(r'[A-ZÀ-Ý]{3,}', lambda m: canonico(m.group()).capitalize(), s)

    out = [l.rstrip('\n') for l in open(intestazione, encoding='utf-8')]
    fonti = [None] * len(out)
    stato = None          # 'luogo' subito dopo SCENA, 'prosa' nella didascalia iniziale
    prosa = []

    def emetti(testo, *origine):
        out.append(testo)
        fonti.append([{'pagina': r.pagina, 'box': r.box(),
                       'parole': r.parole} for r in origine] or None)

    def vuota():
        if out and out[-1] != '':
            emetti('')

    def chiudi_prosa():
        if prosa:
            testo = ''
            for p in prosa:
                t = p.testo.strip()
                testo = testo[:-1] + t if testo.endswith('-') else (testo + ' ' + t).strip()
            emetti(f'({tipografia(testo).strip("()")})', *prosa)
            prosa.clear()

    for r in righe:
        t = r.testo.strip()
        m = re.match(r'(?:ATTO|PROLOGO)\b\s*(\S*)', t)
        if m and len(t) < 20:
            chiudi_prosa()
            vuota()
            if t.upper().startswith('PROLOGO'):
                emetti('# Prologo', r)
            else:
                n = numero(m.group(1), ORDINALI) or 1
                emetti(f'# Atto {ORDINALI[n - 1]}', r)
            stato = 'luogo'
            continue
        m = re.match(r'S\s?C\s?E\s?N\s?A\s+([A-Z|]+)\b', t)
        if m and len(t) < 25:
            chiudi_prosa()
            vuota()
            n = numero(m.group(1), ORDINALI_F)
            emetti(f'## Scena {ORDINALI_F[n - 1] if n else m.group(1).lower()}', r)
            stato = 'luogo'
            continue
        testa, _, coda = t.partition(',')
        if maiuscola(t) and stato == 'luogo' and len(t) > 12 and not re.search(r'\bE\s+DETT', t):
            chiudi_prosa()
            emetti(f'({tipografia(frase(t))})', r)          # GIARDINO NEL PALAZZO DEL RE
            stato = 'prosa'
            continue
        if maiuscola(t) and (',' in t.rstrip('.,;') or re.search(r'\bE\s', t)):
            chiudi_prosa()
            vuota()
            emetti(f'({tipografia(elenco_nomi(t).rstrip(",. ") + ".")})', r)   # AIDA E DETTI
            stato = None
            continue
        if maiuscola(t):
            chiudi_prosa()
            vuota()
            emetti(canonico(t), r)
            stato = None
            continue
        if maiuscola(testa) and coda.strip() and not maiuscola(coda):
            chiudi_prosa()
            vuota()
            emetti(canonico(testa), r)                       # RAMPHIS, con intenzione
            emetti(f'({tipografia(coda.strip(" ;,")).strip("()")})', r)
            stato = None
            continue
        if stato in ('luogo', 'prosa'):
            prosa.append(r)
            stato = 'prosa'
            continue
        if (out and out[-1].startswith('(') and ')' not in out[-1] and t[:1].islower()):
            out[-1] += ' ' + tipografia(t)                   # didascalia su due righe
            fonti[-1].append({'pagina': r.pagina, 'box': r.box(), 'parole': r.parole})
            continue
        emetti(tipografia(t), r)

    chiudi_prosa()
    while out and out[-1] == '':
        out.pop()
        fonti.pop()
    with open(os.path.join(cartella, 'libretto.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(out) + '\n')
    with open(os.path.join(cartella, 'righe.json'), 'w', encoding='utf-8') as f:
        json.dump(fonti, f, ensure_ascii=False)
    print(f'{len(out)} righe, personaggi: ' +
          ', '.join(sorted({canonico(n) for c in varianti.values() for n in c
                            if sum(c.values()) >= 3})))


if __name__ == '__main__':
    main()
