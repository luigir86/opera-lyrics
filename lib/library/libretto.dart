/// A libretto, as read from a text file in `assets/libretti/`
/// (the format is in docs/formato-libretti.md).
class Libretto {
  const Libretto({
    required this.id,
    required this.title,
    required this.composer,
    this.librettist = '',
    this.year,
    this.source = '',
    this.license = '',
    this.acts = const [],
  });

  /// The file name without `.txt`, e.g. `verdi-la-traviata`.
  final String id;
  final String title;
  final String composer;
  final String librettist;
  final int? year;

  /// Where the text was taken from: a link or a book.
  final String source;

  /// Under what terms the text is shared.
  final String license;
  final List<Act> acts;

  /// The composer's surname, which the library sorts and groups by.
  String get composerSurname => surnameOf(composer);
}

/// The last word of [name], skipping particles such as "von" and "de":
/// "Giuseppe Verdi" → "Verdi", "Wolfgang Amadeus Mozart" → "Mozart".
String surnameOf(String name) {
  final words = name.trim().split(RegExp(r'\s+'));
  return words.isEmpty ? '' : words.last;
}

class Act {
  const Act({required this.title, this.numbers = const []});

  /// "Atto primo", "Prologo".
  final String title;

  /// The numbers in the order they are sung. The first may have an empty
  /// title: the stage directions before the first number.
  final List<OperaNumber> numbers;
}

/// A number of the opera: an aria, a duet, a recitative, a chorus. On a
/// recording it is usually one track.
class OperaNumber {
  const OperaNumber({required this.title, this.lines = const []});

  final String title;
  final List<LibrettoLine> lines;
}

enum LineKind {
  /// The name of who sings next: "VIOLETTA", "ALFREDO E VIOLETTA".
  role,

  /// A verse.
  verse,

  /// A stage direction, written in brackets in the file.
  direction,

  /// A blank line between two stanzas.
  stanzaBreak,
}

class LibrettoLine {
  const LibrettoLine(this.kind, [this.text = '']);

  final LineKind kind;
  final String text;

  @override
  bool operator ==(Object other) =>
      other is LibrettoLine && other.kind == kind && other.text == text;

  @override
  int get hashCode => Object.hash(kind, text);

  @override
  String toString() => '${kind.name}($text)';
}

/// Where a line is in its libretto: act, number and line, counted from 0.
/// It is what a later "Sync" will attach times to, so it must not change
/// when the app changes: it changes only if the text file is edited above
/// that line.
class LineId {
  const LineId(this.act, this.number, this.line);

  final int act;
  final int number;
  final int line;

  @override
  String toString() => 'a$act.n$number.l$line';

  @override
  bool operator ==(Object other) =>
      other is LineId &&
      other.act == act &&
      other.number == number &&
      other.line == line;

  @override
  int get hashCode => Object.hash(act, number, line);
}
