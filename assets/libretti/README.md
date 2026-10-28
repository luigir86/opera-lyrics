# Libretti

Every `.txt` file in this folder is an opera in the library: adding an opera means adding a file here, nothing else. The format is in [docs/formato-libretti.md](../../docs/formato-libretti.md).

The texts are in the public domain (their authors died more than 70 years ago). Each file says in its header where its text comes from (`source:`) and under which terms that transcription is shared (`license:`). Transcriptions from Wikisource are shared under CC BY-SA 4.0: they keep that licence and their attribution, separate from the app's code, which is under the MIT License. Transcriptions made from the Library of Congress scans (Albert Schatz Collection, public domain) with the scripts in [tools/loc](../../tools/loc) are shared under CC0. In `verdi-il-trovatore.txt` the scan of the main edition (Ricordi, Trieste 1853) lacks pages 30-31: the end of Part Three, from "Ah! sì, ben mio" to "Di quella pira", comes from the scan of the second edition listed in `tools/loc/verdi.tsv`, which prints no stage directions there.

The file name is `composer-title.txt` in lower case, with hyphens: `verdi-la-traviata.txt`. It is also the libretto's id, so it should not change once published.
