import 'package:flutter/services.dart';

import 'libretto.dart';
import 'libretto_parser.dart';

/// The libretti shipped with the app: every `.txt` file in
/// `assets/libretti/`. Adding an opera means adding a file there, nothing
/// else.
class Catalog {
  /// [files] lists the paths of the libretti in [_bundle]; by default the
  /// bundle's own manifest says (tests hand in a list).
  Catalog(this._bundle, {Future<List<String>> Function()? files})
    // ignore: prefer_initializing_formals, a private named parameter is not allowed
    : _files = files;

  static const folder = 'assets/libretti/';

  final AssetBundle _bundle;
  final Future<List<String>> Function()? _files;
  final _full = <String, Libretto>{};

  Future<List<String>> _paths() async {
    final files = _files;
    if (files != null) return files();
    final manifest = await AssetManifest.loadFromAssetBundle(_bundle);
    return manifest.listAssets();
  }

  /// The libretti with their header only, sorted by composer surname, then
  /// by year and title.
  Future<List<Libretto>> list() async {
    final paths = (await _paths())
        .where((p) => p.startsWith(folder) && p.endsWith('.txt'))
        .toList();
    final libretti = <Libretto>[];
    for (final path in paths) {
      final text = await _bundle.loadString(path);
      libretti.add(parseLibrettoHeader(idOf(path), text));
    }
    libretti.sort(compareLibretti);
    return libretti;
  }

  /// The whole libretto [id], read once and then kept.
  Future<Libretto> load(String id) async {
    final cached = _full[id];
    if (cached != null) return cached;
    final text = await _bundle.loadString('$folder$id.txt');
    return _full[id] = parseLibretto(id, text);
  }

  static String idOf(String path) =>
      path.substring(path.lastIndexOf('/') + 1, path.length - '.txt'.length);
}

/// Composer surname, then year (undated last), then title.
int compareLibretti(Libretto a, Libretto b) {
  final byComposer = a.composerSurname.toLowerCase().compareTo(
    b.composerSurname.toLowerCase(),
  );
  if (byComposer != 0) return byComposer;
  final byYear = (a.year ?? 9999).compareTo(b.year ?? 9999);
  if (byYear != 0) return byYear;
  return a.title.toLowerCase().compareTo(b.title.toLowerCase());
}

/// [libretti], already sorted, in groups by composer, in the same order.
Map<String, List<Libretto>> byComposer(List<Libretto> libretti) {
  final groups = <String, List<Libretto>>{};
  for (final l in libretti) {
    (groups[l.composer] ??= []).add(l);
  }
  return groups;
}
