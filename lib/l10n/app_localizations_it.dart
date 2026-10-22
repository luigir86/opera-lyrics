// ignore: unused_import
import 'package:intl/intl.dart' as intl;

import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Italian (`it`).
class AppLocalizationsIt extends AppLocalizations {
  AppLocalizationsIt([String locale = 'it']) : super(locale);

  @override
  String get appTitle => 'Opera Lyrics';

  @override
  String get settings => 'Impostazioni';

  @override
  String get about => 'Informazioni';

  @override
  String get language => 'Lingua';

  @override
  String get languageSystem => 'Lingua del telefono';

  @override
  String get languageEnglish => 'English';

  @override
  String get languageItalian => 'Italiano';

  @override
  String get textSize => 'Dimensione del testo';

  @override
  String get textSizeSample => 'Libiamo ne\' lieti calici';

  @override
  String get keepScreenOn => 'Schermo sempre acceso';

  @override
  String get keepScreenOnHint => 'Mentre un libretto è aperto';

  @override
  String get resumeReading => 'Riprendi la lettura';

  @override
  String resumePlace(String opera, String act) {
    return '$opera, $act';
  }

  @override
  String get emptyLibrary => 'Ancora nessun libretto.';

  @override
  String get libraryError => 'Non è stato possibile leggere i libretti.';

  @override
  String librettoBy(String name) {
    return 'Libretto di $name';
  }

  @override
  String source(String source) {
    return 'Fonte: $source';
  }

  @override
  String license(String license) {
    return 'Testo: $license';
  }

  @override
  String readAct(String act) {
    return 'Leggi $act';
  }

  @override
  String get contents => 'Numeri di questo atto';

  @override
  String get previousAct => 'Atto precedente';

  @override
  String get nextAct => 'Atto successivo';

  @override
  String get aboutDescription =>
      'Opera Lyrics è una biblioteca gratuita di libretti d\'opera da leggere mentre la musica va, a casa o a teatro. Funziona senza internet: i testi sono dentro l\'app.';

  @override
  String get aboutLegalese =>
      'Libera e open source con licenza MIT. I libretti sono di pubblico dominio; ognuno dice da dove viene il suo testo.';

  @override
  String aboutSource(String url) {
    return 'Codice sorgente: $url';
  }
}
