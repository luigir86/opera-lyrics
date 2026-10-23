"""Applica le correzioni della revisione.

Uso: python3 applica.py lavoro/aida-cairo assets/libretti/verdi-aida.txt

Legge revisione/dubbi.tsv (e revisione/segni.tsv, se c'è): nella colonna "correzione" ci va la parola come
è stampata, "=" se l'OCR aveva letto bene, "-" se la parola non c'è nella
stampa (una macchia, un numero di pagina), oppure niente se il dubbio non è
ancora stato guardato. Si ferma se restano dubbi senza risposta.
"""
import csv
import os
import re
import sys

from dubbi import PAROLA
from verifica import ripara


def leggi_tsv(percorso):
    if not os.path.exists(percorso):
        return []
    with open(percorso, encoding='utf-8') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def main():
    cartella, uscita = sys.argv[1], sys.argv[2]
    with open(os.path.join(cartella, 'libretto.txt'), encoding='utf-8') as f:
        righe = f.read().split('\n')
    rev = os.path.join(cartella, 'revisione')
    dubbi = leggi_tsv(os.path.join(rev, 'dubbi.tsv'))
    segni = leggi_tsv(os.path.join(rev, 'segni.tsv'))

    for nome, tabella in (('dubbi', dubbi), ('segni', segni)):
        aperti = [d['n'] for d in tabella if not d['correzione'].strip()]
        if aperti:
            sys.exit(f'{nome}: {len(aperti)} senza risposta (n. {", ".join(aperti[:10])}...)')

    per_riga = {}
    for d in dubbi:
        if d['correzione'].strip() != '=':
            per_riga.setdefault(int(d['riga']), []).append(('parola', d))
    for d in segni:
        if d['correzione'].strip() != '=':
            per_riga.setdefault(int(d['riga']), []).append(('segno', d))
    cambiate = 0
    prima = {}          # riga -> nome di personaggio da mettere prima
    for n, ds in per_riga.items():
        riga = righe[n - 1]
        nomi = [d for k, d in ds if d['pos'] == 'nome']
        if nomi:                      # nome di personaggio: si cambia la riga intera
            nuova = nomi[0]['correzione'].strip().lstrip('>').strip()
            righe[n - 1] = None if nuova == '-' else nuova.upper()
            cambiate += 1
            continue
        # ogni correzione è un pezzo della riga originale (inizio, fine) da
        # sostituire; un segno vince sulla parola che contiene ("i0" e "i")
        parole = list(PAROLA.finditer(riga))
        pezzi = list(re.finditer(r'\S+', riga))
        modifiche = []
        for k, d in ds:
            m = (parole if k == 'parola' else pezzi)[int(d['pos'])]
            if m.group() != d['parola']:
                sys.exit(f'riga {n}: mi aspettavo "{d["parola"]}", trovo "{m.group()}"')
            nuova = ripara(d, righe) if k == 'parola' else d['correzione'].strip()
            modifiche.append((k, m, re.sub(r"'\s+", "'", nuova)))
        segnati = [m for k, m, _ in modifiche if k == 'segno']
        modifiche = [x for x in modifiche if x[0] == 'segno' or not any(
            s.start() <= x[1].start() and x[1].end() <= s.end() for s in segnati)]
        # da destra a sinistra, così le posizioni non si spostano
        for k, m, nuova in sorted(modifiche, key=lambda x: x[1].start(), reverse=True):
            if nuova.startswith('>'):
                # era il nome di chi canta, a inizio verso: va su una riga sua
                riga = riga[m.end():].lstrip(' .,:')
                prima.setdefault(n, nuova[1:].strip().upper())
                cambiate += 1
                continue
            if nuova.lower() == m.group().lower():
                continue    # solo maiuscole diverse: si tiene la forma del testo
            if nuova == '-':
                riga = (riga[:m.start()].rstrip() + ' ' + riga[m.end():].lstrip()).strip()
            else:
                riga = riga[:m.start()] + nuova + riga[m.end():]
            cambiate += 1
        riga = re.sub(r"(\w')\s+(?=\w)", r'\1', riga)      # l' eguale -> l'eguale
        riga = re.sub(r"\b(\w{1,3}')\1", r'\1', riga, flags=re.I)   # l'l'amor: segno e parola
        righe[n - 1] = re.sub(r'^[^\w(«"]+', '', riga) if riga.strip() else None
    for n in sorted(prima, reverse=True):
        righe[n - 1:n - 1] = ['', prima[n]] if righe[n - 2] else [prima[n]]
    righe = [r for r in righe if r is not None]
    with open(uscita, 'w', encoding='utf-8') as f:
        f.write('\n'.join(righe))
    tutte = len(dubbi) + len(segni)
    print(f'{cambiate} correzioni, {tutte - cambiate} confermate')


if __name__ == '__main__':
    main()
