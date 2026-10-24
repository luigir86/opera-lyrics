import 'libretto.dart';

/// Reads a libretto written in the plain text format of
/// docs/formato-libretti.md:
///
/// ```text
/// title: La traviata
/// composer: Giuseppe Verdi
///
/// # Atto primo
/// (Salotto in casa di Violetta.)
///
/// ## Brindisi
/// ALFREDO
/// Libiamo, libiamo ne' lieti calici
/// ```
///
/// `key: value` lines before the first act are the header; `#` starts an
/// act, `##` a number, a line in capitals names who sings, a line in
/// brackets is a stage direction, a blank line ends a stanza and `//`
/// starts a comment. Anything else is a verse, and so is a line that starts
/// with a backslash, for verses that would read as something else: a sung
/// aside in brackets, or a cry in capitals. The parser never fails on a
/// text: what it cannot place it keeps as a verse.
Libretto parseLibretto(String id, String text) {
  final header = <String, String>{};
  final acts = <Act>[];
  String? actTitle;
  var numbers = <OperaNumber>[];
  String? numberTitle;
  var lines = <LibrettoLine>[];

  void closeNumber() {
    // Trailing blank lines are dropped; a number with no title and no
    // lines (an act that starts straight with "##") is not kept.
    while (lines.isNotEmpty && lines.last.kind == LineKind.stanzaBreak) {
      lines.removeLast();
    }
    if (numberTitle != null || lines.isNotEmpty) {
      numbers.add(OperaNumber(title: numberTitle ?? '', lines: lines));
    }
    numberTitle = null;
    lines = <LibrettoLine>[];
  }

  void closeAct() {
    closeNumber();
    if (actTitle != null) acts.add(Act(title: actTitle!, numbers: numbers));
    actTitle = null;
    numbers = <OperaNumber>[];
  }

  for (final raw in text.split(RegExp(r'\r?\n'))) {
    final line = raw.trim();
    if (line.startsWith('//')) continue;
    if (line.startsWith('## ')) {
      closeNumber();
      actTitle ??= '';
      numberTitle = line.substring(3).trim();
    } else if (line.startsWith('# ')) {
      closeAct();
      actTitle = line.substring(2).trim();
    } else if (actTitle == null) {
      // The header, before the first act.
      final colon = line.indexOf(':');
      if (colon > 0) {
        header[line.substring(0, colon).trim().toLowerCase()] = line
            .substring(colon + 1)
            .trim();
      }
    } else if (line.startsWith(r'\')) {
      lines.add(LibrettoLine(LineKind.verse, line.substring(1).trim()));
    } else if (line.isEmpty) {
      if (lines.isNotEmpty && lines.last.kind != LineKind.stanzaBreak) {
        lines.add(const LibrettoLine(LineKind.stanzaBreak));
      }
    } else if (line.startsWith('(') && line.endsWith(')')) {
      lines.add(
        LibrettoLine(
          LineKind.direction,
          line.substring(1, line.length - 1).trim(),
        ),
      );
    } else if (isRoleName(line)) {
      lines.add(LibrettoLine(LineKind.role, line));
    } else {
      lines.add(LibrettoLine(LineKind.verse, line));
    }
  }
  closeAct();

  return Libretto(
    id: id,
    title: header['title'] ?? id,
    composer: header['composer'] ?? '',
    librettist: header['librettist'] ?? '',
    year: int.tryParse(header['year'] ?? ''),
    source: header['source'] ?? '',
    license: header['license'] ?? '',
    acts: acts,
  );
}

/// Whether [line] names who sings: written all in capitals, with at least
/// two letters ("VIOLETTA", "CORO DI ZINGARI", "ALFREDO E VIOLETTA"). A
/// final full stop or colon is allowed, as in many printed libretti.
bool isRoleName(String line) {
  final letters = line.replaceAll(RegExp(r'[^\p{L}]', unicode: true), '');
  if (letters.length < 2) return false;
  return letters == letters.toUpperCase() && letters != letters.toLowerCase();
}

/// Reads only the header of a libretto, for the library list: it stops at
/// the first act, so a long text costs almost nothing.
Libretto parseLibrettoHeader(String id, String text) {
  final end = RegExp(r'^# ', multiLine: true).firstMatch(text)?.start;
  return parseLibretto(id, end == null ? text : text.substring(0, end));
}
