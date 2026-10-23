"""Applica le correzioni della revisione.

Uso: python3 applica.py lavoro/aida-cairo assets/libretti/verdi-aida.txt

Legge revisione/dubbi.tsv: nella colonna "correzione" ci va la parola come
è stampata, "=" se l'OCR aveva letto bene, "-" se la parola non c'è nella
stampa (una macchia, un numero di pagina), oppure niente se il dubbio non è
ancora stato guardato. Si ferma se restano dubbi senza risposta.
"""
import csv
import os
import re
import sys

from dubbi import PAROLA


def main():
    cartella, uscita = sys.argv[1], sys.argv[2]
    with open(os.path.join(cartella, 'libretto.txt'), encoding='utf-8') as f:
        righe = f.read().split('\n')
    with open(os.path.join(cartella, 'revisione', 'dubbi.tsv'), encoding='utf-8') as f:
        dubbi = list(csv.DictReader(f, delimiter='\t'))

    aperti = [d['n'] for d in dubbi if not d['correzione'].strip()]
    if aperti:
        sys.exit(f'{len(aperti)} dubbi senza risposta (n. {", ".join(aperti[:10])}...)')

    per_riga = {}
    for d in dubbi:
        if d['correzione'].strip() != '=':
            per_riga.setdefault(int(d['riga']), []).append(d)
    cambiate = 0
    for n, ds in per_riga.items():
        riga = righe[n - 1]
        ms = list(PAROLA.finditer(riga))
        # da destra a sinistra, così le posizioni non si spostano
        for d in sorted(ds, key=lambda d: int(d['pos']), reverse=True):
            m = ms[int(d['pos'])]
            if m.group() != d['parola']:
                sys.exit(f'riga {n}: mi aspettavo "{d["parola"]}", trovo "{m.group()}"')
            nuova = d['correzione'].strip()
            if nuova == '-':
                riga = (riga[:m.start()].rstrip() + ' ' + riga[m.end():].lstrip()).strip()
            else:
                riga = riga[:m.start()] + nuova + riga[m.end():]
            cambiate += 1
        righe[n - 1] = re.sub(r'^[^\w(«"]+', '', riga) if riga.strip() else None
    righe = [r for r in righe if r is not None]
    with open(uscita, 'w', encoding='utf-8') as f:
        f.write('\n'.join(righe))
    print(f'{cambiate} parole corrette, {len(dubbi) - cambiate} confermate')


if __name__ == '__main__':
    main()
