import 'package:flutter/material.dart';

import '../app/opera_lyrics_app.dart';
import '../app/style.dart';
import '../l10n/app_localizations.dart';
import '../library/libretto.dart';
import 'reader_screen.dart';

/// One opera: who wrote it, its acts and, in each act, its numbers. A
/// touch on an act or a number opens the text there.
class OperaScreen extends StatefulWidget {
  const OperaScreen({super.key, required this.librettoId});

  final String librettoId;

  @override
  State<OperaScreen> createState() => _OperaScreenState();
}

class _OperaScreenState extends State<OperaScreen> {
  Future<Libretto>? _libretto;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _libretto ??= AppScope.of(context).catalog.load(widget.librettoId);
  }

  void _read(int act, [int? number]) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => ReaderScreen(
          librettoId: widget.librettoId,
          act: act,
          number: number,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Libretto>(
      future: _libretto,
      builder: (context, snapshot) {
        final libretto = snapshot.data;
        return Scaffold(
          appBar: AppBar(title: Text(libretto?.title ?? '')),
          body: snapshot.hasError
              ? Center(child: Text(AppLocalizations.of(context).libraryError))
              : libretto == null
              ? const Center(child: CircularProgressIndicator())
              : _OperaContents(libretto: libretto, onRead: _read),
        );
      },
    );
  }
}

class _OperaContents extends StatelessWidget {
  const _OperaContents({required this.libretto, required this.onRead});

  final Libretto libretto;
  final void Function(int act, [int? number]) onRead;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context);
    final muted = theme.textTheme.bodyMedium?.copyWith(
      color: theme.colorScheme.onSurfaceVariant,
    );
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: OperaShape.maxTextWidth),
        child: ListView(
          padding: const EdgeInsets.only(bottom: 24),
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(
                OperaShape.gutter,
                8,
                OperaShape.gutter,
                8,
              ),
              child: Text(
                [
                  libretto.composer,
                  if (libretto.year != null) '${libretto.year}',
                  if (libretto.librettist.isNotEmpty)
                    l10n.librettoBy(libretto.librettist),
                ].join(' · '),
                style: muted,
              ),
            ),
            for (final (a, act) in libretto.acts.indexed) ...[
              const Divider(height: 24),
              ListTile(
                title: Semantics(
                  header: true,
                  child: Text(
                    act.title,
                    style: theme.textTheme.titleMedium?.copyWith(
                      color: theme.colorScheme.primary,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
                trailing: Icon(
                  Icons.menu_book,
                  color: theme.colorScheme.primary,
                  semanticLabel: l10n.readAct(act.title),
                ),
                onTap: () => onRead(a),
              ),
              for (final (n, number) in act.numbers.indexed)
                if (number.title.isNotEmpty)
                  ListTile(
                    dense: true,
                    contentPadding: const EdgeInsets.only(
                      left: OperaShape.gutter * 2,
                      right: OperaShape.gutter,
                    ),
                    title: Text(number.title, style: theme.textTheme.bodyLarge),
                    onTap: () => onRead(a, n),
                  ),
            ],
            if (libretto.source.isNotEmpty || libretto.license.isNotEmpty)
              const Divider(height: 32),
            if (libretto.source.isNotEmpty)
              _Footnote(l10n.source(libretto.source), style: muted),
            if (libretto.license.isNotEmpty)
              _Footnote(l10n.license(libretto.license), style: muted),
          ],
        ),
      ),
    );
  }
}

class _Footnote extends StatelessWidget {
  const _Footnote(this.text, {this.style});

  final String text;
  final TextStyle? style;

  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.symmetric(
      horizontal: OperaShape.gutter,
      vertical: 4,
    ),
    child: Text(text, style: style),
  );
}
