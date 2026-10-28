"""Scrive personaggi.txt dalle etichette lette dall'OCR, con Sonnet (solo testo).

Uso: python3 personaggi.py <cartella opera>
"""
import collections
import json
import os
import re
import subprocess
import sys

from ricostruisci import SISTEMA

PROMPT = """Questo è un libretto d'opera ({titolo}, {compositore}) uscito dall'OCR. Ti do l'inizio del testo, dove di solito c'è l'elenco dei personaggi, e tutte le righe in maiuscolo che l'OCR ha preso per nomi di chi canta, con quante volte compaiono.

Scrivi l'elenco dei personaggi che cantano, uno per riga, con il nome completo in maiuscolo come nella stampa, e dopo " = " le sigle o storpiature dell'OCR che corrispondono a quel personaggio, separate da virgole. Aggiungi CORO se c'è un coro. Non mettere nell'elenco le righe che non sono personaggi (intestazioni, parole di un verso, numeri).

Inizio del testo:
<inizio>
{inizio}
</inizio>

Etichette lette (volte):
{etichette}

Rispondi SOLO con l'elenco, nella forma:
NOME COMPLETO = SIG, SIGLA2"""


def ruolo(x):
    lett = ''.join(c for c in x if c.isalpha())
    return len(lett) >= 2 and lett == lett.upper() and not x.startswith('#')


def main():
    cartella = sys.argv[1]
    righe = open(os.path.join(cartella, 'parole.txt'), encoding='utf-8').read().split('\n')
    testa = {k.strip(): v.strip() for k, v in (r.split(':', 1) for r in righe if re.match(r'^\w+:', r))}
    conta = collections.Counter(r.strip() for r in righe if ruolo(r.strip()))
    eti = '\n'.join(f'{k} ({v})' for k, v in conta.most_common(80))
    inizio = '\n'.join(righe[:120])
    p = PROMPT.format(titolo=testa.get('title', ''), compositore=testa.get('composer', ''), inizio=inizio, etichette=eti)
    r = subprocess.run(['claude', '-p', '--model', 'sonnet', '--system-prompt', SISTEMA, '--tools', '',
                        '--output-format', 'json', '--no-session-persistence'],
                       input=p, capture_output=True, text=True, timeout=600)
    d = json.loads(r.stdout)
    testo = '\n'.join(x for x in (d.get('result') or '').split('\n') if x.strip() and not x.startswith('```'))
    open(os.path.join(cartella, 'personaggi.txt'), 'w', encoding='utf-8').write(testo + '\n')
    print(os.path.basename(cartella), f"${d.get('total_cost_usd', 0):.3f}")
    print(testo)


if __name__ == '__main__':
    main()
