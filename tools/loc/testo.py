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
    if re.match(r'(ATTO|PARTE|SCENA|PROLOGO)\b', t) and len(t) < 45:
        return False
    if maiuscola(t) and sum(c.isalpha() for c in t) <= 3:          # frammenti: MER, BR
        return r.conf < 90
    if maiuscola(t) and r.conf >= 15:                             # nome di personaggio
        return False
    return r.conf < CONF_RUMORE


def tipografia(s):
    s = re.sub(r'\s+[|¦]+(?=\s|$)', '', s)              # filetti a margine
    s = re.sub(r'^[a-zìè]\s+(?=[A-ZÀ-Ý])', '', s)        # macchia prima del verso
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


NUMERI_A = {'2': 'A DUE', '3': 'A TRE', '4': 'A QUATTRO', '5': 'A CINQUE', '6': 'A SEI'}


def nomi_dei_personaggi(prima, dopo):
    """I nomi dei personaggi: la prima parola in maiuscolo di ogni riga
    dell'elenco iniziale (dopo vengono gli interpreti, da ignorare) e i nomi
    in maiuscolo degli ingressi in scena."""
    nomi = Counter()
    esclusi = ('PERSONAGGI', 'ATTORI', 'ATTO', 'PARTE', 'SCENA', 'PROLOGO', 'SIG', 'SIGN',
               'SIGNORA', 'DETTI', 'DETTO', 'FINE')
    esclusi += ('PRIMA', 'SECONDA', 'TERZA', 'QUARTA', 'ULTIMA', 'III', 'CORI', 'COMPARSE')
    pag = next((r.pagina for r in prima if 'PERSONAGGI' in r.testo), None)
    elenco = [r for r in prima if not pag or r.pagina == pag]
    for r in elenco:
        m = re.match(r"(?:Il|La|Lo|Un|Una|Gran|Il Gran)?\s*([A-ZÀ-Ý][A-ZÀ-Ý']{2,})", r.testo)
        if m and m.group(1) not in esclusi:
            nomi[m.group(1)] += 1
    if pag and len(nomi) < 3:
        # elenco in tondo ("Il Conte di Luna . . . sig. Coretti"): la prima
        # parola con la maiuscola di ogni riga
        for r in elenco:
            m = re.match(r"(?:(?i:il|la|lo|un|una|gran|il gran)\s+)?([A-ZÀ-Ý][\wÀ-ÿ']{2,})", r.testo)
            if m and m.group(1).upper() not in esclusi:
                nomi[m.group(1).upper()] += 1
    for r in dopo:
        for w in re.findall(r"[A-ZÀ-Ý][A-ZÀ-Ý']{2,}", r.testo):
            if w not in esclusi:
                nomi[w] += 1
    for w in ('TUTTI', 'TUTTE', 'CORO'):
        nomi[w] += 3
    return nomi


