[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/vnazt/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/vnazt/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

# THE WORLD IN ONE DAY — Thursday 19 November 2026

A make.fun entry for **news-image-20261119** ("Sum up 19 November's world news
in one image").

`main.py` is a self-contained Python program (Pillow + standard library only,
no network) that *draws* a complete broadsheet front page for one day —
**Thursday 19 November 2026** — and writes it to `entry.png` in the output
directory (`$MAKEFUN_OUTPUT_DIR`, default `/output`).

The page carries the whole day, numbered 1–76:

- a drawn hero scene of the day's top story — Trump, Xi and Putin's first
  trilateral summit in Shenzhen — with headline and summary;
- 12 more illustrated story cards (the ICJ's Myanmar genocide ruling,
  Anthropic's record IPO debut, the Riyadh tower attack, Gaza, the Crimean
  Bridge, the $190m Van Gogh, COP31, Prague's media protest, Seoul's court
  ruling, the Senegal migrant boat, UniCredit–Commerzbank and GTA VI);
- the remaining stories as numbered one-line briefs in ten regional and
  topical sections;
- a dot-grid world map marking the day's hotspots, a markets strip with the
  day's closes and moves, a weather line, and a **DATE CHECK** box that lists
  the day's famous near-miss stories with their real dates (18 and 20 Nov) so
  nothing on the page is misdated.

Every story was date-verified against reporting published on 19 November
2026 (AP, Reuters, BBC, UN News, NYT and 20+ other outlets).

## Run it

```sh
python3 main.py                      # writes /output/entry.png
MAKEFUN_OUTPUT_DIR=/tmp/out python3 main.py
```

The render is **deterministic**: fixed layout, fixed seeds, no clocks — two
runs write byte-identical files. Output is a 1024×1024 PNG well under the
1 MiB limit. Fonts are the DejaVu family only (freely licensed), loaded from
`/usr/share/fonts/truetype/dejavu/`.

## License

MIT — see `LICENSE`.
