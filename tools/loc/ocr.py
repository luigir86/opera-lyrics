"""OCR delle pagine scaricate, tenendo solo il testo italiano.

Uso: python3 ocr.py lavoro/aida-cairo

Per ogni immagine in pagine/: toglie il bordo nero della scansione, divide le
doppie pagine sulla piega e passa ogni metà a Tesseract (modello italiano).
Tiene le metà che il dizionario italiano riconosce: nei libretti bilingui
l'altra lingua viene scartata da sola, in quelli solo italiani si tengono
entrambe le pagine.

Scrive ita/NNNNa.png e NNNNb.png (pagina sinistra e destra; le coordinate
dell'OCR si riferiscono a queste immagini), ocr/NNNNa.tsv e NNNNb.tsv e
pagine.json con il riassunto.
Richiede: tesseract-ocr, tesseract-ocr-ita, hunspell, hunspell-it, Pillow.
"""
import csv
import io
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor

from PIL import Image, ImageOps

SOGLIA_ITALIANO = 0.6  # quota minima di parole riconosciute dal dizionario
TEMPO = 90            # secondi massimi di OCR per mezza pagina


def togli_bordo(im):
    """Taglia le fasce quasi nere ai margini della scansione."""
    g = im.convert('L')
    w, h = g.size
    piccola = g.resize((max(1, w // 4), max(1, h // 4)))
    pw, ph = piccola.size
    px = piccola.load()
    col = [sum(px[x, y] for y in range(ph)) / ph for x in range(pw)]
    rig = [sum(px[x, y] for x in range(pw)) / pw for y in range(ph)]

    def limiti(v):
        chiaro = [i for i, m in enumerate(v) if m > 110]
        return (chiaro[0], chiaro[-1] + 1) if chiaro else (0, len(v))
    x0, x1 = limiti(col)
    y0, y1 = limiti(rig)
    return g.crop((x0 * 4, y0 * 4, x1 * 4, y1 * 4))


def piega(g):
    """Ascissa della piega in una doppia pagina.

    La piega è scura lungo tutta l'altezza, mentre una colonna di testo è
    chiara tra una riga e l'altra: si prende la colonna centrale con la
    mediana più scura.
    """
    w, h = g.size
    piccola = g.resize((max(1, w // 4), max(1, h // 4)))
    pw, ph = piccola.size
    px = piccola.load()
    a, b = int(pw * 0.38), int(pw * 0.62)
    mediane = {x: sorted(px[x, y] for y in range(ph))[ph // 2] for x in range(a, b)}
    liscia = {x: sum(mediane.get(x + d, 255) for d in (-1, 0, 1)) for x in mediane}
    return min(liscia, key=liscia.get) * 4


def tesseract(im):
    buf = io.BytesIO()
    im.save(buf, format='PNG')
    try:
        r = subprocess.run(['tesseract', 'stdin', 'stdout', '-l', 'ita', '--psm', '4', 'tsv'],
                           input=buf.getvalue(), capture_output=True, check=True, timeout=TEMPO,
                           env={**os.environ, 'OMP_THREAD_LIMIT': '1'})
    except subprocess.TimeoutExpired:
        return ''            # pagine illustrate o macchiate: Tesseract si perde
    return r.stdout.decode('utf-8')


def parole(tsv):
    out = []
    for r in csv.DictReader(io.StringIO(tsv), delimiter='\t', quoting=csv.QUOTE_NONE):
        if r.get('level') == '5' and (r['text'] or '').strip():
            out.append(r['text'])
    return out


def sconosciute(words):
    """Parole che il dizionario italiano non riconosce."""
    if not words:
        return set()
    r = subprocess.run(['hunspell', '-d', 'it_IT', '-l'], input='\n'.join(words),
                       capture_output=True, text=True, check=True)
    return set(r.stdout.split())


def quota_italiana(tsv):
    ws = [m for w in parole(tsv) for m in re.findall(r"[A-Za-zÀ-ÿ]{3,}", w)]
    ws = [w for w in ws if not w.isupper()]       # i nomi dei personaggi non contano
    if len(ws) < 5:
        return 0.0, len(ws)
    ignote = sconosciute(ws)
    return sum(w not in ignote for w in ws) / len(ws), len(ws)


def una_pagina(args):
    cartella, nome = args
    n = nome[:-4]
    im = ImageOps.exif_transpose(Image.open(os.path.join(cartella, 'pagine', nome)))
    g = togli_bordo(im)
    w, h = g.size
    if w > h * 1.1:
        x = piega(g)
        meta = {'a': g.crop((0, 0, x, h)), 'b': g.crop((x, 0, w, h))}
    else:
        meta = {'a': g}
    info = {}
    for lato, img in meta.items():
        tsv = tesseract(img)
        quota, conte = quota_italiana(tsv)
        tenuta = quota >= SOGLIA_ITALIANO
        if tenuta:
            img.save(os.path.join(cartella, 'ita', f'{n}{lato}.png'))
            with open(os.path.join(cartella, 'ocr', f'{n}{lato}.tsv'), 'w', encoding='utf-8') as f:
                f.write(tsv)
        info[lato] = {'italiano': round(quota, 2), 'parole': conte, 'tenuta': tenuta}
    return n, info


def main():
    cartella = sys.argv[1]
    for d in ('ita', 'ocr'):
        os.makedirs(os.path.join(cartella, d), exist_ok=True)
        for vecchio in os.listdir(os.path.join(cartella, d)):
            os.remove(os.path.join(cartella, d, vecchio))
    nomi = sorted(f for f in os.listdir(os.path.join(cartella, 'pagine')) if f.endswith('.jpg'))
    riassunto = {}
    with ProcessPoolExecutor() as ex:
        for n, info in ex.map(una_pagina, [(cartella, x) for x in nomi]):
            riassunto[n] = info
            print(n, info)
    with open(os.path.join(cartella, 'pagine.json'), 'w', encoding='utf-8') as f:
        json.dump(riassunto, f, indent=1)


if __name__ == '__main__':
    main()
