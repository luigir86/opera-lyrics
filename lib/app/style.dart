import 'package:flutter/material.dart';

/// The few font sizes the screens are made from. Colours live in
/// `theme.dart`; the size of the libretto itself is the reader's choice
/// ([readerSizes]).
abstract final class OperaType {
  /// Titles: the opera on its page, the bar at the top.
  static const title = 22.0;

  /// Names in lists, headings of an act.
  static const body = 16.0;

  /// Captions: the year and librettist under an opera, the source.
  static const caption = 14.0;

  /// The smallest text anywhere. Nothing is set smaller.
  static const small = 13.0;

  /// The sizes the libretto can be read at, from the settings.
  static const readerSizes = [16.0, 18.0, 20.0, 24.0, 28.0];

  /// The size the libretto opens at, until the reader picks another.
  static const readerDefault = 20.0;

  static const textTheme = TextTheme(
    headlineSmall: TextStyle(fontSize: title),
    titleLarge: TextStyle(fontSize: title),
    titleMedium: TextStyle(fontSize: body),
    titleSmall: TextStyle(fontSize: caption),
    bodyLarge: TextStyle(fontSize: body),
    bodyMedium: TextStyle(fontSize: caption),
    labelLarge: TextStyle(fontSize: caption),
    bodySmall: TextStyle(fontSize: small),
    labelMedium: TextStyle(fontSize: small),
    labelSmall: TextStyle(fontSize: small),
  );
}

/// Shapes and spacing.
abstract final class OperaShape {
  /// Corner radius of buttons, cards and menus.
  static const radius = 16.0;

  /// Space at the sides of every page.
  static const gutter = 16.0;

  /// The widest a column of text grows, so lines stay easy to read on a
  /// tablet or in landscape.
  static const maxTextWidth = 640.0;
}
