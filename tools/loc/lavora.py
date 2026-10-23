"""Tutti i passi automatici per le opere di un elenco, fino alla revisione.

Uso: python3 lavora.py verdi.tsv lavoro/verdi [file...]

Per ogni riga dell'elenco (file, scheda principale, scheda di confronto,
titolo, anno della prima) usa le cartelle lavoro/verdi/<file>-a e -b, già
riempite da scarica.py, e fa: OCR delle due edizioni, intestazione, testo
nel formato dell'app, dubbi. Si possono indicare solo alcune opere.
Alla fine stampa un riassunto per opera.
"""
import json
import os
import re
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
LICENZA = 'Pubblico dominio (Library of Congress, Music Division); trascrizione CC0'


def esegui(*args):
    r = subprocess.run([sys.executable, *args], cwd=QUI, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr.strip().splitlines()[-1] if r.stderr else 'errore')
    return r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ''


def librettista(cartella):
    with open(os.path.join(cartella, 'item.json'), encoding='utf-8') as f:
        nomi = json.load(f)['item'].get('contributor_names', [])
    for n in nomi:
        if n.endswith('librettist'):
            parti = [p.strip() for p in n.split(',')]
            cognome, nome = parti[0], parti[1] if len(parti) > 2 else ''
            if re.match(r'\d', nome):
                nome = ''
            return f'{nome} {cognome}'.strip()
    return None


def intestazione(cartella, titolo, anno, scheda):
    righe = [f'title: {titolo}', 'composer: Giuseppe Verdi']
    lib = librettista(cartella)
    if lib:
        righe.append(f'librettist: {lib}')
    righe += [f'year: {anno}', f'source: https://www.loc.gov/item/{scheda}/',
              f'license: {LICENZA}']
    dest = os.path.join(cartella, 'intestazione.txt')
    with open(dest, 'w', encoding='utf-8') as f:
        f.write('\n'.join(righe) + '\n')
    return dest


def main():
    elenco, base, scelte = sys.argv[1], sys.argv[2], set(sys.argv[3:])
    for riga in open(os.path.join(QUI, elenco), encoding='utf-8'):
        if riga.startswith('#') or not riga.strip():
            continue
        nome, a, b, titolo, anno = riga.rstrip('\n').split('\t')
        if scelte and nome not in scelte:
            continue
        ca, cb = os.path.join(base, nome + '-a'), os.path.join(base, nome + '-b')
        try:
            for c in (ca, cb):
                if not os.path.exists(os.path.join(c, 'pagine.json')):
                    esegui('ocr.py', c)
            print(f'{nome}: {esegui("testo.py", ca, intestazione(ca, titolo, anno, a))}')
            try:
                esegui('testo.py', cb, intestazione(cb, titolo, anno, b))
                print(f'  {esegui("dubbi.py", ca, cb)}')
            except (RuntimeError, StopIteration):
                # l'edizione di confronto non ha dato testo italiano: si va senza
                print(f'  senza confronto: {esegui("dubbi.py", ca)}')
        except (RuntimeError, OSError, StopIteration) as e:
            print(f'{nome}: ERRORE {e}')


if __name__ == '__main__':
    main()
