import 'package:flutter/material.dart';

import 'style.dart';

/// Opera Lyrics' look, in one place: change a colour here and every screen
/// follows, like the variables of a CSS stylesheet.
///
/// The bronze on ebony of Low End, reduced to what a reader needs: always
/// dark (it is read in the dark of a theatre), light ink for the verses, a
/// muted ink for stage directions and one flat accent, the bronze, for the
/// names of the characters and of the numbers.
abstract final class Palette {
  /// The accent.
  static const bronze = Color(0xFFD4A373);

  // The ground, from the darkest up.
  static const ebony = Color(0xFF141312);
  static const ebonyShade1 = Color(0xFF1C1B19);
  static const ebonyShade2 = Color(0xFF262422);
  static const ebonyShade3 = Color(0xFF312F2C);
  static const walnutDeep = Color(0xFF2B1D16);

  // Text.
  static const inkOnDark = Color(0xFFEFEDEA);
  static const inkOnDarkMuted = Color(0xFFC9C5BF);
}

abstract final class OperaTheme {
  /// The bronze mixed into the ebony: the more of it, the stronger.
  static Color tint(double amount) =>
      Color.lerp(Palette.ebony, Palette.bronze, amount)!;

  /// The one theme: dark, bronze on ebony. There is no light theme.
  static final dark = () {
    final container = tint(0.2);
    final scheme = ColorScheme(
      brightness: Brightness.dark,
      primary: Palette.bronze,
      onPrimary: Palette.walnutDeep,
      primaryContainer: container,
      onPrimaryContainer: Palette.inkOnDark,
      secondary: Palette.bronze,
      onSecondary: Palette.walnutDeep,
      error: const Color(0xFFFF5F56),
      onError: Palette.walnutDeep,
      surface: Palette.ebony,
      onSurface: Palette.inkOnDark,
      onSurfaceVariant: Palette.inkOnDarkMuted,
      surfaceContainerLowest: Colors.black,
      surfaceContainerLow: Palette.ebonyShade1,
      surfaceContainer: Palette.ebonyShade1,
      surfaceContainerHigh: Palette.ebonyShade2,
      surfaceContainerHighest: Palette.ebonyShade3,
      outline: tint(0.75),
      outlineVariant: tint(0.26),
    );
    final shape = RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(OperaShape.radius),
    );
    return ThemeData(
      fontFamily: 'Edwin',
      colorScheme: scheme,
      textTheme: OperaType.textTheme,
      scaffoldBackgroundColor: scheme.surface,
      appBarTheme: AppBarTheme(
        backgroundColor: scheme.surface,
        foregroundColor: scheme.onSurface,
        surfaceTintColor: Colors.transparent,
        centerTitle: false,
        titleTextStyle: TextStyle(
          fontFamily: 'Edwin',
          fontSize: OperaType.title,
          color: scheme.onSurface,
          fontWeight: FontWeight.w700,
        ),
      ),
      cardTheme: CardThemeData(
        color: scheme.surfaceContainer,
        surfaceTintColor: Colors.transparent,
        shape: shape,
        margin: EdgeInsets.zero,
      ),
      popupMenuTheme: PopupMenuThemeData(
        color: scheme.surfaceContainerHigh,
        surfaceTintColor: Colors.transparent,
        shape: shape,
      ),
      bottomSheetTheme: BottomSheetThemeData(
        backgroundColor: scheme.surfaceContainer,
        surfaceTintColor: Colors.transparent,
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: scheme.surfaceContainerHigh,
        surfaceTintColor: Colors.transparent,
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(shape: shape),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          shape: shape,
          foregroundColor: scheme.onSurface,
          side: BorderSide(color: scheme.outline),
        ),
      ),
      dividerTheme: DividerThemeData(color: scheme.outlineVariant),
    );
  }();
}
