"""Pilota della revisione strutturata: il modello riscrive il libretto a blocchi, solo testo.

Uso: python3 ricostruisci.py <cartella opera> <modello> [righe per blocco]
Legge parole.txt e personaggi.txt, scrive <modello>.txt, <modello>-blocchi.json.
"""
import difflib
import json
import os
import re
import subprocess
import sys

SISTEMA = "Sei un curatore esperto di libretti d'opera italiani dell'Ottocento. Ricostruisci la struttura di testi usciti dall'OCR senza inventare nulla."

REGOLE = """Ti do un pezzo di libretto uscito dall'OCR di una stampa dell'Ottocento, con le parole già corrette. La struttura invece è sporca. Riscrivilo nel formato dell'app:

- `# Atto ...` inizio atto, `## Scena ...` inizio scena: tienili dove sono. Se la numerazione delle scene salta o si ripete, correggila in sequenza.
- Una riga TUTTA MAIUSCOLA è il nome di chi canta, da sola su una riga, preceduta da una riga vuota. Usa SOLO i nomi completi dell'elenco personaggi (più CORO, TUTTI, e combinazioni con E, per esempio "LUISA E LAURA"). Le sigle della stampa (Lui., Mil., Cono e Lau.) diventano nomi completi; se una sigla è all'inizio di un verso ("Lui. Padre!"), il nome va su una riga sua.
- Una riga in maiuscolo che in realtà è l'inizio di un verso (DIE, MA, DI) non è un nome: torna verso, con le maiuscole normali.
- Didascalie e indicazioni sceniche tra parentesi tonde, ognuna su una riga sua, sotto il nome di chi canta o tra i versi dove sono stampate. Una didascalia spezzata su più righe va riunita in una sola riga tra parentesi.
- Un verso per riga: riunisci i versi spezzati dall'OCR (riga che continua in minuscolo la precedente) e separa quelli fusi solo se è evidente.
- Togli il rumore: numeri di pagina, testatine, lettere isolate, righe senza senso che non sono testo del libretto.
- Correggi solo errori OCR evidenti di una o due lettere (cd -> ed, quesl'aura -> quest'aura, de'cori -> de' cori, E / pura -> È pura). Non modernizzare la grafia (ne', cor, gioja restano), non riscrivere, non aggiungere parole che non ci sono, non completare versi mancanti.
- Non aggiungere commenti o spiegazioni.

Personaggi dell'opera (a destra di = le sigle lette dall'OCR):
{personaggi}

{contesto}Pezzo da sistemare:
<testo>
{blocco}
</testo>

Rispondi SOLO con il pezzo sistemato tra <testo> e </testo>."""


def blocchi(righe, n):
    """Divide il corpo (dopo l'intestazione) in blocchi che iniziano a un '## ' o '# '."""
    inizio = next(i for i, r in enumerate(righe) if r.startswith('# '))
    testa, corpo = righe[:inizio], righe[inizio:]
    out, cur = [], []
    for r in corpo:
        piene = len([x for x in cur if x.strip()])
        if ((r.startswith('## ') or r.startswith('# ')) and piene >= n) or r.startswith('# ') and piene \
                or (not r.strip() and piene >= 1.5 * n):
            out.append(cur)
            cur = []
        cur.append(r)
    if cur:
        out.append(cur)
    return testa, out


def chiama(modello, testo):
    r = subprocess.run(['claude', '-p', '--model', modello, '--system-prompt', SISTEMA, '--tools', '',
                        '--output-format', 'json', '--no-session-persistence'],
                       input=testo, capture_output=True, text=True, timeout=900)
    d = json.loads(r.stdout)
    m = re.search(r'<testo>\n?(.*?)\n?</testo>', d.get('result') or '', re.S)
    return (m.group(1) if m else None), d.get('total_cost_usd', 0), d.get('usage', {})


PAR = re.compile(r"[A-Za-zÀ-ÿ]+")


def parole_nuove(vecchio, nuovo):
    """Parole del testo nuovo che non somigliano a nessuna del vecchio (possibili invenzioni)."""
    v = set(w.lower() for w in PAR.findall(vecchio))
    nuove = []
    for w in PAR.findall(nuovo):
        lw = w.lower()
        if lw in v or len(lw) <= 2:
            continue
        if not difflib.get_close_matches(lw, v, n=1, cutoff=0.75):
            nuove.append(w)
    return nuove


def main():
    cartella, modello = sys.argv[1], sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 150
    righe = open(os.path.join(cartella, 'parole.txt'), encoding='utf-8').read().split('\n')
    personaggi = open(os.path.join(cartella, 'personaggi.txt'), encoding='utf-8').read().strip()
    testa, bl = blocchi(righe, n)
    uscita, info, prec = list(testa), [], []
    for i, b in enumerate(bl):
        contesto = ''
        if prec:
            contesto = 'Fine del pezzo precedente, già sistemato (solo per contesto, non ripeterlo):\n<contesto>\n' + '\n'.join(prec[-15:]) + '\n</contesto>\n\n'
        vecchio = '\n'.join(b)
        parte = os.path.join(cartella, f'{modello}-parti', f'{i:03d}.json')
        if os.path.exists(parte):
            d = json.load(open(parte))
            info.append(d['info'])
            uscita += d['testo'].split('\n')
            prec = d['testo'].split('\n')
            continue
        prompt = REGOLE.format(personaggi=personaggi, contesto=contesto, blocco=vecchio)
        nuovo, costo, u = None, 0, {}
        for _ in range(2):
            try:
                nuovo, c, u = chiama(modello, prompt)
                costo += c
            except Exception as e:  # noqa: BLE001
                u = {'errore': str(e)[:200]}
            if nuovo is not None:
                break
        if nuovo is None:
            nuovo = vecchio
        nuove = parole_nuove(vecchio, nuovo)
        info.append({'blocco': i, 'righe': len(b), 'costo': costo, 'parole_nuove': nuove,
                     'ingresso': u.get('input_tokens'), 'uscita': u.get('output_tokens')})
        os.makedirs(os.path.dirname(parte), exist_ok=True)
        json.dump({'info': info[-1], 'testo': nuovo}, open(parte, 'w'), ensure_ascii=False)
        uscita += nuovo.split('\n')
        prec = nuovo.split('\n')
        print(f'{os.path.basename(cartella)} {modello} blocco {i + 1}/{len(bl)} ${costo:.3f} nuove={len(nuove)}', flush=True)
    open(os.path.join(cartella, f'{modello}.txt'), 'w', encoding='utf-8').write('\n'.join(uscita).rstrip('\n') + '\n')
    json.dump(info, open(os.path.join(cartella, f'{modello}-blocchi.json'), 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
