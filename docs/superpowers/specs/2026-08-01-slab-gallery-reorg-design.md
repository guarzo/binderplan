# Slab gallery reorganization — design

**Date:** 2026-08-01
**Branch:** `worktree-slabs-refresh`
**Status:** awaiting approval — no content changes made yet beyond the completed Gold Stars removal

---

## Intent

The graded-card sections of the gallery no longer match the collection. A period of
buying and selling has left 14 cards on the site that are no longer owned, and 20
newly acquired cards with nowhere to live. At the same time the section scheme
itself has a structural problem worth fixing while everything is being touched.

Two outcomes:

1. The site reflects the collection as it actually stands.
2. The gallery index distinguishes between groups that can be *incomplete* and
   groups that cannot.

---

## The two-tier structure

The gallery's graded sections currently sit in one undifferentiated list. But they
answer to two different logics, and the distinguishing question is:

> **Does this group have a defined "outside" — cards that belong to it but aren't owned?**

**Themes** — membership is a judgment call. There is no such thing as a card
missing from a theme, because the theme is defined by what's in it.

- Definitive Pokemon
- Touchstones
- Personal Significance

**Runs** — membership is a fact about the card, independent of opinion. A
"Still Hunting" block is meaningful because the set has an outside.

- Masaki
- Chinese Exclusives *(new)*
- Emolga Masterset

### Rules

- **Every card lives in exactly one section.** No cross-listing. Cross-listing would
  make per-section counts meaningless and force every future edit to be made twice.
  Themes may *link* to Runs where a relationship is worth pointing at.
- Run pages follow the existing Emolga pattern exactly: an owned grid, a `---`, then
  a `## Still Hunting` grid. See `content/gallery/emolga-masterset/_index.md:60-75`.
- **Chinese Exclusives ships with no Still Hunting block.** It is open-ended — an
  ongoing interest in Chinese-exclusive releases, not a completable set. This is a
  deliberate exception to the Run pattern, not an oversight.
- **Masaki does get Still Hunting.** It is a set intended to be completed.

---

## Inventory

36 images in `_inbox/`, each identified by reading its slab label directly. This is
the complete current graded inventory — anything on the site and not in this list is
sold.

### Definitive Pokemon (Theme) — 3 cards

| Source | Card | Grade | Target filename |
|---|---|---|---|
| `charizard.jpg` | 1999 Base Shadowless #4 Charizard Holo | PSA 1 | `definitive_charizard_base_shadowless.jpg` |
| `Umbreon.jpg` | 2017 Sun & Moon 154/149 Umbreon GX Rainbow Rare, Off-Center Error | CGC 8.5 | `definitive_umbreon_gx_rainbow.jpg` |
| `Kyogre.jpg` | 2015 XY Ancient Origins #96 FA Primal Kyogre EX | PSA 3 | `definitive_kyogre_primal.jpg` |

Three cards, three different Pokemon — which fits the section's stated premise
("the card that currently represents a Pokemon best") more cleanly than the outgoing
eight did.

### Touchstones (Theme) — 7 cards

| Source | Card | Grade | Target filename |
|---|---|---|---|
| `Pikachu.jpg` | 2000 Black Star Promo #27 Pikachu | PSA 10 | `touchstone_pikachu_blackstar_2000.jpg` |
| `CelebiGoldStar.jpg` | 2006 EX Crystal Guardians #100 Celebi Gold Star | PSA 5 | `touchstone_celebi_gold_star.jpg` |
| `Professor.jpg` | 2004 EX Ruby & Sapphire 107/109 Psychic Energy, Professor Program '04–'05 | CGC 10 | `touchstone_professor_program_energy.jpg` |
| `Typholosion.jpg` | 2001 JP VS #070 Blaine's Typhlosion, 1st Edition | PSA 7 | `touchstone_typhlosion_vs_1st_ed.jpg` |
| `Shaymin.jpg` | 2009 JP L.V.Mtgrs. Expert Deck: Leafeon Deck #005 Shaymin | PSA 10 | `touchstone_shaymin_leafeon_deck.jpg` |
| `PikaJP.jpg` | 2025 JP M2a #234 Pikachu ex SAR | PSA 10 | `touchstone_pikachu_ex_sar.jpg` |
| `Dragonite.jpg` | 2025 JP M2a #232 Mega Dragonite ex, Mega Attack Rare | PSA 10 | `touchstone_dragonite_mega_ex.jpg` |

