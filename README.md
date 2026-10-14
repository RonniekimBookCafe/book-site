# book-site
Official book hub for published books, sample chapters, table of contents, FAQs, and purchase links.

## Site structure

Static HTML served by GitHub Pages (no build step, no framework).

```
index.html                         Home (book grid rendered from assets/js/books-data.js)
{ko|en}/books/book-NNN/            Book pages: index · toc · sample · faq · buy
{ko|en}/books/book-NNN/learn/      Video & web extras (RoboCo series only, opened in a new tab)
{ko|en}/books/book-NNN/v/{VIDEO-ID}/  Permanent QR address for each official video (inside the book folder)
{ko|en}/books/book-NNN/course.html   Book sets by goal + class schedules (elementary → adult)
assets/js/media/book-NNN.js       Videos, playlist, and sample pages per book (edit this to add media)
assets/js/book-media.js           Renders media data into the pages
{ko|en}/books/book-NNN/downloads/ Digital Package page; files live once under ko/ (robots/, start file + library,
                                   ZIPs, record-sheets/, manifest.json, SHA256SUMS.txt); en/ holds its own record sheets
assets/css/series-roboco.css       Styles used only by RoboCo series pages
assets/images/books/book-NNN/      Covers, OG images, figures/
assets/images/books/book-005/web/  Web-only explanatory images C01-WEB-01…17 (ko/en WebP)
sitemaps/books/book-NNN.xml        Per-book sitemap, listed in sitemap.xml
```

## Physical AI with RoboCo — fixed Book IDs

| Series code | Site Book ID | Video ID prefix | Status |
|---|---|---|---|
| CORE-01 | book-005 | C01 | Published (ko + en pages) |
| CORE-02 | book-006 | C02 | Upcoming — Korean placeholder pages |
| CORE-03 | book-007 | C03 | Upcoming — Korean placeholder pages |
| QUAD-01 | book-008 | Q01 | Upcoming — Korean placeholder pages |
| QUAD-02 | book-009 | Q02 | Upcoming — Korean placeholder pages |
| QUAD-03 | book-010 | Q03 | Upcoming — Korean placeholder pages |

Upcoming covers are placeholders ("표지 준비 중"); replace `cover-large-ko.webp`, `cover-thumb-ko.webp`,
`og-ko.webp` in each `assets/images/books/book-NNN/` folder. The CORE-03 accent `#7DC242` is provisional.

Later Physical AI series (robot hand, face robot, robot arm, drone, hexapod, biped …) continue from book-011.
In `books-data.js`, RoboCo books carry `series: "roboco"`, `seriesCode`, `category: "robotics"`, and,
before publication, `status: "upcoming"`, an empty `publishedAt`, and a `badge` label per language.

## Adding videos and sample pages (no HTML edits)

Edit `assets/js/media/book-NNN.js`:

- **Publish a video** — paste the 11-character YouTube ID into `"youtube"` for that video ID.
  Every placeholder with that ID (web companion, `/v/{ID}/` QR page) becomes an embedded player with a YouTube link.
- **Playlist** — paste the playlist URL into `"playlist"`; a "YouTube 재생목록" button appears.
- **New video** — append an object to `"extraVideos"`; it appears under "새로 추가된 영상".
- **Sample page** — save `sample-ko-NN.webp` in `assets/images/books/book-NNN/` and append it to `"samples"`;
  the sample page shows a "지면 미리보기" gallery.

## Turning an upcoming book into a published one

1. Replace the placeholder cover/OG images.
2. In `books-data.js`: set `publishedAt`, remove `status`, change `badge` to "신간", set `button`.
3. Replace the pending cards in `buy.html` with store links; change badges on index/faq/learn pages.
4. Add Digital Package files under `ko/books/book-NNN/downloads/` (see book-005) and regenerate `manifest.json`.
5. Update the CORE-01 and other books' series tables and `course.html` statuses (generated from one list).

CORE-01 store links currently open a **title search** at each store; swap them for product URLs when available.

## Web companion policy (v1.2)

The `learn/` page is **not** a copy of the book. It carries only what the book cannot or should not hold:
run videos, side-by-side comparison videos, failure scenes, install recordings, web-only challenges,
practice-file downloads, versions, and errata. Each item says *what to watch* and links to the chapter
that explains *why* and *how*. Do not post the book's tables, code listings, Port maps, parameter tables,
troubleshooting tables, or manuscript figures on the web (the sample page keeps one figure, C01-S01).

Web-only video IDs (no QR in the book):

