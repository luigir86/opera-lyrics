import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:opera_lyrics/library/libretto.dart';
import 'package:opera_lyrics/library/libretto_parser.dart';

/// Every libretto shipped with the app must read cleanly: a header with
/// title, composer, source and licence, and acts with text in them.
void main() {
  final files = Directory('assets/libretti')
      .listSync()
      .whereType<File>()
      .where((f) => f.path.endsWith('.txt'));

  for (final file in files) {
    final name = file.uri.pathSegments.last;
    test(name, () {
      expect(
        name,
        matches(RegExp(r'^[a-z0-9]+(-[a-z0-9]+)*\.txt$')),
        reason: 'file names are lower case words joined by hyphens',
      );
      final l = parseLibretto(name, file.readAsStringSync());
      expect(l.title, isNot(name), reason: 'title: is missing');
      expect(l.composer, isNotEmpty, reason: 'composer: is missing');
      expect(l.source, isNotEmpty, reason: 'source: is missing');
      expect(l.license, isNotEmpty, reason: 'license: is missing');
      expect(l.acts, isNotEmpty);
      for (final act in l.acts) {
        expect(act.title, isNotEmpty);
        expect(
          act.numbers
              .expand((n) => n.lines)
              .any((x) => x.kind == LineKind.verse),
          isTrue,
          reason: '${act.title} has no verses',
        );
      }
    });
  }
}
