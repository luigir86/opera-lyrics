import 'package:flutter/material.dart';

import '../app/opera_lyrics_app.dart';
import '../app/settings.dart';
import '../app/style.dart';
import '../l10n/app_localizations.dart';
import '../library/libretto.dart';

/// The text of one act, to scroll while the music plays: the numbers as
/// headings, who sings in the accent, the stage directions muted. It keeps
/// the screen on (if the settings say so) and remembers how far the reader
/// got.
class ReaderScreen extends StatefulWidget {
  const ReaderScreen({
    super.key,
    required this.librettoId,
    required this.act,
    this.number,
    this.offset = 0,
  });

  final String librettoId;
  final int act;

  /// The number to open at, or null for [offset].
  final int? number;

  /// How far down the act to open, when no [number] is given.
  final double offset;

  @override
  State<ReaderScreen> createState() => _ReaderScreenState();
}

class _ReaderScreenState extends State<ReaderScreen> {
  Future<Libretto>? _libretto;
  late int _act = widget.act;
  late ScrollController _scroll = ScrollController(
    initialScrollOffset: widget.number == null ? widget.offset : 0,
  );
  var _numberKeys = <GlobalKey>[];
  AppScope? _scope;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final scope = AppScope.of(context);
    if (_scope == null) {
      _libretto = scope.catalog.load(widget.librettoId);
      scope.screenAwake.keepOn(scope.settings.keepScreenOn);
      final number = widget.number;
      if (number != null) {
        _libretto!.then((_) => _showNumber(number));
      }
    }
    _scope = scope;
  }

  @override
  void dispose() {
    _remember();
    _scope?.screenAwake.keepOn(false);
    _scroll.dispose();
    super.dispose();
  }

  void _remember() {
    final offset = _scroll.hasClients ? _scroll.offset : 0.0;
    _scope?.settings.remember(ReadingPlace(widget.librettoId, _act, offset));
  }

  /// Scrolls to number [n] of the act, once it is drawn.
  void _showNumber(int n) {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted || n >= _numberKeys.length) return;
      final target = _numberKeys[n].currentContext;
      if (target == null) return;
      Scrollable.ensureVisible(target, alignment: 0);
      _remember();
    });
  }

  void _goToAct(int act) {
    final old = _scroll;
    setState(() {
      _act = act;
      _scroll = ScrollController();
    });
    WidgetsBinding.instance.addPostFrameCallback((_) => old.dispose());
    _remember();
  }

  Future<void> _showContents(Act act) async {
    final l10n = AppLocalizations.of(context);
    final picked = await showModalBottomSheet<int>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (context) => SafeArea(
        child: ConstrainedBox(
          constraints: BoxConstraints(
            maxHeight: MediaQuery.sizeOf(context).height * 0.7,
          ),
          child: ListView(
            shrinkWrap: true,
            children: [
              Padding(
                padding: const EdgeInsets.symmetric(
                  horizontal: OperaShape.gutter,
                ),
                child: Semantics(
                  header: true,
                  child: Text(
                    l10n.contents,
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                ),
              ),
              for (final (n, number) in act.numbers.indexed)
                if (number.title.isNotEmpty)
                  ListTile(
                    title: Text(number.title),
                    onTap: () => Navigator.of(context).pop(n),
                  ),
            ],
          ),
        ),
      ),
    );
    if (picked != null) _showNumber(picked);
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final settings = AppScope.of(context).settings;
    return FutureBuilder<Libretto>(
      future: _libretto,
      builder: (context, snapshot) {
        final libretto = snapshot.data;
        final act = libretto != null && _act < libretto.acts.length
            ? libretto.acts[_act]
            : null;
        return Scaffold(
          appBar: AppBar(
            title: act == null
                ? null
                : Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(act.title, overflow: TextOverflow.ellipsis),
                      Text(
                        libretto!.title,
                        overflow: TextOverflow.ellipsis,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Theme.of(context).colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ],
                  ),
            actions: [
              if (act != null && act.numbers.any((n) => n.title.isNotEmpty))
                IconButton(
                  tooltip: l10n.contents,
                  icon: const Icon(Icons.list),
                  onPressed: () => _showContents(act),
                ),
              _TextSizeButton(settings: settings),
            ],
          ),
          body: snapshot.hasError
              ? Center(child: Text(l10n.libraryError))
              : act == null
              ? const Center(child: CircularProgressIndicator())
              : NotificationListener<ScrollEndNotification>(
                  onNotification: (_) {
                    _remember();
                    return false;
                  },
                  child: ListenableBuilder(
                    listenable: settings,
                    builder: (context, _) {
                      _numberKeys = [for (final _ in act.numbers) GlobalKey()];
                      return _ActText(
                        act: act,
                        numberKeys: _numberKeys,
                        size: settings.textSize,
                        controller: _scroll,
                        footer: _ActButtons(
                          hasPrevious: _act > 0,
                          hasNext: _act < libretto!.acts.length - 1,
                          onPrevious: () => _goToAct(_act - 1),
                          onNext: () => _goToAct(_act + 1),
                        ),
                      );
                    },
                  ),
                ),
        );
      },
    );
  }
}

