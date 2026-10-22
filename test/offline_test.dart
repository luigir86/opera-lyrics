import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

/// The app asks for no permission at all, and above all not INTERNET: the
/// promise of PRIVACY.md. (The debug and profile builds add INTERNET for
/// Flutter's own tools; the release build takes only the main manifest.)
void main() {
  test('the main manifest asks for no permission', () {
    final manifest = File('android/app/src/main/AndroidManifest.xml')
        .readAsStringSync();
    expect(manifest, isNot(contains('<uses-permission')));
  });

  test('no networking package is used', () {
    final pubspec = File('pubspec.yaml').readAsStringSync();
    for (final name in ['http:', 'dio:', 'web_socket']) {
      expect(pubspec, isNot(contains(name)));
    }
  });
}
