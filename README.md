# Opera Lyrics

Opera Lyrics is a free, open-source library of opera libretti for Android, to read while the music plays: at home with a recording, or at the theatre. It is built with [Flutter](https://flutter.dev) on the structure of [Low End](https://github.com/luigir86/Low-End), works fully offline and is available in English and Italian.

## What it does

- **Library.** The operas grouped by composer, each with its year and librettist.
- **Opera.** Its acts and, inside each act, its numbers (arias, duets, recitatives, choruses): a touch opens the text there.
- **Reading.** The whole act on one scrolling page: the numbers as headings, who sings in bronze, the stage directions in a muted italic. An index jumps to any number, and the buttons at the end go to the next or the previous act.
- **Comfortable in the dark.** Always dark, five text sizes, and the screen stays on while a libretto is open (it can be switched off in the settings).
- **Picks up where you left off.** The library offers the last act read, at the point it was left.

What comes later, as separate modes inside an opera: **Guess the opera** (recognise what Spotify is playing) and **Sync** (follow the verse being sung). The libretto format already gives every line a stable place, so the timings can be attached to it.

## Adding an opera

One text file in [`assets/libretti/`](assets/libretti/), nothing else: the format is in [docs/formato-libretti.md](docs/formato-libretti.md). `flutter test` checks every file.

## Free, light and private

- **Open source** under the [MIT License](LICENSE). The libretti are in the public domain; each file says where its text comes from and under which terms that transcription is shared (see [assets/libretti/README.md](assets/libretti/README.md)).
- **Private**: no account, no internet, no ads, no tracking, no permissions at all. See [PRIVACY.md](PRIVACY.md).
- **Light**: four small packages (`shared_preferences`, `wakelock_plus`, `url_launcher`, `intl`).

## Building

```
flutter pub get
flutter analyze
flutter test
flutter run
```
