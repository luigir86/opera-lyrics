import 'dart:io';

import 'package:flutter/material.dart';

import 'dart:convert';

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:opera_lyrics/app/opera_lyrics_app.dart';
import 'package:opera_lyrics/app/screen_awake.dart';
import 'package:opera_lyrics/app/settings.dart';
import 'package:opera_lyrics/library/catalog.dart';

/// A bundle holding the test libretto as `assets/libretti/prova-esempio.txt`.
class _FixtureBundle extends CachingAssetBundle {
  static final _text = File('test/fixtures/esempio.txt').readAsStringSync();

  @override
  Future<ByteData> load(String key) async {
    if (key == '${Catalog.folder}prova-esempio.txt') {
      return ByteData.sublistView(Uint8List.fromList(utf8Encode(_text)));
    }
    throw FlutterError('No asset $key');
  }
}

List<int> utf8Encode(String s) => const Utf8Codec().encode(s);

Future<(AppSettings, FakeScreenAwake)> _pump(
  WidgetTester tester, {
  bool empty = false,
}) async {
  final settings = AppSettings()..languageCode = 'it';
  final awake = FakeScreenAwake();
  await tester.pumpWidget(
    OperaLyricsApp(
      settings: settings,
      catalog: Catalog(
        _FixtureBundle(),
        files: () async => empty ? [] : ['${Catalog.folder}prova-esempio.txt'],
      ),
      screenAwake: awake,
    ),
  );
  await tester.pumpAndSettle();
  return (settings, awake);
}

void main() {
  testWidgets('the library groups operas by composer', (tester) async {
    await _pump(tester);
    expect(find.text('Giovanni Battista Prova'), findsOneWidget);
    expect(find.text("L'esempio"), findsOneWidget);
    expect(find.text('1850 · Libretto di Anna Verso'), findsOneWidget);
  });

  testWidgets('an empty library says so', (tester) async {
    await _pump(tester, empty: true);
    expect(find.text('Ancora nessun libretto.'), findsOneWidget);
  });

  testWidgets('the opera lists its acts and numbers', (tester) async {
    await _pump(tester);
    await tester.tap(find.text("L'esempio"));
    await tester.pumpAndSettle();
    expect(find.text('Atto primo'), findsOneWidget);
    expect(find.text('Atto secondo'), findsOneWidget);
    expect(find.text('Duetto – Insieme'), findsOneWidget);
    expect(find.text('Fonte: Scritto per i test'), findsOneWidget);
  });

  testWidgets('reading an act keeps the screen on and remembers the place', (
    tester,
  ) async {
    final (settings, awake) = await _pump(tester);
    await tester.tap(find.text("L'esempio"));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Duetto – Insieme'));
    await tester.pumpAndSettle();

    expect(awake.on, isTrue);
    expect(find.text('Insieme canteremo'), findsOneWidget);
    expect(find.text('ANNA E CARLO'), findsOneWidget);
    expect(find.text('Anna apre.'), findsOneWidget);
    expect(settings.place?.librettoId, 'prova-esempio');

    await tester.tap(find.text('Atto successivo'));
    await tester.pumpAndSettle();
    expect(find.text('Evviva, evviva!'), findsOneWidget);
    expect(settings.place?.act, 1);

    // Back to the library: the place is offered there.
    await tester.tap(find.byType(BackButton));
    await tester.pumpAndSettle();
    expect(awake.on, isFalse);
    await tester.tap(find.byType(BackButton));
    await tester.pumpAndSettle();
    expect(find.text('Riprendi la lettura'), findsOneWidget);
    expect(find.text("L'esempio, Atto secondo"), findsOneWidget);
  });

  testWidgets('the text size applies to the verses', (tester) async {
    final (settings, _) = await _pump(tester);
    settings.textSize = 28;
    await tester.tap(find.text("L'esempio"));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Atto primo'));
    await tester.pumpAndSettle();
    final verse = tester.widget<Text>(find.text('Sono io, apri.'));
    expect(verse.style?.fontSize, 28);
  });

  testWidgets('settings change the language', (tester) async {
    final (settings, _) = await _pump(tester);
    await tester.tap(find.byTooltip('Impostazioni'));
    await tester.pumpAndSettle();
    expect(find.text('Schermo sempre acceso'), findsOneWidget);
    settings.languageCode = 'en';
    await tester.pumpAndSettle();
    expect(find.text('Keep the screen on'), findsOneWidget);
  });
}