Two Pikachu cards here is intentional and not a rule violation — Touchstones marks
eras, not Pokemon, and 2000 Black Star vs. 2025 SAR is precisely the span the section
exists to show.

`CelebiGoldStar` lands here rather than in a Gold Stars section because that section
was deleted; the card is kept as an era/rarity marker.

### Personal Significance (Theme) — 15 cards

| Source | Card | Grade | Target filename |
|---|---|---|---|
| `HoundoomAq.jpg` | 2003 Aquapolis #14 Houndoom Reverse Foil | PSA 5 | `personal_houndoom_aquapolis.jpg` |
| `Houndoom.jpg` | 2015 XY Breakthrough #154 FA/M Houndoom EX | PSA 8 | `personal_houndoom_ex_154.jpg` |
| `Houndoom2.jpg` | 2015 XY Breakthrough #22 M Houndoom EX | PSA 7 | `personal_houndoom_ex_22.jpg` |
| `Houndoor.jpg` | 2000 JP Neo 2 #228 Houndour Holo | PSA 8 | `personal_houndour_neo2.jpg` |
| `GengarEX.jpg` | 2014 XY Phantom Forces #34 Gengar EX | PSA 6 | `personal_gengar_ex_phantom.jpg` |
| `GengarJP.jpg` | 1999 JP Gym 2 #94 Sabrina's Gengar Holo | PSA 2 | `personal_gengar_sabrina_gym2.jpg` |
| `GengarTopps.jpg` | 2000 Topps TV Animation Series 2 #94 Gengar Foil | PSA 8 | `personal_gengar_topps.jpg` |
| `Lickitung-Personal.jpg` | 2006 EX Dragon Frontiers #19 Lickitung Reverse Foil | PSA 8 | `personal_lickitung_dragon_frontiers.jpg` |
| `Mew2nd.jpg` | 2016 XY Evolutions #53 Mew, League Challenge 2nd Place | PSA 8 | `personal_mew_2nd.jpg` |
| `Keckleon.jpg` | 2024 JP Super Electric Breaker 118/106 Kecleon AR | CGC Pristine 10 | `personal_kecleon_jp.jpg` |
| `EmolgaCard.jpg` | 2012 JP Pokémon Playing Cards, White 2 Deck, 3♥ Emolga | CGC Pristine 10 | `personal_emolga_playing_3.jpg` |
| `EmolgaSummer.jpg` | 2011 JP B&W Promo #81 Emolga, Summer Carnival | PSA 9 | `personal_emolga_carnival.jpg` |
| `ShinyEmolga.jpg` | 2013 JP B&W Shiny Collection 1st Ed #023 FA Emolga | PSA 7 | `personal_emolga_shiny_fa.jpg` |
| `Iris.jpg` | 2013 JP B&W Megalo Cannon #082 FA Iris | PSA 7 | `personal_iris_fa.jpg` |
| `Rosa.jpg` | 2026 JP M3 #115 Rosa's Encouragement SAR | PSA 10 | `personal_rosa_sar.jpg` |

This section absorbs two depth clusters — four Houndoom-line cards and three Gengars
(the fourth Gengar belongs to the Masaki run). Both are cases of collecting one
Pokemon in depth for reasons that aren't era-marking or "best version," which is what
Personal Significance is for.

Iris and Rosa are graded singles. The existing `waifu` / "Trainer Full Arts" section
is binder-page spreads, so adding loose slabs there would have broken its format.

### Chinese Exclusives (Run, no Still Hunting) — 6 cards — **new section**

| Source | Card | Grade | Target filename |
|---|---|---|---|
| `eeveeccic.webp` | 2025 CHN CBB2C 宝石包 Vol.2 01/15 Eevee 伊布 | CCIC 10 | `chinese_eevee_cbb2c.webp` |
| `umbreonccic.webp` | 2025 CHN CBB2C Vol.2 06/15 Umbreon 月亮伊布 | CCIC 10 | `chinese_umbreon_cbb2c.webp` |
| `leafeon.webp` | 2025 CHN CBB2C Vol.2 07/15 Leafeon 叶伊布 | CCIC 10 | `chinese_leafeon_cbb2c.webp` |
| `sylveonccic.webp` | 2025 CHN CBB2C Vol.2 09/15 Sylveon 仙子伊布 | CCIC 10 | `chinese_sylveon_cbb2c.webp` |
| `mauseholdccic.webp` | 2025 CHN CSV4C 158/129 Maushold ex SAR | CCIC 10 | `chinese_maushold_ex_sar.webp` |
| `carmine.jpg` | 2026 CHN CSV8 CS #255 Carmine SAR (丹瑜) | PSA 10 | `chinese_carmine_sar.jpg` |

