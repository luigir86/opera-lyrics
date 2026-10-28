# Importare un libretto da Wikisource

Gli script di questa cartella hanno prodotto `verdi-la-traviata.txt` e `mozart-don-giovanni.txt` a partire da it.wikisource.org. Non sono un importatore generico: ogni trascrizione di Wikisource segna ruoli e didascalie a modo suo, e il testo che ne esce va sempre riletto prima di pubblicarlo.

1. Scaricare ogni atto già impaginato, una richiesta per volta e con calma (Wikisource limita le richieste):

   ```sh
   curl -A "OperaLyricsImporter/0.1 (https://github.com/luigir86/opera-lyrics)" \
     -o atto1.html "https://it.wikisource.org/w/index.php?title=La_traviata/Atto_primo&action=render"
   ```

2. Ridurre l'HTML a testo: i nomi di chi canta escono come `<<Nome>>`, le didascalie in corsivo come `_testo_` e quelle a margine come `⟦testo⟧`.

   ```sh
   python3 html2txt.py atto1.html > atto1.txt
   ```

3. Convertire nel formato dell'app ([docs/formato-libretti.md](../../docs/formato-libretti.md)), con l'intestazione dell'opera:

   ```sh
   python3 converti.py tr intestazione-la-traviata.txt atto1.txt atto2.txt atto3.txt > verdi-la-traviata.txt
   ```

   Il primo argomento (`tr`, `dg`) sceglie i nomi dei ruoli e le correzioni puntuali dell'opera, raccolti in cima a `converti.py`: battute che la fonte attribuisce solo nel titolo della scena, ruoli spezzati su due righe, didascalie fuori posto. Su `stderr` lo script elenca le righe che ha trattato come didascalie prima del primo ruolo di ogni scena (`PRE:`), da controllare una per una.

4. Rileggere il file nell'app e far girare `flutter test`.
