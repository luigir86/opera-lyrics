"""Riporta le risposte di una revisione vecchia su una revisione nuova.

Uso: python3 riprendi.py lavoro/rigoletto libretto-prima.txt revisione-prima

Quando si rifà l'OCR di alcune pagine (un taglio della piega sbagliato, per
esempio) si rilanciano testo.py, dubbi.py e segni.py, che scrivono una
revisione nuova con le colonne "correzione" vuote. Questo script allinea le
parole del vecchio testo con quelle del nuovo (come rimappa.py) e, per ogni
dubbio nuovo che cade sulla stessa parola di un dubbio già risolto, copia la
risposta. Copia anche controllate.txt con i numeri nuovi. Restano vuoti solo
i dubbi davvero nuovi, da far rivedere.
"""
import csv
import os
import sys

from dubbi import PAROLA
from rimappa import PEZZO, mappa, pulito


def leggi_tsv(percorso):
    with open(percorso, encoding='utf-8') as f:
        return list(csv.DictReader(f, delimiter='\t'))


def main():
    cartella, prima, vecchia = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(prima, encoding='utf-8') as f:
        vecchie = f.read().split('\n')
    with open(os.path.join(cartella, 'libretto.txt'), encoding='utf-8') as f:
        nuove = f.read().split('\n')
    rev = os.path.join(cartella, 'revisione')
    fatte = set()
    if os.path.exists(os.path.join(vecchia, 'controllate.txt')):
        with open(os.path.join(vecchia, 'controllate.txt'), encoding='utf-8') as f:
            fatte = set(f.read().split())
    controllate = []
    for nome, regola in (('dubbi.tsv', PAROLA), ('segni.tsv', PEZZO)):
        if not os.path.exists(os.path.join(vecchia, nome)) or not os.path.exists(os.path.join(rev, nome)):
            continue
        m = mappa(vecchie, nuove, regola)
        primi = mappa(vecchie, nuove, PEZZO)
        risposte = {}
        for d in leggi_tsv(os.path.join(vecchia, nome)):
            if not d['correzione'].strip():
                continue
            if d['pos'] == 'nome':
                dove = primi.get((int(d['riga']), 0))
                if dove:
                    risposte[(dove[0] + 1, 'nome', d['parola'])] = d
                continue
            dove = m.get((int(d['riga']), int(d['pos'])))
            if dove:
                risposte[(dove[0] + 1, str(dove[1]), pulito(d['parola']))] = d
        righe = leggi_tsv(os.path.join(rev, nome))
        riprese = 0
        for d in righe:
            chiave = (int(d['riga']), d['pos'],
                      d['parola'] if d['pos'] == 'nome' else pulito(d['parola']))
            vecchio = risposte.get(chiave)
            if vecchio:
                d['correzione'] = vecchio['correzione']
                riprese += 1
                if nome == 'dubbi.tsv' and vecchio['n'] in fatte:
                    controllate.append(d['n'])
        with open(os.path.join(rev, nome), 'w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(righe[0].keys()), delimiter='\t',
                               lineterminator='\n')
            w.writeheader()
            w.writerows(righe)
        print(f'{nome}: {riprese} risposte riprese, {len(righe) - riprese} da rivedere')
    if controllate:
        with open(os.path.join(rev, 'controllate.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(controllate) + '\n')


if __name__ == '__main__':
    main()
