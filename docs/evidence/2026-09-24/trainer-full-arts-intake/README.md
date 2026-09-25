# Trainer Full Arts intake — received 2026-09-24

These six owner-supplied files were copied byte-for-byte from the primary checkout's disposable `tmp/trainers/` inbox into this linked worktree. The original filenames, contents, and timestamps were preserved; each copy was verified with `cmp`. `SHA256SUMS` records hashes of the archived copies. Receipt date is not a photo capture date. Keep these originals outside the public Hugo asset trees.

| Original | Description / observation | Limits |
|---|---|---|
| `trainers.pdf` | Three-page DoubleHolo “Trainers” lot export, printed 2026-09-24. It lists 31 available-card records and links to `https://doubleholo.com/lot/wo197axgmFs4`. | Catalogue/export entries are proposed matches, not authenticated physical printing, ownership, placement, stamp, finish, grade, or a move. No per-object IDs or image URLs appear in the PDF text. The public lot URL returned HTTP 403 during initial intake. |
| `IMG_7149.HEIC` | Owner-supplied close-up, Japanese ヒガナの信頼 (Zinnia's Trust), 112/076 SAR, as legible in photograph. | Photo is supplemental identity evidence, not proof this card is in one of the three photographed binder pages. |
| `IMG_7150.HEIC` | Owner-supplied close-up, Japanese Cynthia's Ambition (シロナの覇気), 239/172 SAR. | Same placement limit. |
| `IMG_7151.HEIC` | Owner-supplied close-up, Japanese カミツレ (Elesa), 331/151 SR, as legible in photograph. | Same placement limit; Japanese title カミツレ is Elesa, not Candice. Treat any English catalogue mapping as unverified. |
| `IMG_7152.HEIC` | Owner-supplied close-up, Japanese カミツレ (Elesa), 257/151 SR. | Same placement limit. |
| `IMG_7153.HEIC` | Owner-supplied close-up, Japanese カミツレ (Elesa), 226/151 SR. | Same placement limit. |

**Important:** These are intake readings only. Recheck Japanese titles and printed numbers at card-level review before metadata or gallery use. The export and close-ups may include cards outside the photographed three-page gallery; never add or move one merely because it appears here.

## Export-to-photograph reconciliation

The DoubleHolo public search index was reachable even though the lot page returned HTTP 403. A subsequent read-only query of the owner's DoubleHolo Supabase project joined `shared_lots.token = 'wo197axgmFs4'` (lot ID 32699; 31 JSON items) to `cards.id` and `storage.objects.name`, confirming the lot's actual card IDs and available Storage filenames. Ten catalogue objects were initially matched to photographed artwork. After the owner chose a PDF-order digital binder, the public page uses 28 locally stored DoubleHolo catalogue images and one Japanese Olivia photo crop; these are not claims of exact physical printings. Public Storage URLs use `https://navythaxplgdibyahpqb.supabase.co/storage/v1/object/public/card-images/card_images/<ID>/<filename>`; the search index's `primary.webp` URL was stale for IDs 52710, 86661, and 86651, whose usable files are `large.webp` (HTTP 200) and `primary.jpg`. Each selected image's actual source URL, ID, review date, and conservative proxy classification are recorded in `data/card-images.yaml`. The archived photographs and the table below document the old photographic layout; `data/binders/waifu.yaml` now records the owner-requested PDF-order digital layout, not those photographed pocket positions.

| Photographed pocket | Catalogue comparison | Outcome |
|---|---|---|
| P1 R1C1 | Erika's Invitation, DoubleHolo 22801; formerly mistaken for Erika's Hospitality | Cherry-blossom kimono artwork matched and object downloaded; local reference image selected. |
| P1 R1C2 | Raifort, DoubleHolo 46882 | Glasses/blue coat artwork matched and object downloaded; local reference image selected. |
| P1 R1C3 | Professor's Research, DoubleHolo 73297; formerly left unidentified | Photographed white-coat researcher matches the VMAX Climax export artwork, not Worker; local reference image selected. This is not the Volume II Professor Willow promo. |
| P1 R2C1 | Jacinthe, DoubleHolo 52641; formerly left unidentified | Feast artwork matches the Nihil Zero export image (116), rather than the other Jacinthe entry (108); local reference image selected. |
| P1 R2C3 | Furisode Girl, DoubleHolo 34996; formerly mistaken for Erika's Invitation | Autumn kimono artwork matched; local reference image selected. |
| P1 R2C2 | Olivia, export DoubleHolo 16988 | Owner confirms the physical card is Japanese and there are no English cards; the export's English label is erroneous. Supabase has only English Olivia records under that name, so the public binder retains the Japanese photo crop rather than substituting an English scan. |
| P1 R3C1 | Tulip, export DoubleHolo 34512 | The pictured card reads リップ; the exported #92 art differs from the photograph, so the printing is unresolved. |
| P1 R3C2 and P2 R1C1 | Iris's Fighting Spirit, owner-lot DoubleHolo 33366 and 52710 | Both photographed cards read アイリスの闘志, but show different art. Direct Supabase `52710/large.webp` (HTTP 200) matches **P2 R1C1** and was saved locally. The available 33366 artwork differs from **P1 R3C2**. In the replacement PDF-order binder, the catalogue's 33366 artwork is used as a proxy for that PDF entry, not as a match to the photographed pocket. |
| P1 R3C3 | Nemona, export DoubleHolo 36764 and 73302 | The photograph reads ネモ. The 73302 Poké Ball composition matches; local reference image selected. Do not substitute the different 36764 artwork. |
| P3 R1C1 | Misty's Spirit, DoubleHolo 85089 | Swimming-pool artwork matched and object downloaded; local reference image selected. |
| P3 R1C2–C3 | Zinnia's Trust / Tate & Liza's Training, owner-lot DoubleHolo 86661 / 86651 | Search-index `primary.webp` URLs returned HTTP 400; Supabase Storage contains `large.webp` for each (HTTP 200). Both match the photographed art and were saved locally. Do not infer a photographed set/number from a lot match alone. |

The other photographed names can be cross-checked by their Japanese titles and the export, but the export's 31 records are **not** a list of the 13 photographed pockets. The owner confirms **all physical cards are Japanese**; language in the PDF is not authoritative when it contradicts that correction. The public digital Trainer binder uses the 29 Trainer entries in PDF order, omitting the two Pokémon entries (Larvitar and Pyroar ex). In the earlier photographic draft, Tulip and one Iris also used photo crops because their PDF artwork differed from the photos. In the replacement PDF-order binder they show the PDF catalogue artwork as proxies; only Japanese Olivia retains a photo crop. The photo/PDF artwork mismatch is not evidence that either exact physical printing has been verified.

Visual-review JPEGs, if any, were generated only in `/tmp/stage3-trainer-intake-previews/` and are not archival originals or approved gallery derivatives.
