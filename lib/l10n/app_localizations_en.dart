// ignore: unused_import
import 'package:intl/intl.dart' as intl;

import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'Opera Lyrics';

  @override
  String get settings => 'Settings';

  @override
  String get about => 'About';

  @override
  String get language => 'Language';

  @override
  String get languageSystem => 'Phone language';

  @override
  String get languageEnglish => 'English';

  @override
  String get languageItalian => 'Italiano';

  @override
  String get textSize => 'Text size';

  @override
  String get textSizeSample => 'Libiamo ne\' lieti calici';

  @override
  String get keepScreenOn => 'Keep the screen on';

  @override
  String get keepScreenOnHint => 'While a libretto is open';

  @override
  String get resumeReading => 'Continue reading';

  @override
  String resumePlace(String opera, String act) {
    return '$opera, $act';
  }

  @override
  String get emptyLibrary => 'No libretti yet.';

  @override
  String get libraryError => 'The libretti could not be read.';

  @override
  String librettoBy(String name) {
    return 'Libretto by $name';
  }

  @override
  String source(String source) {
    return 'Source: $source';
  }

  @override
  String license(String license) {
    return 'Text: $license';
  }

  @override
  String readAct(String act) {
    return 'Read $act';
  }

  @override
  String get contents => 'Numbers in this act';

  @override
  String get previousAct => 'Previous act';

  @override
  String get nextAct => 'Next act';

  @override
  String get aboutDescription =>
      'Opera Lyrics is a free library of opera libretti to read while the music plays, at home or at the theatre. It works fully offline: the texts are inside the app.';

  @override
  String get aboutLegalese =>
      'Free and open source under the MIT License. The libretti are in the public domain; each says where its text comes from.';

  @override
  String aboutSource(String url) {
    return 'Source code: $url';
  }
}