| ID | Content | Book chapter | YouTube |
|---|---|---|---|
| C01-W01 | Eight motions, one key at a time | CH10 | `Rox7nBVuzTo` |
| C01-W02 | Slope climb: low vs. high power | CH17 | — |
| C01-W03 | Stopping distance: short vs. long braking time | CH19 | — |
| C01-W04 | Steering change: together vs. staggered | CH18 | — |
| C01-W05 | Failure: wheels spin on a slope | CH17 | — |
| C01-W06 | Failure: key pressed, no response | CH12, CH24 | — |
| C01-W07 | Failure: mission overshoots the target | CH23, CH25 | — |
| C01-W08 | Install & first-run screen recording | Getting Started | `UJiqc7WV-II` |

Book QR video IDs keep the `C01-CC-NN` form (same ID as the figure they extend) and get a page at `/{lang}/books/book-NNN/v/{ID}/`.

| Book QR ID | Video | Book location | YouTube |
|---|---|---|---|
| C01-06-00 | Robot structure & exploded view | CH06, next to figure C01-06-00 | `9eBLvXMD51U` |
| C01-07-00 | Microcontroller Port connections | CH07 (7.2), next to figure C01-07-00 | `TCCaK7J9d48` |
| C01-25-00 | Guide robot final mission | CH25 (25.1), next to figure C01-25-00 | `CD96tZ2EnUM` |

When a video goes public: set its ID in `assets/js/media/book-005.js` (live immediately). If you regenerate the
site, also set it in `series_data.YOUTUBE` so the player is rendered statically and the `noindex` tag is dropped.

## Changelog

- **v1.15 (2026-10-14)**
  - CORE-01 (book-005): add permanent QR landing pages for `C01-W02`–`C01-W07` in both Korean and English
 (12 HTML pages).
  - Link to each landing page from the existing videos in Korean/English `learn/index.html` without chang
ing YouTube IDs.
  - Extend `sitemaps/books/book-005.xml` with the 12 new URLs.
  - Print QR images should encode the permalink `/ko/books/book-005/v/<VIDEO_ID>/`, not YouTube directly.
 Verify deployment and mobile scanning before printing.


- **v1.14 (2026-10-10)**
  - Desktop reading width (series-roboco.css, `@media (min-width: 1024px)` only). On wide monitors the book pages
    filled the whole window because a shared rule in style.css resets `.layout` to `max-width: 100%`. Book-005–010
    pages now sit in a centred 1280px frame (240px sidebar + 32px gap + 960px content card). At 1920px the main
    video went from 1534 × 863 to 894 × 503 and fits on one screen; figures render at 864px. Header text uses the
    same 1232px line so the title lines up with the sidebar (`body:has(> .layout)`; /v/ pages keep their 980px column).
  - Mobile and tablet (< 1024px) unchanged. style.css/book.css untouched, so book-001–004 are unaffected.

- **v1.13 (2026-10-10)**
  - Six web-only videos published on YouTube (series_data.YOUTUBE → assets/js/media/book-005.js and the
    learn page ko/en): C01-W02 kfBA4yUwPuk, C01-W03 rbUbGB2ueI8, C01-W04 AW76p-tNCHw, C01-W05 sHlhZDKaORM,
    C01-W06 SAlQcQ_8GWs, C01-W07 OhDsglJrOVw. Their cards now carry the player (built statically, works without JS)
    instead of a "Coming soon" thumbnail. The hero counter shows 11 published videos, and the pending line disappears
    once nothing is pending. Comparison and failure sections get the "On YouTube" badge.
  - C01-W04 label in the media data now matches the YouTube title: "조향 전환 — 앞뒤 동시 vs 시간차".
  - CSS: players inside .rk-vcard fill the card top; the watch link is indented to match the card text.
  - C01-06-00, C01-07-00, C01-25-00 IDs were already the ones supplied; unchanged.

- **v1.12 (2026-10-09)**
  - Book sets by goal, second author draft (series_data.COMBOS → course pages ko/en and book-006–010, image
    C01-WEB-11 ko/en): "Picking and placing with a robot arm" = CORE-03 + QUAD-03 (MANIPULATE → WORK); "The full CORE track" = CORE-01 + CORE-02 + CORE-03 + QUAD-03 (MOVE → SENSE → MANIPULATE →
    WORK); "Walking on four legs" = QUAD-01 + QUAD-02 + QUAD-03 (WALK → DECIDE → WORK); "A quadruped that decides
    for itself" = QUAD-02 + QUAD-03 (DECIDE → WORK). Other rows unchanged. Record-sheet PDFs kept from v1.11.

