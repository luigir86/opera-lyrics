import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

/// Adds the font's licence to the page that the About dialog opens, next to
/// the ones Flutter collects for the code packages. It is read only when
/// that page is opened.
void registerAssetLicenses() {
  LicenseRegistry.addLicense(() async* {
    yield LicenseEntryWithLineBreaks([
      'Edwin',
    ], await rootBundle.loadString('assets/fonts/OFL-Edwin.txt'));
  });
}