The four CBB2C Vol.2 cards are the full arts of that set — the part of it being
collected. The remaining eleven are not wanted, so the group has no meaningful
"outside" and a Still Hunting block would list cards nobody is hunting. This is why
the section ships without one: not an exception to the Run pattern, but the pattern
applied correctly to a group whose boundary is drawn at full arts rather than at the
set.

The section is open-ended more broadly — Chinese-exclusive releases are an ongoing
interest, not a defined set — which is the second reason no Still Hunting block fits.

`carmine` is routed here on set origin (Chinese CSV8) rather than on character art,
which is why it separates from Iris and Rosa.

### Masaki (Run) — 5 cards

**Owned:**

| Source | Card | Grade | Target filename |
|---|---|---|---|
| `Alakazam.jpg` | 1999 JP Vending #65 Alakazam Holo, Masaki Promo | PSA 5 | `masaki_alakazam.jpg` |
| `GengarMasaki.jpg` | 1999 JP Vending #94 Gengar Holo, Masaki Promo | PSA 4 | `masaki_gengar.jpg` |

**Still Hunting** (plain card scans, not slabs — matching the Emolga convention):

| Source | Card | Target filename |
|---|---|---|
| `golemmasakimissing.webp` | JP Vending #076 Golem | `masaki_golem_wanted.webp` |
| `omastarmasakimissing.webp` | JP Vending #139 Omastar | `masaki_omastar_wanted.webp` |
| `machampmasaki-missing.webp` | JP Vending #068 Machamp | `masaki_machamp_wanted.webp` |

Golem and Omastar were owned and are now sold; their slab photos come down and are
replaced by want-scans. Machamp is new to the site — a want that was never owned.

### Emolga Masterset (Run) — unchanged

Binder pages and its existing Still Hunting block stay as they are. Only the intro
prose changes (see below).

---

## Removals

`static/images/slabs/` currently holds 26 files. **All 26 are removed**, because each
is either sold, orphaned, or superseded by a full-resolution version of the same card.

**Sold — card no longer owned (16):**

`definitive_umbreon_aquapolis` · `definitive_mew_shining_darkness` ·
`definitive_charizard_base_2` · `definitive_kingdra_aquapolis` ·
`definitive_gengar_chinese_2025` · `definitive_plusle_jp` · `definitive_minun_jp` ·
`touchstone_jolteon_pop` · `touchstone_dragonite_expedition` ·
`touchstone_squirtle_expedition` · `touchstone_charizard_jp_basic` ·
`touchstone_umbreon_tag` · `touchstone_charizard_151_jp` · `touchstone_mew_sv4a_jp` ·
`masaki_golem` · `masaki_omastar`

**Orphan — already unreferenced by any page, predating this work (1):**

`personal_kanga_mega_jp`

**Superseded — same card, replaced by the full-size photo under a new name (9):**

`definitive_houndoom_aquapolis` · `masaki_alakazam` · `masaki_gengar` ·
`personal_emolga_carnival` · `personal_emolga_playing_3` · `personal_kecleon_jp` ·
`personal_mew_2nd` · `touchstone_pikachu_blackstar_2000` · `touchstone_maushold_ccic`

Two near-misses recorded deliberately, because they look like re-photographs and are
not:

- New `charizard.jpg` is Base **Shadowless**; the outgoing card was Base Set **2**.
- New `Dragonite.jpg` is 2025 **Mega Dragonite ex**; the outgoing card was
  **Expedition** Dragonite.

Both are a sale plus a separate acquisition, not a replacement.

---

## Prose changes

**`content/gallery/emolga-masterset/_index.md:9`** — currently reads "This binder
sits completely outside the thematic structure of the main volumes." Under the
two-tier scheme Emolga Masterset *is* a Run, so the claim is now false. Rewrite to
keep the personal tone while placing it inside the structure.

