import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'app/licenses.dart';
import 'app/opera_lyrics_app.dart';
import 'app/screen_awake.dart';
import 'app/settings.dart';
import 'library/catalog.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // A quick read of a small file, so the app opens in the chosen language.
  AppSettings settings;
  try {
    settings = await AppSettings.load();
  } catch (error) {
    // Unreadable settings must never keep the app from opening: it then
    // starts with the defaults, which are not saved.
    debugPrint('Settings could not be read: $error');
    settings = AppSettings();
  }
  registerAssetLicenses();
  runApp(
    OperaLyricsApp(
      settings: settings,
      catalog: Catalog(rootBundle),
      screenAwake: WakelockScreenAwake(),
    ),
  );
}
