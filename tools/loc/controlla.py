"""Controlla un libretto come fa l'app, e segnala ciò che va guardato a mano.

Uso: python3 controlla.py assets/libretti/verdi-aida.txt [...]

Ripete i controlli di test/libretti_test.dart (intestazione completa, atti con
versi) con le stesse regole di lib/library/libretto_parser.dart, poi elenca
gli atti e i personaggi che compaiono una volta sola (spesso un nome storpiato
dall'OCR) e le righe che sembrano rumore.
"""
import re
import sys
from collections import Counter


def ruolo(riga):
    lettere = ''.join(c for c in riga if c.isalpha())
    return len(lettere) >= 2 and lettere == lettere.upper() and lettere != lettere.lower()


def controlla(percorso):
    testa, atti, problemi = {}, [], []
    ruoli = Counter()
    rumore = []
    atto = None
    with open(percorso, encoding='utf-8') as f:
        for n, raw in enumerate(f, 1):
            r = raw.strip()
            if r.startswith('//'):
                continue
            if r.startswith('## '):
                if atto is None:
                    atto = ['', 0]
                    atti.append(atto)
            elif r.startswith('# '):
                atto = [r[2:].strip(), 0]
                atti.append(atto)
            elif atto is None:
                if ':' in r:
                    k, v = r.split(':', 1)
                    testa[k.strip().lower()] = v.strip()
            elif not r or (r.startswith('(') and r.endswith(')')):
                continue
            elif ruolo(r):
                ruoli[r] += 1
            else:
                atto[1] += 1
                if len(re.findall(r'[A-Za-zÀ-ÿ]', r)) < 3:
                    rumore.append(f'{n}: {r}')
    for k in ('title', 'composer', 'source', 'license'):
        if not testa.get(k):
            problemi.append(f'manca {k}:')
    if not atti:
        problemi.append('nessun atto')
    for titolo, versi in atti:
        if not titolo:
            problemi.append('atto senza titolo')
        if not versi:
            problemi.append(f'"{titolo}" senza versi')
    print(f'{percorso}: {"OK" if not problemi else "; ".join(problemi)}')
    print('  atti: ' + ', '.join(f'{t} ({v} versi)' for t, v in atti))
    rari = [r for r, c in ruoli.items() if c == 1]
    if rari:
        print('  personaggi una volta sola: ' + ', '.join(rari))
    if rumore:
        print('  righe sospette: ' + ' | '.join(rumore[:12]))
    return not problemi


if __name__ == '__main__':
    ok = all([controlla(p) for p in sys.argv[1:]])
    sys.exit(0 if ok else 1)
