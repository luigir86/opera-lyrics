"""Controlla le risposte della revisione prima di applicarle.

Uso: python3 verifica.py lavoro/aida-cairo

Segnala le correzioni sospette, da riguardare sul ritaglio:
- doppione: la correzione ripete la parola vicina (prima o dopo nella riga,
  o la prima della riga seguente). Succede quando la parola dell'OCR è una
  macchia e chi rivede scrive la parola accanto invece di "-";
- lontana: la correzione non somiglia per niente alla parola letta dall'OCR.
Scrive revisione/sospette.tsv con le stesse colonne di dubbi.tsv. I numeri
già riguardati si scrivono in revisione/controllate.txt (uno per riga) e non
vengono più segnalati.
"""
import csv
import os
import sys
from difflib import SequenceMatcher

from dubbi import PAROLA, norm


def ripara(d, righe):
    """La correzione senza la parola che segue, se chi rivede l'ha attaccata.

    "l°" + "eguale" letti come due parole: la risposta giusta per "l" è
    "l'", non "l'eguale" (che ripeterebbe "eguale").
    """
    c = d['correzione'].strip()
    if d['pos'] == 'nome' or c in ('=', '-') or c.startswith('>'):
        return c
    parole = [m.group() for m in PAROLA.finditer(righe[int(d['riga']) - 1])]
    k = int(d['pos'])
    if k + 1 < len(parole):
        dopo = parole[k + 1]
        if len(c) > len(dopo) and norm(c).endswith(norm(dopo)) and norm(c) != norm(d['parola']):
            return c[:-len(dopo)].rstrip()
    return c


def sospetto(d, righe):
    c = ripara(d, righe)
    if d['pos'] == 'nome' or c in ('=', '-') or c.startswith('>'):
        return None
    n = int(d['riga'])
    parole = [m.group() for m in PAROLA.finditer(righe[n - 1])]
    k = int(d['pos'])
    vicine = parole[max(0, k - 1):k] + parole[k + 1:k + 2]
    seguente = next((r for r in righe[n:] if r.strip()), '')
    prima = PAROLA.search(seguente)
    if prima:
        vicine.append(prima.group())
    if norm(c) in {norm(v) for v in vicine} and norm(c) != norm(d['parola']):
        return 'doppione'
    if SequenceMatcher(None, norm(c), norm(d['parola'])).ratio() < 0.34:
        return 'lontana'
    return None


def main():
    cartella = sys.argv[1]
    with open(os.path.join(cartella, 'libretto.txt'), encoding='utf-8') as f:
        righe = f.read().split('\n')
    rev = os.path.join(cartella, 'revisione')
    with open(os.path.join(rev, 'dubbi.tsv'), encoding='utf-8') as f:
        dubbi = list(csv.DictReader(f, delimiter='\t'))
    fatte = set()
    if os.path.exists(os.path.join(rev, 'controllate.txt')):
        with open(os.path.join(rev, 'controllate.txt'), encoding='utf-8') as f:
            fatte = set(f.read().split())
    trovate = []
    for d in dubbi:
        if d['correzione'].strip() and d['n'] not in fatte:
            m = sospetto(d, righe)
            if m:
                trovate.append({**d, 'motivi': m})
    with open(os.path.join(rev, 'sospette.tsv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(dubbi[0].keys()), delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(trovate)
    for d in trovate:
        print(f"{d['n']}\t{d['motivi']}\t{d['parola']} -> {ripara(d, righe)}")
    print(f'{len(trovate)} correzioni sospette su {len(dubbi)}')


if __name__ == '__main__':
    main()