**`content/philosophy/grading.md:12-28`** — the "Public Roles" section describes four
roles (Crown Art, Definitive Pokemon, Historical/Touchstone, Personal Significance)
that no longer map to the gallery. Two specific breaks: "Crown Art" has no
corresponding section, and line 23 says Masaki promos sit under Historical/Touchstone
when Masaki is now its own Run. Replacement prose drafted below.

**`content/philosophy/grading.md:35`** — Tier A reads "Crown Art and selected
Historical / Touchstone cards". Depends on the Crown Art decision below.

**`content/gallery/_index.md:19-27`** — the "Special Collections" and "Personal Slabs"
headings are replaced by "Themes" and "Runs", with Chinese Exclusives added and
Masaki and Emolga Masterset moved under Runs.

---

## Drafted prose

### `grading.md` — replacing "Public Roles" (lines 12–28)

> ## Public Roles
>
> Every graded card needs one clear reason to be in plastic, and each card takes
> exactly one. The reasons come in two kinds, and the difference is whether the group
> has an outside.
>
> ### Themes
>
> Membership is a judgment call. There is no such thing as a card missing from a
> theme, because the theme is defined by what's in it.
>
> **Definitive Pokemon** — the card that currently represents a Pokemon best in the
> collection.
>
> **Touchstones** — cards tied to a particular era, release style, or moment in the
> hobby.
>
> **Personal Significance** — cards whose meaning comes from a memory, milestone,
> gift, or personal connection rather than a broader collecting category.
>
> ### Runs
>
> Membership is a fact about the card rather than an opinion, so a run can be
> incomplete — and saying which cards are still missing is part of the point.
>
> **Masaki** — the Communication Evolution mail-in promos, collected as a set I intend
> to finish.
>
> **Chinese Exclusives** — Chinese-market releases, collected as an ongoing interest
> rather than a defined set.
>
> **Emolga Masterset** — every Emolga printing I can track down.
>
> Cards held mainly for trade or resale may still be stored with the collection, but I
> do not treat that as a public curatorial role.

### `grading.md` — Tier A (line 35)

> - Selected Touchstones and standout cards from the runs

### `emolga-masterset/_index.md` — replacing line 9

> I'm working toward every Emolga printing I can track down. It's the longest-running
> of the runs and the only one that will never actually end: one Pokemon across
> languages, eras, and illustration styles, because Emolga is the best and I will not
> be taking questions.

Keeps the closing joke and the personal register, drops the "sits completely outside
the thematic structure" claim, and states its place in the Runs tier without
flattening the voice into taxonomy.

---

## Resolved — Crown Art is dropped

`grading.md:16` defined **Crown Art** as "a favorite art version of a card, where the
grade supports the presentation." No gallery section ever corresponded to it, and
under Themes/Runs there was nowhere for it to go.

**Decision: remove it entirely** — from the Public Roles list and from the Tier A
display rule at line 35. It described a role the philosophy page claimed and the site
never showed. Alternatives considered and rejected: demoting it to a purely physical
display designation, or promoting it to a Theme with its own gallery section (which
would have required pulling cards back out of Definitive Pokemon and Touchstones to
populate it).

---

## Draft captions

Captions match each section's existing voice — Touchstones and Personal Significance
use `<strong>Name.</strong> One sentence.`; Definitive Pokemon and Masaki use bare
names. These are drafts to be edited.

**Definitive Pokemon**

- Charizard Base Shadowless
- Umbreon GX Rainbow
- Primal Kyogre EX

**Touchstones**

- **Pikachu Black Star 2000.** A turn-of-the-millennium Black Star promo. *(unchanged)*
- **Celebi Gold Star.** The Gold Star treatment at the height of its scarcity.
- **Professor Program Energy.** An organized-play reward that never reached retail.
- **Blaine's Typhlosion.** The VS series, where Gym leaders got their own deck identity.
- **Shaymin Leafeon Deck.** A promo tied to a Japanese expert deck release.
- **Pikachu ex SAR.** The modern special-art treatment at full volume.
- **Mega Dragonite ex.** Mega Evolution's return, rendered as spectacle.

**Personal Significance**

