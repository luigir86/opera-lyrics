# Istruzioni per chi rivede (persona o modello)

Queste istruzioni si possono dare così come sono a un modello piccolo che sappia leggere immagini (per esempio Claude Haiku), indicando la cartella `revisione/` di un libretto.

---

Stai correggendo l'OCR di un libretto d'opera stampato nell'Ottocento. Il lavoro è meccanico: guardi un'immagine e scrivi che cosa c'è stampato. Non scrivere mai niente a memoria: conta solo l'immagine.

Il file da riempire è `revisione/dubbi.tsv` (separato da tabulazioni; colonne: n, riga, pos, parola, motivi, altra_edizione, dizionario, ritaglio, correzione).

Per ogni riga del file:

1. Apri l'immagine indicata nella colonna `ritaglio`: è la riga stampata (a volte due righe).
2. Trova la parola della colonna `parola`: è la parola numero `pos` della riga, contando da 0. La punteggiatura non conta come parola; una forma elisa come `l'arcano` conta come una parola sola.
3. Scrivi nella colonna `correzione`:
   - `=` se la parola è stampata proprio così, con le stesse lettere e gli stessi accenti;
   - `-` se nella stampa quella parola non c'è: è una macchia, un pezzo di numero di pagina o un segno letto come lettere;
   - `>NOME` se la parola è il nome (anche abbreviato) di chi canta, stampato a margine all'inizio del verso: per esempio `>TUTTI` per `Tutti` o `>ZACCARIA` per `Zac.`, usando i nomi dei personaggi che trovi nelle altre righe;
   - altrimenti la parola come è stampata, con gli accenti e gli apostrofi della stampa. Se l'OCR ha attaccato due parole, scrivile staccate (`A me`).
   Non contano le differenze di sole maiuscole e minuscole (i titoli stampati in maiuscolo) né gli spazi dopo l'apostrofo: in quei casi scrivi `=`.
4. Le righe con `pos` uguale a `nome` riguardano il nome di chi canta: il ritaglio mostra il nome stampato, spesso abbreviato (`Zac.`). Scrivi in `correzione` il nome intero in maiuscolo scegliendolo tra quelli della colonna `altra_edizione` (`ZACCARIA`), oppure `=` se il nome è già giusto, oppure `-` se quella riga non è un nome ma un pezzo di didascalia o una macchia.
5. Le colonne `altra_edizione` e `dizionario` sono solo suggerimenti. Un'altra edizione può avere davvero una parola diversa: vale sempre l'immagine.
6. Se l'immagine non si legge, non mostra la parola cercata o non sei sicuro, scrivi `=` e annota il numero della riga in un elenco a parte.

Lavora a gruppi di una decina di immagini e aggiorna il file dopo ogni gruppo (con uno script Python e il modulo csv, salvato dentro la cartella `revisione/` che stai rivedendo e non altrove, perché altri revisori possono lavorare in parallelo su altre opere; separatore tabulazione, intestazione e colonne invariate: riempi solo `correzione`). Non modificare altri file. Non fermarti finché tutte le righe hanno un valore in `correzione`.

Alla fine riporta: quante righe `=`, quante corrette, quante `-` e l'elenco delle righe incerte.
