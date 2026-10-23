"""Ritocchi a mano sulla struttura del libretto finito, ripetibili.

Uso: python3 ritocchi.py assets/libretti/verdi-attila.txt lavoro/attila/ritocchi.tsv

Dopo applica.py restano errori di struttura che si vedono solo leggendo:
un atto non riconosciuto, un "SCENA III" letto "SCENA im", un verso finito
dentro una didascalia. Si scrivono in ritocchi.tsv, così si possono rifare
dopo ogni nuovo applica.py. Una riga per ritocco, separata da tabulazioni:

    sostituisci <riga com'è>  <riga nuova>    (<riga nuova> vuota: si toglie)
    prima       <riga com'è>  <riga nuova>    (aggiunge una riga prima)
    dopo        <riga com'è>  <riga nuova>    (aggiunge una riga dopo)
    vai         <riga com'è>                  (non cambia niente: serve solo a
                                               indicare da dove cercare la riga
                                               del ritocco seguente)

Le righe si cercano nell'ordine del file, ognuna dopo quella del ritocco
precedente: così "## Scena prima" indica la prossima, non la prima del
libretto. "\\n" nella riga nuova la divide in più righe. Le righe che
cominciano con # nel file dei ritocchi sono commenti.
"""
import sys


def main():
    percorso, ritocchi = sys.argv[1], sys.argv[2]
    with open(percorso, encoding='utf-8') as f:
        righe = f.read().split('\n')
    cursore = 0
    with open(ritocchi, encoding='utf-8') as f:
        for n, r in enumerate(f, 1):
            r = r.rstrip('\n')
            if not r.strip() or r.startswith('#'):
                continue
            azione, vecchia, *resto = r.split('\t')
            nuove = resto[0].split('\\n') if resto and resto[0] else []
            try:
                i = righe.index(vecchia, cursore)
            except ValueError:
                sys.exit(f'ritocco {n}: non trovo "{vecchia}" dopo la riga {cursore + 1}')
            if azione == 'sostituisci':
                righe[i:i + 1] = nuove
                cursore = i + len(nuove)
            elif azione == 'prima':
                righe[i:i] = nuove
                cursore = i + len(nuove)
            elif azione == 'vai':
                cursore = i + 1
            elif azione == 'dopo':
                righe[i + 1:i + 1] = nuove
                cursore = i + 1 + len(nuove)
            else:
                sys.exit(f'ritocco {n}: azione sconosciuta "{azione}"')
    with open(percorso, 'w', encoding='utf-8') as f:
        f.write('\n'.join(righe))


if __name__ == '__main__':
    main()