- **v1.11 (2026-10-09)**
  - Practice code: each language page links only its own edition. Korean pages (book page, web companion,
    practice files) offer only `Book_C01_Robot_release_v1.6.3_kr.zip`; English pages only `…_en.zip`. The
    two-edition comparison text and the other-language button/row were removed. Both ZIPs stay in
    manifest/SHA256SUMS as checksum records.
  - Book sets by goal (series_data.COMBOS → course pages ko/en and book-006–010, image C01-WEB-11 ko/en), from the
    author's draft: "Robots that sense and react" = CORE-02 + CORE-03 + QUAD-02 + QUAD-03; "A quadruped that walks
    and works" = QUAD-03 only.

- **v1.10 (2026-10-09)** — Practice code updated to the final release **1.6.3**.
  - Downloads: `Book_C01_Robot_release_v1.6.3_kr.zip` (ko) and `Book_C01_Robot_release_v1.6.3_en.zip` (en), both
    the author's files as supplied (SHA-256 `8ccad6d5…` / `24b30515…`); the extracted `Book_C01_Robot` folders match
    them. All v1.6.0 ZIPs removed; manifest/SHA256SUMS regenerated (41 entries).
  - `tools/i18n/verify_zips.py` on the two 1.6.3 ZIPs: same 17 entries, 8,952 code tokens identical; 0 Hangul in en.
    Line numbers differ only in `c01lib_drive.py` and `c01lib_experiment.py` (longer English docstrings); the start
    file's line numbers (README: 32/55/79/94/109) match.
  - Content aligned with 1.6.3: no power ratios (all eight keys use `TARGET_RPM`), Max Torque fixed (6290, logged as
    `SETUP Motor (fixed)`), Part 4 experiments = RPM, ACCEL, BRAKE F, BRAKE T over 10 levels (values, not
    multipliers), values kept when key 2 picks the next one, folding the screen with key 1 = Reset All, robot screen
    line 3 `RPM 120`, default mission turn 0.5 s. Updated: book page cards/outcomes, PART 1/4 summaries, course labels,
    comparison/failure video notes (C01-W02, W05), record sheet 1 (parameters, LV /10, motor table with fixed TORQUE),
    figures C01-WEB-01, 02, 03, 09, 10, 15 (ko/en), version strings.
  - Not changed (book text): table-of-contents titles 3.1, 9.1, 9.3, 17.2, 17.3 still mention power ratio / Max
    Torque; the run videos were recorded with 1.6.0.

- **v1.9 (2026-10-09)** — Practice code published as two named editions; nothing else removed.
  - `ko/books/book-005/downloads/Book_C01_Robot_release_v1.6.0_kr.zip`: the confirmed release (Korean comments)
    exactly as supplied, only renamed with `_kr` (SHA-256 `2a8ca7bd…bdf3a4`, unchanged since v1.6). The old
    un-suffixed `Book_C01_Robot_release_v1.6.0.zip` is removed.
  - `en/books/book-005/downloads/Book_C01_Robot_release_v1.6.0_en.zip`: same code, English comments, docstrings
    and README, revised for natural US English (key lists like `W/S/A/D`, module docstrings re-wrapped).
    Every file keeps the Korean edition's line count, so line numbers quoted in the book match both editions.
  - Proof: `tools/i18n/apply.py` (AST, code tokens, token line positions) and `tools/i18n/verify_zips.py`
    (run on the two published ZIPs: same 17 entries, 8,635 code tokens identical in value, line and column,
    0 Hangul in the English ZIP).
  - Web companion "Start file and Educational Library" card now offers both ZIPs on both languages (own language
    first); practice-files pages, manifest/SHA256SUMS and image C01-WEB-15 use the new file names.

