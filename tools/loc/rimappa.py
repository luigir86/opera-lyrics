"""Riporta le risposte della revisione su un testo rigenerato.

Uso: python3 rimappa.py lavoro/aida-cairo libretto-prima.txt

Se testo.py migliora mentre la revisione è in corso o finita, il testo
rigenerato ha le stesse parole nello stesso ordine ma divise in righe
diverse (una didascalia che inglobava dei versi, per esempio), e le colonne
"riga" e "pos" di dubbi.tsv e segni.tsv non tornano più. Questo script
allinea le parole del vecchio testo (libretto-prima.txt) con quelle del nuovo
(libretto.txt) e aggiorna riga e pos. Le righe che non si ritrovano vengono
tolte e stampate, da rivedere a mano.
"""
import csv
import os
import re
import sys
from difflib import SequenceMatcher

from dubbi import PAROLA, norm, ruolo

PEZZO = re.compile(r'\S+')


def gettoni(righe, regola):
    return [(i, k, m.group()) for i, r in enumerate(righe)
            for k, m in enumerate(regola.finditer(r))]


def pulito(w):
    return norm(w).strip('()«»".,;:!?')


def mappa(vecchie, nuove, regola):
    a, b = gettoni(vecchie, regola), gettoni(nuove, regola)
    sm = SequenceMatcher(None, [pulito(w) for *_, w in a], [pulito(w) for *_, w in b],
                         autojunk=False)
    m = {}
    for blocco in sm.get_matching_blocks():
        for t in range(blocco.size):
            i, k, _ = a[blocco.a + t]
            m[(i + 1, k)] = b[blocco.b + t]
    return m


def main():
    cartella, prima = sys.argv[1], sys.argv[2]
    with open(prima, encoding='utf-8') as f:
        vecchie = f.read().split('\n')
    with open(os.path.join(cartella, 'libretto.txt'), encoding='utf-8') as f:
        nuove = f.read().split('\n')
    for nome, regola in (('dubbi.tsv', PAROLA), ('segni.tsv', PEZZO)):
        percorso = os.path.join(cartella, 'revisione', nome)
        if not os.path.exists(percorso):
            continue
        with open(percorso, encoding='utf-8') as f:
            righe = list(csv.DictReader(f, delimiter='\t'))
        m = mappa(vecchie, nuove, regola)
        primi = mappa(vecchie, nuove, PEZZO)
        tenute, perse = [], []
        for d in righe:
            if d['pos'] == 'nome':
                # il nome di personaggio è una riga intera: si cerca la riga
                # dove è finito il suo primo pezzo
                # (anche se il nuovo testo lo scrive diverso, "FEN" -> "FERRANDO":
                # la risposta resta giusta)
                dove = primi.get((int(d['riga']), 0))
                if not dove:
                    # il nome cambiato non si allinea: si guarda dove è finita
                    # la riga dopo, e si prende la riga di nome che la precede
                    dopo = next((primi[(r, 0)] for r in range(int(d['riga']) + 1, int(d['riga']) + 4)
                                 if (r, 0) in primi), None)
                    if dopo:
                        j = dopo[0] - 1
                        while j > 0 and not nuove[j].strip():
                            j -= 1
                        dove = (j, 0, nuove[j])
                if dove and (nuove[dove[0]].strip() == d['parola'] or ruolo(nuove[dove[0]])):
                    d['riga'], d['parola'] = str(dove[0] + 1), nuove[dove[0]].strip()
                    tenute.append(d)
                else:
                    perse.append(d)
                continue
            dove = m.get((int(d['riga']), int(d['pos'])))
            if dove and pulito(dove[2]) == pulito(d['parola']):
                d['riga'], d['pos'], d['parola'] = str(dove[0] + 1), str(dove[1]), dove[2]
                if 'riga_letta' in d:
                    d['riga_letta'] = nuove[dove[0]]
                tenute.append(d)
            else:
                perse.append(d)
        with open(percorso, 'w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(righe[0].keys()), delimiter='\t',
                               lineterminator='\n')
            w.writeheader()
            w.writerows(tenute)
        print(f'{nome}: {len(tenute)} riportate, {len(perse)} perse')
        for d in perse:
            print(f"  n. {d['n']}: {d['parola']} -> {d['correzione']}")


if __name__ == '__main__':
    main()
