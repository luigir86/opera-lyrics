import 'package:flutter/material.dart';

import '../app/opera_lyrics_app.dart';
import '../app/settings.dart';
import '../app/style.dart';
import '../l10n/app_localizations.dart';
import '../library/catalog.dart';
import '../library/libretto.dart';
import 'opera_screen.dart';
import 'reader_screen.dart';
import 'settings_screen.dart';

/// The first screen: the libretti, grouped by composer, and a shortcut back
/// to where the reader left off.
class LibraryScreen extends StatefulWidget {
  const LibraryScreen({super.key});

  @override
  State<LibraryScreen> createState() => _LibraryScreenState();
}

class _LibraryScreenState extends State<LibraryScreen> {
  Future<List<Libretto>>? _libretti;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _libretti ??= AppScope.of(context).catalog.list();
  }

  /// Opens [page] and, back here, shows the place the reader got to.
  Future<void> _open(Widget page) async {
    await Navigator.of(context).push(MaterialPageRoute(builder: (_) => page));
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.appTitle),
        actions: [
          IconButton(
            tooltip: l10n.settings,
            icon: const Icon(Icons.settings_outlined),
            onPressed: () => _open(const SettingsScreen()),
          ),
        ],
      ),
      body: FutureBuilder<List<Libretto>>(
        future: _libretti,
        builder: (context, snapshot) {
          if (snapshot.hasError) {
            return _Message(l10n.libraryError);
          }
          final libretti = snapshot.data;
          if (libretti == null) {
            return const Center(child: CircularProgressIndicator());
          }
          if (libretti.isEmpty) return _Message(l10n.emptyLibrary);
          return _LibraryList(
            libretti: libretti,
            place: AppScope.of(context).settings.place,
            onOpen: _open,
          );
        },
      ),
    );
  }
}

class _LibraryList extends StatelessWidget {
  const _LibraryList({
    required this.libretti,
    required this.place,
    required this.onOpen,
  });

  final List<Libretto> libretti;
  final ReadingPlace? place;
  final void Function(Widget page) onOpen;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context);
    final groups = byComposer(libretti);
    final place = this.place;
    final resumable =
        place != null && libretti.any((l) => l.id == place.librettoId);
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: OperaShape.maxTextWidth),
        child: ListView(
          padding: const EdgeInsets.only(bottom: 24),
          children: [
            if (resumable) _ResumeCard(place: place, onOpen: onOpen),
            for (final MapEntry(key: composer, value: operas)
                in groups.entries) ...[
              Padding(
                padding: const EdgeInsets.fromLTRB(
                  OperaShape.gutter,
                  24,
                  OperaShape.gutter,
                  4,
                ),
                child: Semantics(
                  header: true,
                  child: Text(
                    composer,
                    style: theme.textTheme.titleMedium?.copyWith(
                      color: theme.colorScheme.primary,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ),
              for (final opera in operas)
                ListTile(
                  title: Text(opera.title),
                  subtitle: Text(
                    [
                      if (opera.year != null) '${opera.year}',
                      if (opera.librettist.isNotEmpty)
                        l10n.librettoBy(opera.librettist),
                    ].join(' · '),
                  ),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => onOpen(OperaScreen(librettoId: opera.id)),
                ),
            ],
          ],
        ),
      ),
    );
  }
}

/// "Continue reading": the opera and act last open, a touch away.
class _ResumeCard extends StatelessWidget {
  const _ResumeCard({required this.place, required this.onOpen});

  final ReadingPlace place;
  final void Function(Widget page) onOpen;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final theme = Theme.of(context);
    return FutureBuilder<Libretto>(
      future: AppScope.of(context).catalog.load(place.librettoId),
      builder: (context, snapshot) {
        final libretto = snapshot.data;
        if (libretto == null || place.act >= libretto.acts.length) {
          return const SizedBox.shrink();
        }
        return Padding(
          padding: const EdgeInsets.fromLTRB(
            OperaShape.gutter,
            8,
            OperaShape.gutter,
            0,
          ),
          child: Card(
            child: ListTile(
              leading: Icon(Icons.bookmark, color: theme.colorScheme.primary),
              title: Text(l10n.resumeReading),
              subtitle: Text(
                l10n.resumePlace(
                  libretto.title,
                  libretto.acts[place.act].title,
                ),
              ),
              onTap: () => onOpen(
                ReaderScreen(
                  librettoId: libretto.id,
                  act: place.act,
                  offset: place.offset,
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}

class _Message extends StatelessWidget {
  const _Message(this.text);

  final String text;

  @override
  Widget build(BuildContext context) => Center(
    child: Padding(
      padding: const EdgeInsets.all(OperaShape.gutter),
      child: Text(text, textAlign: TextAlign.center),
    ),
  );
}
