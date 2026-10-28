"""Ultimi ritocchi deterministici sul libretto ricostruito.

Uso: python3 rifinisci.py <entrata> <uscita> [personaggi.txt]
- rinumera le scene di ogni atto in sequenza (Scena prima, seconda...);
- toglie le righe vuote subito dopo un titolo e quelle doppie;
- porta le sigle rimaste ai nomi completi di personaggi.txt (NOME = SIG1, SIG2).
"""
import re
import sys

ORD = ['prima', 'seconda', 'terza', 'quarta', 'quinta', 'sesta', 'settima', 'ottava', 'nona', 'decima',
       'undicesima', 'dodicesima', 'tredicesima', 'quattordicesima', 'quindicesima', 'sedicesima',
       'diciassettesima', 'diciottesima', 'diciannovesima', 'ventesima']


def main():
    entrata, uscita = sys.argv[1], sys.argv[2]
    mappa = {}
    if len(sys.argv) > 3:
        for r in open(sys.argv[3], encoding='utf-8'):
            if '=' in r:
                nome, sigle = r.split('=', 1)
                nome = re.sub(r'\s*\(.*', '', nome).strip()
                for s in re.sub(r'\(.*?\)', '', sigle).split(','):
                    s = s.strip().rstrip('.').upper()
                    if s and s != nome:
                        mappa[s] = nome
    righe = open(entrata, encoding='utf-8').read().split('\n')
    out, scena = [], 0
    for r in righe:
        if r.startswith('# '):
            scena = 0
        elif r.startswith('## Scena'):
            r = '## Scena ' + (ORD[scena] if scena < len(ORD) else str(scena + 1))
            scena += 1
        elif r.strip() in mappa:
            r = mappa[r.strip()]
        if not r.strip() and out and (not out[-1].strip() or out[-1].startswith('## ')):
            continue
        out.append(r)
    open(uscita, 'w', encoding='utf-8').write('\n'.join(out).rstrip('\n') + '\n')


if __name__ == '__main__':
    main()