def separa_etichette(righe, nomi):
    """Nei libretti di metà Ottocento chi canta è un'abbreviazione a margine,
    sulla stessa riga del verso ("Zac. D'Egitto là sui lidi"). La si riconosce
    dallo spazio largo che la separa dal verso. Diventa una riga a sé con il
    nome per intero, preso dall'elenco dei personaggi."""
    inizi = defaultdict(list)
    for r in righe:
        if len(r.parole) >= 3:
            inizi[r.pagina].append(r.parole[0]['box'][0])
    mediane = {p: sorted(v)[len(v) // 2] for p, v in inizi.items()}

    def etichetta(r):
        ps = r.parole
        if len(ps) < 2 or re.match(r'(ATTO|PARTE|SCENA|PROLOGO)\b', r.testo):
            return 0
        med = mediane.get(r.pagina, 0)
        p0 = ps[0]['box']
        if p0[0] < med - 100 and p0[0] + p0[2] < med - 30:
            k = 1                    # parola tutta a sinistra della colonna dei versi
            a_sinistra.add(id(r))
        else:
            for k in range(1, min(4, len(ps))):
                fine = ps[k - 1]['box'][0] + ps[k - 1]['box'][2]
                if ps[k]['box'][0] - fine > max(30, 1.3 * ps[k - 1]['box'][3]):
                    break            # spazio largo dopo l'etichetta
            else:
                return 0
        testo = ' '.join(p['t'] for p in ps[:k])
        if not re.fullmatch(r"[A-ZÀ-Ýa][\wÀ-ÿ'.,]{0,14}(?:\s(?:e|ed|E|[\dA-ZÀ-Ý][\wÀ-ÿ.,]*)){0,2}", testo):
            return 0
        return k

    a_sinistra = set()
    trovate = [etichetta(r) for r in righe]
    # In un'aria rientrata anche l'inizio di un verso sta a sinistra della
    # colonna ("È strano!...", "Che risolvi"). Su una pagina così nessuna di
    # queste parole sembra un nome: nessuna finisce col punto, è in maiuscolo
    # o è l'inizio di un nome dell'elenco. Allora non sono nomi.
    def nome_sicuro(w):
        lettere = senza_accenti(w).upper().strip(".,:;!?'")
        return w.endswith('.') or (len(lettere) >= 2 and w.isupper()) or (
            len(lettere) >= 2 and any(senza_accenti(n).startswith(lettere) and c >= 3
                                      for n, c in nomi.items()))
    pagine_buone = {r.pagina for r, k in zip(righe, trovate)
                    if k and id(r) in a_sinistra and nome_sicuro(r.parole[0]['t'])}
    trovate = [0 if k and id(r) in a_sinistra and r.pagina not in pagine_buone else k
               for r, k in zip(righe, trovate)]
    if sum(1 for r, k in zip(righe, trovate) if k and r.parole[k - 1]['t'].endswith('.')) < 10:
        return righe            # questo libretto scrive i nomi su righe proprie

    def nome_pieno(et):
        intero = not et.rstrip(' :').endswith('.')    # "Coro" e non "Con.": parola intera
        et = et.strip(' .:')
        m = re.fullmatch(r'a\s*(\d)', et)
        if m:
            return NUMERI_A.get(m.group(1), et.upper())
        pezzi = re.split(r'\s+(?:e|ed|E)\s+', et)
        if len(pezzi) > 1:
            return ' E '.join(nome_pieno(p) for p in pezzi)
        k = senza_accenti(et).upper().strip('.,')
        if k[:1] == 'T' and SequenceMatcher(None, k, 'TUTTI').ratio() >= 0.4:
            return 'TUTTI'           # Turri, Turi, Torri: il coro di tutti
        candidati = [n for n in nomi if senza_accenti(n).startswith(k)]
        if candidati:
            return max(candidati, key=lambda n: nomi[n])
        # letture storpiate: Turri -> TUTTI, Isn. -> ISMAELE
        voto = {n: SequenceMatcher(None, k, senza_accenti(n)[:max(len(k), 3)]).ratio()
                + (0.1 if n[:1] == k[:1] else 0)            # Fan. -> FAMIGLIARI, non MANRICO
                + (0.05 if intero and len(n) == len(k) else 0)  # Cono -> CORO, non CONTE
                for n in nomi}
        migliore = max(voto, key=lambda n: (voto[n], nomi[n]), default=None)
        if migliore and voto[migliore] >= 0.6:
            return migliore
        return et.upper()

    out = []
    for r, k in zip(righe, trovate):
        if not k:
            out.append(r)
            continue
        et = Riga(r.pagina, r.parole[:k])
        et.testo = nome_pieno(et.testo)
        out.append(et)
        out.append(Riga(r.pagina, r.parole[k:]))
    return out


def fine_di(testo):
    """"FINE DELL'ATTO PRIMO" -> "ATTO PRIMO", anche letto male ("Fine versa Panre Terza")."""
    parole = re.findall(r"[A-ZÀ-Ý]+", senza_accenti(testo.upper()))
    if len(testo) > 40 or len(parole) < 2 or parole[0] != 'FINE':
        return None
    for i, w in enumerate(parole[1:4], 1):
        for tipo in ('ATTO', 'PARTE', 'PROLOGO'):
            if w == tipo or (len(w) >= 4 and SequenceMatcher(None, w, tipo).ratio() >= 0.6):
                return ' '.join([tipo] + parole[i + 1:i + 2])
    return None


def maiuscole_le_etichette(righe, nomi=()):
    """Nomi di chi canta stampati in tondo su una riga loro ("Zaccaria.").

    Alcune edizioni non usano il maiuscoletto: il nome è una riga corta che
    finisce col punto. Sono etichette le righe così che tornano almeno tre
    volte, e quelle che somigliano molto a una di esse ("Zacearia."); si
    scrivono in maiuscolo, come le altre edizioni. Un nome abbreviato ("Abig.")
    diventa il nome intero se è l'inizio di uno solo dei nomi scritti a mano
    in personaggi.txt.
    """
    forma = re.compile(r"[A-ZÀ-Ý][\wÀ-ÿ']*(?:\s+(?:e|ed|[A-ZÀ-Ý][\wÀ-ÿ']*\.?),?){0,3}\s*\.")
    conta = Counter(r.testo.strip() for r in righe
                    if forma.fullmatch(r.testo.strip()) and not maiuscola(r.testo))
    frequenti = [t for t, c in conta.items() if c >= 3]
    for r in righe:
        t = r.testo.strip()
        if t in conta and (t in frequenti or any(
                SequenceMatcher(None, t, f).ratio() >= 0.8 for f in frequenti)):
            r.testo = t.upper()
            k = r.testo.strip(' .')
            pieni = [n for n in nomi if nomi[n] >= 100 and n != k and n.startswith(k)]
            if r.testo.endswith('.') and len(pieni) == 1:
                r.testo = pieni[0]


def main():
    cartella, intestazione = sys.argv[1], sys.argv[2]
    tutte = []
    for r in leggi_righe(cartella):
        # macchie in testa alla riga: "; SCENA SETTIMA.", "Ò ATTO III."
        while len(r.parole) > 1 and not re.search(r'[\w(]', r.parole[0]['t']):
            r.parole.pop(0)                      # macchie a margine: "|", "®."
        r.testo = ' '.join(p['t'] for p in r.parole)
        r.testo = re.sub(r'^(?:[^\w(«"]+|[A-ZÀ-Ý]\s+(?=[A-Z]{3}))', '', r.testo.strip())
        r.testo = re.sub(r'^\d+\s+(?=(ATTO|PARTE)\b)', '', r.testo)   # testatina: "10 ATTO I"
        m = fine_di(r.testo)
        if m:
            # FINE DELL'ATTO PRIMO: serve a ritrovare gli atti quando il titolo
            # dell'atto, in caratteri grandi, l'OCR non lo legge
            r.testo = '§FINE ' + m
            tutte.append(r)
            continue
        if re.match(r"FINE\s+(DELL|DEL)", r.testo.upper()):
            continue
        if rumore(r):
            continue
        if (r.testo.strip(' .') in ('ELENCO', 'CATALOGO')
                or re.match(r"(ELENCO|CATALOGO)\b.{0,30}\b(libretti|opere|edizioni)", r.testo, re.I)):
            break           # in fondo, il catalogo dell'editore: non è libretto
        if tutte and tutte[-1].testo.endswith('-') and r.testo[:1].isalpha():
            tutte[-1].testo = tutte[-1].testo[:-1] + r.testo     # parola divisa a fine riga
            tutte[-1].parole += r.parole
            continue
        tutte.append(r)

    # Il libretto comincia al primo atto (o prologo): prima ci sono frontespizio,
    # avvertenze e personaggi.
    inizio = next((i for i, r in enumerate(tutte)
                   if re.match(r'(ATTO|PARTE|PROLOGO)\b', r.testo.strip()) and len(r.testo) < 45),
                  None)
    if inizio is not None and not re.search(r'\b(PRIM[OA]|I|PROLOGO)\b\W*$',
                                             tutte[inizio].testo.replace('|', 'I')):
        # il primo titolo letto non è il primo atto: quello è andato perso,
        # si comincia dalla prima scena che lo precede
        prima_scena = next((i for i, r in enumerate(tutte[:inizio])
                            if re.match(r'S\s?C\s?E\s?N\s?A\s+(PRIMA|I)\b', r.testo)), None)
        if prima_scena is not None:
            tipo = tutte[inizio].testo.split()[0]
            finto = Riga(tutte[prima_scena].pagina, tutte[prima_scena].parole[:1])
            finto.testo = f'{tipo} PRIM{"A" if tipo == "PARTE" else "O"}'
            tutte.insert(prima_scena, finto)
            inizio = prima_scena
    if inizio is None:
        # nessun titolo d'atto letto: si comincia dalla prima scena
        inizio = next(i for i, r in enumerate(tutte)
                      if re.match(r'S\s?C\s?E\s?N\s?A\s+[A-Z|]+\b', r.testo) and len(r.testo) < 25)
        fini = [r.testo for r in tutte[inizio:] if r.testo.startswith('§FINE')]
        primo = 'PROLOGO' if fini and 'PROLOGO' in fini[0] else (
            'PARTE PRIMA' if fini and 'PARTE' in fini[0] else 'ATTO PRIMO')
        finto = Riga(tutte[inizio].pagina, tutte[inizio].parole[:1])
        finto.testo = primo
        tutte.insert(inizio, finto)
    nomi = nomi_dei_personaggi(tutte[:inizio], tutte[inizio:])
    if os.path.exists(os.path.join(cartella, 'personaggi.txt')):
        # elenco scritto a mano guardando la pagina dei personaggi, quando
        # l'OCR non la legge bene ("Yerrando" per Ferrando)
        with open(os.path.join(cartella, 'personaggi.txt'), encoding='utf-8') as f:
            for n in f.read().split('\n'):
                if n.strip():
                    nomi[n.strip().upper()] += 100
    righe = separa_etichette(tutte[inizio:], nomi)
    maiuscole_le_etichette(righe, nomi)

    # Nomi dei personaggi: la grafia più frequente (con gli accenti) vince.
    varianti = defaultdict(Counter)
    alias = {}
    for r in righe:
        testa = re.split(r'[,.;]', r.testo)[0].strip()
        if maiuscola(testa) and not re.match(r'(ATTO|PARTE|SCENA|PROLOGO)\b', testa):
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

    for indice, r in enumerate(righe):
        t = r.testo.strip()
        if t.startswith('§FINE'):
            fatti = [o for o in out if o.startswith('# ')]
            ultimo = fatti[-1].split() if fatti else ['#', 'Prologo']
            if ultimo[1] == 'Prologo':
                t = 'ATTO PRIMO'
            else:
                lista = ORDINALI_F if ultimo[1] == 'Parte' else ORDINALI
                i = lista.index(ultimo[2]) + 1 if ultimo[2] in lista else 1
                if i >= len(lista):
                    continue
                t = f'{ultimo[1].upper()} {lista[i].upper()}'
        m = re.match(r'(ATTO|PARTE|PROLOGO)\b\W*([A-Z|l]*)\W*(.*)', t)
        if m and len(t) < 45 and (maiuscola(m.group(3)) or len(m.group(3)) <= 2):
            chiudi_prosa()
            vuota()
            tipo, num, resto = m.groups()
            if tipo != 'PROLOGO':
                lista = ORDINALI_F if tipo == 'PARTE' else ORDINALI
                n = numero(num, lista) or 1
                titolo = f'# {tipo.capitalize()} {lista[n - 1]}'
                if titolo in out:
                    continue                 # testatina ripetuta in cima alla pagina
                fatti = [o for o in out if o.startswith('# ')]
                if fatti and (fatti[-1].split()[1] != tipo.capitalize() and fatti[-1] != '# Prologo'
                              or (tipo != 'PROLOGO' and fatti[-1].split()[1] == tipo.capitalize()
                                  and lista.index(fatti[-1].split()[2]) >= n - 1)):
                    break                    # ricomincia la numerazione: è un altro libretto
            if tipo == 'PROLOGO':
                emetti('# Prologo', r)
                resto = ' '.join(x for x in (num, resto) if x)
            elif tipo == 'PARTE':
                n = numero(num, ORDINALI_F) or 1
                emetti(f'# Parte {ORDINALI_F[n - 1]}', r)
            else:
                n = numero(num, ORDINALI) or 1
                emetti(f'# Atto {ORDINALI[n - 1]}', r)
            sc = re.match(r'S\s?C\s?E\s?N\s?A\s+([A-Z|]+)', resto)
            if sc:                                                   # ATTO I. SCENA I.
                n = numero(sc.group(1), ORDINALI_F)
                emetti(f'## Scena {ORDINALI_F[n - 1] if n else sc.group(1).lower()}', r)
            elif len(resto.strip(' .-—')) > 2:
                emetti(f'({tipografia(frase(resto.strip(" .-—")))})', r)   # IL DUELLO
            stato = 'luogo'
            continue
        m = (re.match(r'S\s?C\s?E\s?N\s?A\s+([A-Z|]+)\b', t)
             or re.match(r'Scena\s+([IVXLl|]+|[A-Za-z]+a)\b\W*$', t))   # "Scena IL °", "Scena ultima"
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
            dopo = righe[indice + 1].testo.strip() if indice + 1 < len(righe) else ''
            if (stato is None and dopo and not maiuscola(dopo) and not dopo.startswith('(')
                    and not re.search(r'\b(DETT[OI]|INDI|SOL[OAIE])\b', t)):
                # "RAMPHIS E SACERDOTI." seguito da versi: cantano insieme
                emetti(re.sub(r'[A-ZÀ-Ý]{3,}', lambda m: canonico(m.group()), t).strip(' .,;:'), r)
                stato = None
                continue
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
        if stato == 'prosa' and prosa:
            # la prosa va da margine a margine; una riga rientrata o stretta
            # dopo una frase chiusa è un verso: la didascalia era finita
            larga = max(p.box()[2] for p in prosa)
            rientro = r.box()[0] - min(p.box()[0] for p in prosa)
            chiusa = re.search(r'[.)!?]\W*$', prosa[-1].testo.strip())
            if (chiusa and (rientro > 0.08 * larga or len(prosa) >= 2 and r.box()[2] < 0.6 * larga)
                    or len(prosa) >= 2 and rientro > 0.15 * larga):
                chiudi_prosa()
                stato = None
        if stato in ('luogo', 'prosa'):
            prosa.append(r)
            stato = 'prosa'
            # la didascalia è prosa a tutta riga: una riga corta che chiude la
            # frase è la sua ultima, quel che segue sono versi
            larga = max(p.box()[2] for p in prosa)
            if len(prosa) >= 2 and r.box()[2] < 0.6 * larga and re.search(r'[.)]\W*$', t):
                chiudi_prosa()
                stato = None
            continue
        if (out and out[-1].startswith('(') and ')' not in out[-1] and t[:1].islower()):
            out[-1] += ' ' + tipografia(t)                   # didascalia su due righe
            fonti[-1].append({'pagina': r.pagina, 'box': r.box(), 'parole': r.parole})
            continue
        emetti(tipografia(t), r)

    chiudi_prosa()
    # Nomi abbreviati su una riga loro ("ERN.", "SIL."): si scrivono per intero
    # se un solo nome dell'elenco comincia così.
    for i, o in enumerate(out):
        if fonti[i] and maiuscola(o) and len(o.strip('. ')) <= 5 and not o.startswith('#'):
            k = senza_accenti(o.strip('. '))
            pieni = [n for n in nomi if senza_accenti(n).startswith(k) and n != k]
            if len(pieni) == 1:
                out[i] = pieni[0]
    while out and (out[-1] == '' or out[-1].startswith('# ')):
        out.pop()                     # in fondo: righe vuote e l'atto dopo l'ultimo FINE
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
