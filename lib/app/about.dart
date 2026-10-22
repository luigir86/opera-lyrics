import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../l10n/app_localizations.dart';

const sourceCodeUrl = 'https://github.com/luigir86/opera-lyrics';

/// Opens [url] in the browser; nothing happens if the phone has none.
Future<void> openLink(String url) async {
  try {
    await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
  } catch (error) {
    debugPrint('Link could not be opened: $error');
  }
}

/// The About dialog: what the app does, its licence, and the licences of the
/// open-source packages it is built with.
void showOperaAbout(BuildContext context) {
  final l10n = AppLocalizations.of(context);
  showAboutDialog(
    context: context,
    applicationName: l10n.appTitle,
    applicationLegalese: l10n.aboutLegalese,
    children: [
      const SizedBox(height: 16),
      Text(l10n.aboutDescription),
      const SizedBox(height: 8),
      Align(
        alignment: AlignmentDirectional.centerStart,
        child: TextButton.icon(
          onPressed: () => openLink(sourceCodeUrl),
          icon: const Icon(Icons.open_in_new, size: 18),
          label: Text(l10n.aboutSource(sourceCodeUrl)),
        ),
      ),
    ],
  );
}
