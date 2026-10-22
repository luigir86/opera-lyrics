import 'package:flutter/widgets.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'style.dart';

/// Where the reader left off: an act of a libretto, and how far down it.
class ReadingPlace {
  const ReadingPlace(this.librettoId, this.act, this.offset);

  final String librettoId;
  final int act;

  /// The scroll offset in the act, in logical pixels.
  final double offset;
}

/// The reader's preferences, kept on the phone between launches.
class AppSettings extends ChangeNotifier {
  /// Settings that are not saved anywhere; used in tests.
  AppSettings() : _prefs = null;

  AppSettings._(this._prefs) {
    final prefs = _prefs!;
    // Each value is checked for its type as well: one saved by another
    // build must fall back to the default, not stop the app from opening.
    final language = _read<String>(prefs, _languageKey);
    _languageCode = supportedLanguages.contains(language) ? language : null;
    final size = _read<num>(prefs, _textSizeKey)?.toDouble();
    _textSize = OperaType.readerSizes.contains(size)
        ? size!
        : OperaType.readerDefault;
    _keepScreenOn = _read<bool>(prefs, _keepScreenOnKey) ?? true;
    final id = _read<String>(prefs, _placeIdKey);
    final act = _read<int>(prefs, _placeActKey);
    final offset = _read<num>(prefs, _placeOffsetKey)?.toDouble();
    if (id != null && act != null && act >= 0) {
      _place = ReadingPlace(id, act, offset ?? 0);
    }
  }

  /// Reads the saved settings.
  static Future<AppSettings> load() async =>
      AppSettings._(await SharedPreferences.getInstance());

  static const supportedLanguages = ['en', 'it'];
  static const _languageKey = 'language';
  static const _textSizeKey = 'reader_text_size';
  static const _keepScreenOnKey = 'keep_screen_on';
  static const _placeIdKey = 'place_libretto';
  static const _placeActKey = 'place_act';
  static const _placeOffsetKey = 'place_offset';

  final SharedPreferences? _prefs;
  String? _languageCode;
  double _textSize = OperaType.readerDefault;
  bool _keepScreenOn = true;
  ReadingPlace? _place;

  static T? _read<T>(SharedPreferences prefs, String key) {
    final value = prefs.get(key);
    return value is T ? value : null;
  }

  /// Saves in the background: the setting already applies, and a failed
  /// write only means it is forgotten at the next launch.
  void _save(Future<bool>? write) {
    write?.catchError((Object error) {
      debugPrint('Settings could not be saved: $error');
      return false;
    });
  }

  /// 'en' or 'it', or null to follow the phone.
  String? get languageCode => _languageCode;

  /// The locale to show the app in, or null to follow the phone.
  Locale? get locale => _languageCode == null ? null : Locale(_languageCode!);

  set languageCode(String? code) {
    if (code != null && !supportedLanguages.contains(code)) return;
    if (code == _languageCode) return;
    _languageCode = code;
    _save(
      code == null
          ? _prefs?.remove(_languageKey)
          : _prefs?.setString(_languageKey, code),
    );
    notifyListeners();
  }

  /// The size of the libretto's text, one of [OperaType.readerSizes].
  double get textSize => _textSize;

  set textSize(double size) {
    if (!OperaType.readerSizes.contains(size) || size == _textSize) return;
    _textSize = size;
    _save(_prefs?.setDouble(_textSizeKey, size));
    notifyListeners();
  }

  /// Whether the screen stays on while a libretto is open (on by default:
  /// at the opera both hands may be busy, and a dark screen loses the
  /// place).
  bool get keepScreenOn => _keepScreenOn;

  set keepScreenOn(bool on) {
    if (on == _keepScreenOn) return;
    _keepScreenOn = on;
    _save(_prefs?.setBool(_keepScreenOnKey, on));
    notifyListeners();
  }

  /// Where the reader left off, or null if nothing was read yet.
  ReadingPlace? get place => _place;

  /// Remembers [place]. Saved often while scrolling, so it does not notify
  /// listeners: the library reads it when it is shown again.
  void remember(ReadingPlace place) {
    _place = place;
    _save(_prefs?.setString(_placeIdKey, place.librettoId));
    _save(_prefs?.setInt(_placeActKey, place.act));
    _save(_prefs?.setDouble(_placeOffsetKey, place.offset));
  }
}
