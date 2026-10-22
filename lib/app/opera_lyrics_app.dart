import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

import '../l10n/app_localizations.dart';
import '../library/catalog.dart';
import '../screens/library_screen.dart';
import 'screen_awake.dart';
import 'settings.dart';
import 'theme.dart';

/// What every screen needs, handed down the tree once.
class AppScope extends InheritedWidget {
  const AppScope({
    super.key,
    required this.settings,
    required this.catalog,
    required this.screenAwake,
    required super.child,
  });

  final AppSettings settings;
  final Catalog catalog;
  final ScreenAwake screenAwake;

  static AppScope of(BuildContext context) =>
      context.dependOnInheritedWidgetOfExactType<AppScope>()!;

  @override
  bool updateShouldNotify(AppScope old) =>
      settings != old.settings ||
      catalog != old.catalog ||
      screenAwake != old.screenAwake;
}

class OperaLyricsApp extends StatelessWidget {
  const OperaLyricsApp({
    super.key,
    required this.settings,
    required this.catalog,
    required this.screenAwake,
  });

  final AppSettings settings;
  final Catalog catalog;
  final ScreenAwake screenAwake;

  @override
  Widget build(BuildContext context) {
    return AppScope(
      settings: settings,
      catalog: catalog,
      screenAwake: screenAwake,
      // Only the language is needed up here; the screens listen to the
      // settings they show.
      child: ListenableBuilder(
        listenable: settings,
        builder: (context, _) => MaterialApp(
          onGenerateTitle: (context) => AppLocalizations.of(context).appTitle,
          debugShowCheckedModeBanner: false,
          theme: OperaTheme.dark,
          locale: settings.locale,
          supportedLocales: AppLocalizations.supportedLocales,
          localizationsDelegates: const [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
          home: const LibraryScreen(),
        ),
      ),
    );
  }
}