class _ActText extends StatelessWidget {
  const _ActText({
    required this.act,
    required this.numberKeys,
    required this.size,
    required this.controller,
    required this.footer,
  });

  final Act act;
  final List<GlobalKey> numberKeys;
  final double size;
  final ScrollController controller;
  final Widget footer;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final verse = TextStyle(
      fontSize: size,
      height: 1.4,
      color: scheme.onSurface,
    );
    final role = TextStyle(
      fontSize: size * 0.8,
      fontWeight: FontWeight.w700,
      letterSpacing: 0.6,
      color: scheme.primary,
    );
    final direction = TextStyle(
      fontSize: size * 0.85,
      fontStyle: FontStyle.italic,
      height: 1.35,
      color: scheme.onSurfaceVariant,
    );
    final heading = TextStyle(
      fontSize: size * 1.1,
      fontWeight: FontWeight.w700,
      color: scheme.primary,
    );
    // The whole act is laid out at once (a few hundred lines at most), so
    // the index can jump to any number.
    return SingleChildScrollView(
      controller: controller,
      padding: const EdgeInsets.fromLTRB(
        OperaShape.gutter,
        8,
        OperaShape.gutter,
        32,
      ),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(
            minWidth: OperaShape.maxTextWidth,
            maxWidth: OperaShape.maxTextWidth,
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              for (final (n, number) in act.numbers.indexed)
                Padding(
                  key: numberKeys[n],
                  padding: EdgeInsets.only(top: n == 0 ? 0 : size * 1.5),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (number.title.isNotEmpty)
                        Padding(
                          padding: EdgeInsets.only(bottom: size * 0.6),
                          child: Semantics(
                            header: true,
                            child: Text(number.title, style: heading),
                          ),
                        ),
                      for (final line in number.lines)
                        switch (line.kind) {
                          LineKind.role => Padding(
                            padding: EdgeInsets.only(top: size * 0.5),
                            child: Text(line.text, style: role),
                          ),
                          LineKind.verse => Text(line.text, style: verse),
                          LineKind.direction => Padding(
                            padding: EdgeInsets.symmetric(vertical: size * 0.2),
                            child: Text(line.text, style: direction),
                          ),
                          LineKind.stanzaBreak => SizedBox(height: size * 0.6),
                        },
                    ],
                  ),
                ),
              const SizedBox(height: 32),
              footer,
            ],
          ),
        ),
      ),
    );
  }
}

class _ActButtons extends StatelessWidget {
  const _ActButtons({
    required this.hasPrevious,
    required this.hasNext,
    required this.onPrevious,
    required this.onNext,
  });

  final bool hasPrevious;
  final bool hasNext;
  final VoidCallback onPrevious;
  final VoidCallback onNext;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    return Wrap(
      spacing: 12,
      runSpacing: 12,
      alignment: WrapAlignment.spaceBetween,
      children: [
        if (hasPrevious)
          OutlinedButton.icon(
            onPressed: onPrevious,
            icon: const Icon(Icons.arrow_back),
            label: Text(l10n.previousAct),
          ),
        if (hasNext)
          FilledButton.icon(
            onPressed: onNext,
            icon: const Icon(Icons.arrow_forward),
            label: Text(l10n.nextAct),
          ),
      ],
    );
  }
}

/// The size of the text, picked from a short list without leaving the page.
class _TextSizeButton extends StatelessWidget {
  const _TextSizeButton({required this.settings});

  final AppSettings settings;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    return PopupMenuButton<double>(
      tooltip: l10n.textSize,
      icon: const Icon(Icons.format_size),
      initialValue: settings.textSize,
      onSelected: (size) => settings.textSize = size,
      itemBuilder: (context) => [
        for (final size in OperaType.readerSizes)
          CheckedPopupMenuItem(
            value: size,
            checked: size == settings.textSize,
            child: Text(l10n.textSizeSample, style: TextStyle(fontSize: size)),
          ),
      ],
    );
  }
}
