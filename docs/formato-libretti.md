# Il formato dei libretti

Ogni opera è un file di testo semplice in `assets/libretti/`, in UTF-8, chiamato `compositore-titolo.txt` in minuscolo con i trattini (`verdi-la-traviata.txt`). Il nome del file è anche l'identificativo dell'opera: una volta pubblicato non va cambiato.

## Esempio

```text
// Le righe che iniziano con // sono commenti e non si vedono nell'app.
title: La traviata
composer: Giuseppe Verdi
librettist: Francesco Maria Piave
year: 1853
source: https://it.wikisource.org/wiki/La_traviata
license: Pubblico dominio; trascrizione di Wikisource, CC BY-SA 4.0

# Atto primo
(Salotto in casa di Violetta.)

## Introduzione
VIOLETTA
Flora, amici, la notte che resta
d'altre gioie qui fate brillar.

## Brindisi
ALFREDO
Libiamo, libiamo ne' lieti calici
che la bellezza infiora.
```

## Regole

| Riga | Significato |
| --- | --- |
| `chiave: valore` prima del primo atto | Intestazione: `title`, `composer`, `librettist`, `year`, `source`, `license`. Sono obbligatori `title`, `composer`, `source` e `license`. |
| `# Titolo` | Inizio di un atto (o di un prologo). |
| `## Titolo` | Inizio di un numero: aria, duetto, recitativo, coro. È l'unità che di solito corrisponde a una traccia di un disco. |
| Riga tutta in maiuscolo | Chi canta: `VIOLETTA`, `ALFREDO E VIOLETTA`, `CORO`. |
| `(testo)` | Didascalia, mostrata in corsivo attenuato. |
| Riga vuota | Fine di una strofa. |
| `// testo` | Commento, ignorato. |
| Qualsiasi altra riga | Un verso. |

Le didascalie tra l'inizio dell'atto e il primo `##` restano in cima all'atto, senza titolo.

## Attenzioni

- I versi non vanno scritti tutti in maiuscolo, altrimenti sono letti come nomi di personaggi: `Ah!`, non `AH!`.
- Ogni riga ha un posto fisso (atto, numero, riga, contati da zero), per esempio `a0.n2.l5`. La futura modalità Sync aggancerà i tempi a questi posti: correggere una parola non cambia nulla, ma aggiungere o togliere righe sposta quelle che seguono nello stesso numero.
- Il testo deve essere di pubblico dominio e la fonte deve essere indicata in `source:`. Le traduzioni moderne sono protette e non vanno incluse.
- `flutter test` controlla ogni file della cartella: intestazione completa, almeno un atto, versi in ogni atto.
