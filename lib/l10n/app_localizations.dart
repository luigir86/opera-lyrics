import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_en.dart';
import 'app_localizations_it.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations)!;
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
        delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('en'),
    Locale('it'),
  ];

  /// No description provided for @appTitle.
  ///
  /// In en, this message translates to:
  /// **'Opera Lyrics'**
  String get appTitle;

  /// No description provided for @settings.
  ///
  /// In en, this message translates to:
  /// **'Settings'**
  String get settings;

  /// No description provided for @about.
  ///
  /// In en, this message translates to:
  /// **'About'**
  String get about;

  /// No description provided for @language.
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get language;

  /// No description provided for @languageSystem.
  ///
  /// In en, this message translates to:
  /// **'Phone language'**
  String get languageSystem;

  /// No description provided for @languageEnglish.
  ///
  /// In en, this message translates to:
  /// **'English'**
  String get languageEnglish;

  /// No description provided for @languageItalian.
  ///
  /// In en, this message translates to:
  /// **'Italiano'**
  String get languageItalian;

  /// No description provided for @textSize.
  ///
  /// In en, this message translates to:
  /// **'Text size'**
  String get textSize;

  /// A sample verse shown at the chosen size; left in Italian, as in the libretti.
  ///
  /// In en, this message translates to:
  /// **'Libiamo ne\' lieti calici'**
  String get textSizeSample;

  /// No description provided for @keepScreenOn.
  ///
  /// In en, this message translates to:
  /// **'Keep the screen on'**
  String get keepScreenOn;

  /// No description provided for @keepScreenOnHint.
  ///
  /// In en, this message translates to:
  /// **'While a libretto is open'**
  String get keepScreenOnHint;

  /// No description provided for @resumeReading.
  ///
  /// In en, this message translates to:
  /// **'Continue reading'**
  String get resumeReading;

  /// No description provided for @resumePlace.
  ///
  /// In en, this message translates to:
  /// **'{opera}, {act}'**
  String resumePlace(String opera, String act);

  /// No description provided for @emptyLibrary.
  ///
  /// In en, this message translates to:
  /// **'No libretti yet.'**
  String get emptyLibrary;

  /// No description provided for @libraryError.
  ///
  /// In en, this message translates to:
  /// **'The libretti could not be read.'**
  String get libraryError;

  /// No description provided for @librettoBy.
  ///
  /// In en, this message translates to:
  /// **'Libretto by {name}'**
  String librettoBy(String name);

  /// No description provided for @source.
  ///
  /// In en, this message translates to:
  /// **'Source: {source}'**
  String source(String source);

  /// No description provided for @license.
  ///
  /// In en, this message translates to:
  /// **'Text: {license}'**
  String license(String license);

  /// No description provided for @readAct.
  ///
  /// In en, this message translates to:
  /// **'Read {act}'**
  String readAct(String act);

  /// No description provided for @contents.
  ///
  /// In en, this message translates to:
  /// **'Numbers in this act'**
  String get contents;

  /// No description provided for @previousAct.
  ///
  /// In en, this message translates to:
  /// **'Previous act'**
  String get previousAct;

  /// No description provided for @nextAct.
  ///
  /// In en, this message translates to:
  /// **'Next act'**
  String get nextAct;

  /// No description provided for @aboutDescription.
  ///
  /// In en, this message translates to:
  /// **'Opera Lyrics is a free library of opera libretti to read while the music plays, at home or at the theatre. It works fully offline: the texts are inside the app.'**
  String get aboutDescription;

  /// No description provided for @aboutLegalese.
  ///
  /// In en, this message translates to:
  /// **'Free and open source under the MIT License. The libretti are in the public domain; each says where its text comes from.'**
  String get aboutLegalese;

  /// No description provided for @aboutSource.
  ///
  /// In en, this message translates to:
  /// **'Source code: {url}'**
  String aboutSource(String url);
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['en', 'it'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'en':
      return AppLocalizationsEn();
    case 'it':
      return AppLocalizationsIt();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
