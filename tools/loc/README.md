# Libretti dalla Library of Congress

Script per ricavare un libretto nel formato dell'app ([docs/formato-libretti.md](../../docs/formato-libretti.md)) dalle scansioni della [Albert Schatz Collection](https://www.loc.gov/collections/albert-schatz/) della Library of Congress. La collezione è di pubblico dominio ("free to use or reuse"; si cita "Library of Congress, Music Division"), ma non ha il testo: solo immagini. Il testo lo ricaviamo noi con l'OCR.

**Regola:** la scansione è l'unica fonte del testo. Un'altra edizione o una versione aperta servono solo a trovare i punti dubbi; si corregge solo ciò che la scansione conferma.

## Cosa serve

```
sudo apt-get install tesseract-ocr tesseract-ocr-ita hunspell hunspell-it
pip install Pillow
```

## I passi

Ogni libretto ha una cartella di lavoro (fuori dal repository). Se la Library of Congress ha una seconda edizione dello stesso libretto con il testo italiano, conviene lavorarla allo stesso modo: le due scansioni sbagliano in punti diversi e il confronto trova quasi tutti gli errori.

```
python3 scarica.py 2010657556 lavoro/aida-cairo        # numero della scheda loc.gov/item/...
python3 ocr.py lavoro/aida-cairo
# scrivere lavoro/aida-cairo/intestazione.txt (title, composer, librettist, year, source, license)
python3 testo.py lavoro/aida-cairo lavoro/aida-cairo/intestazione.txt
python3 dubbi.py lavoro/aida-cairo [lavoro/aida-ricordi]
# revisione: vedi sotto
python3 applica.py lavoro/aida-cairo ../../assets/libretti/verdi-aida.txt
```

| Script | Cosa fa |
| --- | --- |
| `scarica.py` | Scheda e immagini a piena risoluzione dal server IIIF della LoC, con una pausa tra le richieste. |
| `ocr.py` | Toglie il bordo nero, divide le doppie pagine sulla piega, fa l'OCR di ogni metà e tiene quella in italiano (la sceglie il dizionario). |
| `testo.py` | Dal testo dell'OCR al formato dell'app: atti, scene, personaggi, didascalie, spaziatura. Non cambia nessuna parola. |
| `dubbi.py` | Segnala le parole dubbie (confidenza bassa, ignote al dizionario, diverse nell'altra edizione, scambi tipici come `AI`/`Al`) e ritaglia la riga dalla scansione. |
| `applica.py` | Applica le correzioni della revisione. Si ferma se ne manca qualcuna. |

## La revisione

`dubbi.py` scrive in `revisione/` il file `dubbi.tsv`, un ritaglio `NNNN.jpg` per ogni dubbio e `index.html` per sfogliarli. Per ogni riga di `dubbi.tsv`:

1. aprire il ritaglio indicato nella colonna `ritaglio`: è la riga stampata;
2. trovare la parola della colonna `parola` (la `pos`-esima parola della riga, contando da 0);
3. scrivere nella colonna `correzione`:
   - `=` se la parola è stampata proprio così;
   - `-` se nella stampa la parola non c'è (una macchia o un numero di pagina letti come lettere);
   - altrimenti la parola come è stampata, con gli accenti e gli apostrofi della stampa (anche due parole, se l'OCR le ha attaccate: `A me`).

Le colonne `altra_edizione` e `dizionario` sono solo suggerimenti: l'altra edizione può avere davvero una parola diversa (Ricordi scrive "Giovine" dove il Cairo stampa "Giovane"), e allora vale la stampa del ritaglio. In caso di dubbio si lascia `=` e si annota il numero.

Il lavoro è meccanico: lo può fare una persona o un modello piccolo che sappia leggere immagini.

La punteggiatura non viene controllata: va riletta a parte.
