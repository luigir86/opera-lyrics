import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:opera_lyrics/library/libretto.dart';
import 'package:opera_lyrics/library/libretto_parser.dart';

void main() {
  final text = File('test/fixtures/esempio.txt').readAsStringSync();

  test('reads the header', () {
    final l = parseLibretto('prova-esempio', text);
    expect(l.id, 'prova-esempio');
    expect(l.title, "L'esempio");
    expect(l.composer, 'Giovanni Battista Prova');
    expect(l.composerSurname, 'Prova');
    expect(l.librettist, 'Anna Verso');
    expect(l.year, 1850);
    expect(l.source, 'Scritto per i test');
    expect(l.license, 'CC0');
  });

  test('splits acts and numbers, keeping the directions before the first', () {
    final l = parseLibretto('x', text);
    expect(l.acts.map((a) => a.title), ['Atto primo', 'Atto secondo']);
    final first = l.acts.first.numbers;
    expect(first.map((n) => n.title), [
      '',
      'Recitativo – Chi bussa?',
      'Duetto – Insieme',
    ]);
    expect(first.first.lines, [
      const LibrettoLine(LineKind.direction, 'Una stanza. È sera.'),
    ]);
    expect(l.acts.last.numbers.single.title, 'Finale');
  });

  test('tells roles, verses, directions and stanzas apart', () {
    final lines = parseLibretto('x', text).acts.first.numbers[1].lines;
    expect(lines, [
      const LibrettoLine(LineKind.role, 'ANNA'),
      const LibrettoLine(LineKind.verse, 'Chi bussa alla mia porta'),
      const LibrettoLine(LineKind.verse, "a quest'ora tarda?"),
      const LibrettoLine(LineKind.stanzaBreak),
      const LibrettoLine(LineKind.role, 'CARLO'),
      const LibrettoLine(LineKind.verse, 'Sono io, apri.'),
      const LibrettoLine(LineKind.direction, 'Anna apre.'),
    ]);
  });

  test('role names are lines in capitals', () {
    expect(isRoleName('VIOLETTA'), isTrue);
    expect(isRoleName('ALFREDO E VIOLETTA'), isTrue);
    expect(isRoleName('CORO DI ZINGARI.'), isTrue);
    expect(isRoleName('Libiamo ne’ lieti calici'), isFalse);
    expect(isRoleName('O'), isFalse);
    expect(isRoleName('...'), isFalse);
  });

  test('a backslash keeps a line a verse', () {
    final lines = parseLibretto(
      'x',
      '# Atto\nANNA\n\\(Che tumulto!)\n\\AH!\n(Parte.)',
    ).acts.single.numbers.single.lines;
    expect(lines, [
      const LibrettoLine(LineKind.role, 'ANNA'),
      const LibrettoLine(LineKind.verse, '(Che tumulto!)'),
      const LibrettoLine(LineKind.verse, 'AH!'),
      const LibrettoLine(LineKind.direction, 'Parte.'),
    ]);
  });

  test('the header alone does not read the acts', () {
    final l = parseLibrettoHeader('x', text);
    expect(l.title, "L'esempio");
    expect(l.acts, isEmpty);
  });

  test('a text with no header or acts gives an empty libretto', () {
    final l = parseLibretto('vuoto', '');
    expect(l.title, 'vuoto');
    expect(l.acts, isEmpty);
  });

  test('line ids name act, number and line', () {
    expect(const LineId(0, 2, 5).toString(), 'a0.n2.l5');
    expect(const LineId(0, 2, 5), const LineId(0, 2, 5));
  });

  test('surnames', () {
    expect(surnameOf('Giuseppe Verdi'), 'Verdi');
    expect(surnameOf('Wolfgang Amadeus Mozart'), 'Mozart');
  });
}
