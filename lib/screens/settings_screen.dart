import 'package:flutter/material.dart';

import '../app/about.dart';
import '../app/opera_lyrics_app.dart';
import '../app/style.dart';
import '../l10n/app_localizations.dart';

/// Language, size of the libretto's text, screen on, and About.
class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final settings = AppScope.of(context).settings;
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(title: Text(l10n.settings)),
      body: ListenableBuilder(
        listenable: settings,
        builder: (context, _) => Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(
              maxWidth: OperaShape.maxTextWidth,
            ),
            child: ListView(
              children: [
                ListTile(
                  title: Text(l10n.language),
                  trailing: DropdownButton<String?>(
                    value: settings.languageCode,
                    underline: const SizedBox.shrink(),
                    onChanged: (code) => settings.languageCode = code,
                    items: [
                      DropdownMenuItem(child: Text(l10n.languageSystem)),
                      DropdownMenuItem(
                        value: 'it',
                        child: Text(l10n.languageItalian),
                      ),
                      DropdownMenuItem(
                        value: 'en',
                        child: Text(l10n.languageEnglish),
                      ),
                    ],
                  ),
                ),
                ListTile(
                  title: Text(l10n.textSize),
                  subtitle: Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(
                      l10n.textSizeSample,
                      style: TextStyle(
                        fontSize: settings.textSize,
                        color: theme.colorScheme.onSurface,
                      ),
                    ),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(
                    horizontal: OperaShape.gutter,
                  ),
                  child: SegmentedButton<double>(
                    showSelectedIcon: false,
                    segments: [
                      for (final size in OperaType.readerSizes)
                        ButtonSegment(
                          value: size,
                          label: Text(
                            'A',
                            style: TextStyle(
                              fontSize: OperaType.small + size / 4,
                            ),
                          ),
                          tooltip: '${size.round()}',
                        ),
                    ],
                    selected: {settings.textSize},
                    onSelectionChanged: (s) => settings.textSize = s.first,
                  ),
                ),
                const SizedBox(height: 8),
                SwitchListTile(
                  title: Text(l10n.keepScreenOn),
                  subtitle: Text(l10n.keepScreenOnHint),
                  value: settings.keepScreenOn,
                  onChanged: (on) => settings.keepScreenOn = on,
                ),
                const Divider(),
                ListTile(
                  title: Text(l10n.about),
                  leading: const Icon(Icons.info_outline),
                  onTap: () => showOperaAbout(context),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
