"""Scarica le pagine di un libretto della Library of Congress.

Uso: python3 scarica.py 2010657556 lavoro/aida-cairo

Crea nella cartella item.json (la scheda) e pagine/0001.jpg, 0002.jpg, ...
(immagini a piena risoluzione dal server IIIF). Le pagine già scaricate
non vengono riscaricate.
"""
import http.client
import json
import os
import sys
import time
import urllib.request

PAUSA = 1.0  # secondi tra una richiesta e l'altra, per cortesia verso la LoC


def scarica(url, dest, tentativi=4):
    for i in range(tentativi):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'opera-lyrics/0.1'})
            with urllib.request.urlopen(req, timeout=120) as r, open(dest + '.tmp', 'wb') as f:
                f.write(r.read())
            os.replace(dest + '.tmp', dest)
            return
        except (OSError, http.client.HTTPException) as e:
            if i == tentativi - 1:
                raise
            print(f'  errore {e}, riprovo', file=sys.stderr)
            time.sleep(2 ** (i + 1))


def main():
    lccn, cartella = sys.argv[1], sys.argv[2]
    os.makedirs(os.path.join(cartella, 'pagine'), exist_ok=True)
    scheda = os.path.join(cartella, 'item.json')
    if not os.path.exists(scheda):
        scarica(f'https://www.loc.gov/item/{lccn}/?fo=json', scheda)
    with open(scheda, encoding='utf-8') as f:
        item = json.load(f)
    pagine = item['resources'][0]['files']
    print(f"{item['item']['title']}: {len(pagine)} immagini")
    for n, varianti in enumerate(pagine, 1):
        dest = os.path.join(cartella, 'pagine', f'{n:04d}.jpg')
        if os.path.exists(dest):
            continue
        info = next(v['info'] for v in varianti if v.get('info'))
        url = info.replace('/info.json', '/full/pct:100.0/0/default.jpg')
        scarica(url, dest)
        print(f'  {n:04d}')
        time.sleep(PAUSA)


if __name__ == '__main__':
    main()
