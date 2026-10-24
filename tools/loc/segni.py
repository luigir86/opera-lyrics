"""Trova i segni che non sono parole: cifre e simboli letti dall'OCR.

Uso: python3 segni.py lavoro/aida-cairo

dubbi.py guarda solo le parole fatte di lettere, così un "0" letto al posto
di "O", un "1" al posto di "I" o di "!" e le macchie lette come "°" o "|"
restano nel testo. Questo script segnala ogni pezzo di riga (tra due spazi)
che contiene una cifra o un simbolo strano, e scrive revisione/segni.tsv
con i ritagli S-NNNN.jpg, nello stesso formato di dubbi.tsv: chi rivede
scrive nella colonna "correzione" il pezzo come è stampato, "=" se è
giusto, "-" se nella stampa non c'è. Non tocca dubbi.tsv, quindi si può
lanciare anche mentre la revisione delle parole è in corso.
"""
import csv
import os
import re
import sys

from dubbi import leggi, ritaglio, struttura

STRANO = re.compile(r'[0-9°|_*©€@+{}$/<>®\\=\[\]%&£^~#]')


def main():
    cartella = sys.argv[1]
    righe, fonti = leggi(cartella)
    segni = []
    for i, r in enumerate(righe):
        if i >= len(fonti) or not fonti[i] or struttura(r):
            continue
        for k, m in enumerate(re.finditer(r'\S+', r)):
            if STRANO.search(m.group()):
                segni.append((i + 1, k, m.group()))
    rev = os.path.join(cartella, 'revisione')
    os.makedirs(rev, exist_ok=True)
    for vecchio in os.listdir(rev):
        if vecchio.startswith('S-'):
            os.remove(os.path.join(rev, vecchio))
    with open(os.path.join(rev, 'segni.tsv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, delimiter='\t', lineterminator='\n')
        w.writerow(['n', 'riga', 'pos', 'parola', 'riga_letta', 'ritaglio', 'correzione'])
        for n, (riga, pos, pezzo) in enumerate(segni, 1):
            nome = f'S-{n:04d}.jpg'
            ritaglio(cartella, fonti[riga - 1], pezzo.strip('.,;:!?()«»"') or pezzo).save(os.path.join(rev, nome), quality=80)
            w.writerow([n, riga, pos, pezzo, righe[riga - 1], nome, ''])
    print(f'{len(segni)} segni da rivedere')


if __name__ == '__main__':
    main()