- **v1.8 (2026-10-09)** — Fine-tuning of v1.7; nothing removed.
  1. Book sets by goal (all RoboCo course pages, ko/en, and image C01-WEB-11): "robots that sense and react" now
     marks CORE-02 only, "picking and placing with a robot arm" marks CORE-03, "walking on four legs" marks QUAD-01.
  2. C01-W01 (eight motions, `Rox7nBVuzTo`) and C01-W08 (install & first run, `UJiqc7WV-II`) are public and embedded
     on the web companion; the video counter now reads 5 public / 6 coming.
  3. Practice code in two editions with identical code: `Book_C01_Robot_release_v1.6.0.zip` (Korean comments,
     the confirmed release, unchanged) on the ko download page and `Book_C01_Robot_release_v1.6.0_en.zip`
     (English comments, docstrings and README) on the en page; each page also links the other edition. Only
     comment and docstring tokens were replaced; for all 14 .py files the AST (docstrings blanked) and the code
     token stream are identical to the Korean release (`tools/i18n/apply.py`). Both ZIPs are in manifest/SHA256SUMS.
  4. English pages contain no Hangul: static scan (`tools/scan_hangul.py`) and rendered-DOM scan after JS
     (`tools/domscan_en.py`) both 0. English cover/OG images (`cover-*-en.webp`, `og-en.webp`) now show the cover
     text in English with a "Korean edition" label (`tools/make_cover_en.py`); sample figure `C01-S01-en.svg` added.
     Exception outside our control: the YouTube player itself shows each video's own (Korean) title.
  5. English copy rewritten for natural US English across the book, contents, sample, FAQ, buy, course,
     web companion, downloads and QR pages, figure captions/alt text, and 9 English web images.

- **v1.7 (2026-10-09)** — 17 web-only explanatory images (34 files, ko/en) added to the CORE-01 pages; all v1.6
  content kept. Each image comes from one idea-generation technique: mind map, mandal-art, storyboard (×3),
  customer journey map, starbursting, rolestorming, Crazy 8s, reverse brainstorming, TRIZ, SCAMPER, morphological
  analysis, backcasting, affinity diagram, flow map, scenario map. Drawn with the roboco-figure-style rules as SVG
  (generator `figs.py` + SVG sources in `CORE-01_web_figures_V1.7_source.zip`, Pretendard) and rendered to WebP; no AI image generation. Placement: book page (6),
  contents, FAQ, buy, course plans, web companion (5), practice files (2). Captions carry the technique name;
  every image has alt text and a tap-to-enlarge link.

- **v1.6 (2026-10-08)** — All three book-QR videos public: C01-06-00 (`9eBLvXMD51U`), C01-07-00 (`TCCaK7J9d48`),
  C01-25-00 (`CD96tZ2EnUM`); static players on the book page (new "영상으로 먼저 보기"), web companion and QR pages,
  all QR pages indexable and in the sitemap. Digital Package moved under the book folder:
  `ko/books/book-005/downloads/` holds both robot files, `Book_C01_Robot` (start file + Educational Library),
  the two ZIPs, `manifest.json` and `SHA256SUMS.txt`; `assets/downloads/` removed. New download pages (ko/en).
  Printable experiment & mission record sheets (A4 × 3, HTML print view + PDF, ko/en) from Appendix I tables
  plus a web-only challenge sheet. FGI fixes: purchase-first CTA, wrong QR address text corrected, playlist button
  no longer shows when no playlist is set, robot 2 file name aligned to the shipped file, "실습 파일" in every
  CORE-01 sidebar, record sheets linked from the course plan. `.nojekyll` added so `__init__.py` is served.

- **v1.5 (2026-10-08)** — C01-25-00 linked to YouTube (`CD96tZ2EnUM`), embedded statically on the web companion and
  its QR page (now indexable). New robot-structure section with C01-06-00 (exploded view) and C01-07-00 (Port wiring)
  QR pages and poster frames. Robot files `Book-CORE-01-CONTROLS` / `Book-CORE-01-SCRIPT_PART` downloadable, with previews.

- **v1.4 (2026-10-08)** — CORE-01 presented as published (badges, store search links, practice-code download).
  Placeholder sites for CORE-02, CORE-03, QUAD-01, QUAD-02, QUAD-03 (Korean, same page set as CORE-01, DOC-035 TOCs).
  New `course.html` on every RoboCo book: book sets by goal and class schedules for elementary, middle, high school,
  university, and adults. QR video pages moved under each book folder. Home sorts newest first with a separate
  upcoming-series row. Videos and sample pages are now data-driven (`assets/js/media/`).

- **v1.2 (2026-10-08)** — Real CORE-01 cover applied (cover, thumbnail, OG). Book page rewritten for sales:
  manuscript figures removed, outcomes section added, cover subtitle/tagline and publisher (PUBPLE) added.
  Web companion rebuilt as video-first, web-only content; manuscript tables, code, and figures removed.
  TOC page no longer shows PART figures. Unused manuscript SVGs removed from `assets/`.
- **v1.1** — book-005 (CORE-01) pages, learning hub, `/v/C01-25-00/`, home card, sitemap.