- **Houndoom Aquapolis.** Where the Houndoom habit started.
- **M Houndoom EX.** The full-art Mega treatment, in its wider frame.
- **M Houndoom EX 22.** The same Mega, in the set's standard layout.
- **Houndour Neo 2.** The line's beginning, in Japanese holo.
- **Gengar EX.** A modern Gengar with the confetti background.
- **Sabrina's Gengar.** The Gym-era printing, and the oldest Gengar here.
- **Gengar Topps.** The TV animation printing, outside the TCG proper.
- **Lickitung Dragon Frontiers.** A Delta Species oddity worth keeping.
- **Mew 2nd.** Kept for its personal association rather than a collection-wide role. *(unchanged)*
- **Kecleon.** A card whose place in the collection is personal rather than thematic. *(unchanged)*
- **Emolga Playing.** A personal favorite within the wider Emolga collection. *(unchanged)*
- **Emolga Summer Carnival.** A favorite Emolga promo and the card featured on the homepage. *(unchanged)*
- **Emolga Shiny Collection.** The full-art shiny, first edition.
- **Iris.** Black & White full art, kept for the illustration.
- **Rosa.** The modern counterpart, thirteen years later.

**Chinese Exclusives**

- **Eevee.** The starting point of the CBB2C gem-pack Eeveelutions.
- **Umbreon.** Moonlight, in the set's signature holo.
- **Leafeon.** The same treatment turned green.
- **Sylveon.** The brightest of the four.
- **Maushold ex.** A special art from the Chinese Scarlet & Violet line.
- **Carmine.** A Chinese-exclusive trainer special art.

**Masaki** — bare names, matching the existing section: `Alakazam Masaki`,
`Gengar Masaki`; Still Hunting: `Golem Masaki`, `Omastar Masaki`, `Machamp Masaki`.

---

## Image resolution

All 36 incoming images are full-size and exceed the site's de-facto 760px standard,
with three exceptions.

| Group | Count | Size |
|---|---|---|
| PSA slabs | 24 | 1428×2400 – 2593×4325 |
| CGC slabs | 4 | 1987×3266 – 2328×3739 |
| CCIC slabs | 5 | 818×1403 – 905×1600 |
| Masaki want-scans | 3 | **424×589** |

The three Masaki want-scans are below the Emolga Still Hunting precedent (~712×998).
They render in a smaller slot than the owned grid so the cost is limited, but they
will be the softest images in that section. Accepted for now; replacing them later is
a drop-in with no content change.

---

## Cert numbers

Read from the slab labels and recorded for reference. Not published — captions on this
site are thematic, not spec sheets. Pulled from the thumbnails and not yet re-verified
against the full-size images, with the exception of `EmolgaSummer` (71232630, confirmed
8 digits at full size).

PSA: Houndoom 155999936 · Houndoom2 155999935 · HoundoomAq 134023706 ·
Houndour 139289003 · GengarEX 147621297 · GengarJP 148253659 · GengarMasaki 139250373 ·
GengarTopps 147504380 · Alakazam 139250372 · Pikachu 137000703 · PikaJP 148253663 ·
charizard 143050980 · Mew2nd 137000693 · Dragonite 148253664 · Iris 154404046 ·
Rosa 155999965 · carmine 159557893 · Shaymin 136079555 · Kyogre 155678896 ·
Typhlosion 139288950 · Lickitung 138795327 · CelebiGoldStar 136042472 ·
ShinyEmolga 144121995 · EmolgaSummer 71232630

CGC: Professor 6027449263 · Umbreon 6098919001 · Keckleon 6052481113 ·
EmolgaCard 6066919242

CCIC: not recoverable — the cert number is masked by a white block in all five source
photos. Occlusion in the image itself, not a resolution limit.

---

## Verification

1. `hugo` builds clean.
2. Every `<img src>` in `content/` resolves to a file that exists.
3. Every file in `static/images/slabs/` is referenced by exactly one page — this is
   the check that catches a card silently dropped or double-listed during a 36-image
   re-sort, and it enforces the one-section rule mechanically.
4. Section counts match this document: Definitive 3, Touchstones 7, Personal 15,
   Chinese 6, Masaki 2 + 3 hunting. Total 36.
5. No reference anywhere to a removed card or to `gold-stars`.

---

## Excluded

- Volumes I and II, `stamped-cards`, and `waifu` are untouched.
- Emolga Masterset binder pages and its Still Hunting block are untouched; only its
  intro prose changes.
- No layout, template, or CSS changes. The existing `span-*` grid classes are reused.
- No re-verification of cert numbers against full-size images (offered separately).
