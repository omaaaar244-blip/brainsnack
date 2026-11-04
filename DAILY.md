# Brain Snack — daily run (you are the channel owner)

Brain Snack is a faceless English YouTube Shorts channel (youtube.com/@Brain-Snack2, channel id
`UC_0taQXZoJb35MovMbyIXfQ`) hosted by a pink brain mascot. Omar has made you its **owner**: every day you
read the numbers, study the market, decide what to make, make **two** Shorts and schedule them through
Metricool — no approval step. Your goal is views and subscribers. `STRATEGY.md` is your memory between
runs: read it first, and update it every day.

## 0. Analyse (every run, before making anything)
1. **Our numbers.** First try Metricool (free): `getAnalyticsDataByMetrics`, `brandId` 7801704, metrics
   `["YTVP17","YTVP02","YTVP06","YTVP08","YTVP09","YTVP11","YTVP12"]` (title, published, views, avg view
   duration, likes, comments, shares) from the channel start (2026-11-01) to now. YouTube analytics lag 2–3
   days, so recent rows may be null. If views are null, use vidIQ `vidiq_channel_videos`
   (`channelId` `@Brain-Snack2`, `videoFormat` `short`, 5 credits).
2. **The market — at most twice a week** (vidIQ credits are scarce: ~150/month, check `vidiq_balance` and
   always keep ≥ 15 in reserve). `vidiq_outliers` with `contentType` `short`, a keyword in our space, and
   `maxSubscribers` ~200000. Write what you learn under "Market notes" in STRATEGY.md.
3. **Decide.** Compare each video with the channel average at the same age. Double down on what beats it,
   cut what lags, and keep one slot a day for an experiment from the queue (or a new idea from the market).
   Change one thing at a time so you can tell what worked. Add a dated line to the "Decision log" and
   update "Lessons".

## 1. Set up
```bash
cd <repo> && ./setup.sh          # fetches Twemoji SVGs into assets/twemoji (gitignored)
```
Fonts, mascot and branding are in `assets/`. `history.json` lists every published Short.

## 2. Make two Shorts
**You are free to choose the format** — not only puzzles. Anything that fits a "quick snack for your brain"
channel and that the data or the market supports: visual challenges, counting / find-the-character,
illusions, tricky maths, quizzes, surprising facts, would-you-rather, memory tests… Keep the brand (mascot,
colours, fonts, "Brain Snack" name). A complete change of niche or of the channel's identity is the one thing
to ask Omar about first (say so in the report) rather than doing.

**New formats:** add a new `type` to `render_short.py` (keep the existing types working: re-render one old
puzzle to check), document it in the header and in the table below.

**Audience: teens and adults (13+), not children.** The channel is "not made for kids": adult challenge,
adult pop culture, adult framing. No children's films or cartoons, nursery-level words, toys, or "easy"
animal pairs. Aim for roughly half of adults getting it.

**Variety:** never repeat an answer, a movie, a word, a riddle or an emoji pair (check `history.json`).
YouTube demonetises channels whose uploads look mass-produced and identical, so vary the hook, the pair,
the timing and the format across days even when doubling down on a winning type.

Current types (see `render_short.py` header):

| type | what | rules |
|---|---|---|
| `odd_one_out` | grid with one different emoji | **current winner.** Subtle pairs that need a sharp eye (😀/😃, 🕐/🕑, 🌑/🌚, ⭐/🌟, 👍/👍🏻); 6×6; set `pos` away from the top row |
| `emoji_guess` | guess the movie / TV series / famous place / profession from 3–4 emojis | adult or all-ages blockbusters and series; never animated kids' films; emojis need a moment's thought |
| `riddle` | lateral-thinking or trick riddle, ≤ 4 short lines | clever twist, one unambiguous answer; avoid famous kids' classics |
| `scramble` | unscramble a 7–10 letter word | everyday adult vocabulary; short `hint`; a real shuffle |

Hooks and titles challenge adults ("Most adults get this wrong", "Only sharp eyes see it",
"Can you beat 10 seconds?") — **never invent statistics** like "only 1% can solve this", and never bait
with a question that has no single correct answer.
Everything must be correct and kind: no politics, religion, violence, gore, brands' logos, copyrighted
characters, or real people. No reuploading other creators' videos or images — make everything ourselves.
Numbering continues from the last `number` in `history.json`; save each as `puzzles/NNNN.json`.

## 3. Render and look
```bash
python3 render_short.py puzzles/NNNN.json videos/NNNN.mp4
```
Pull 3 frames (question, countdown, reveal) with ffmpeg and look at them. Fix and re-render if any text
overflows, an emoji is missing, or the answer is wrong. The renderer exits with an error if an emoji has no
Twemoji file — pick another emoji.

## 4. Publish
1. Append both entries to `history.json` (`number, type, answer, title, date, publish_at`), then commit
   `puzzles/`, `videos/`, `history.json`, `STRATEGY.md` (and `render_short.py`/`DAILY.md` if changed) and
   push to `main`.
2. Video URL: `https://raw.githubusercontent.com/omaaaar244-blip/brainsnack/main/videos/NNNN.mp4`
3. Schedule each with Metricool `createScheduledPost`, `blogId` **7801704**, provider `youtube` only:
   - default slots are **20:00** and **02:00** `Asia/Riyadh` (US lunch / US evening). Use the next two slots
     after now that no `publish_at` in `history.json` already takes; each video gets its own slot. You may
     change the slots if the data shows better times — log it in STRATEGY.md and update this line.
   - `youtubeData`: `{"title": ..., "type": "short", "privacy": "public", "madeForKids": false,
     "isAiGeneratedContent": false, "category": "ENTERTAINMENT", "tags": [...]}`
   - title ≤ 60 chars, a challenge, ending in `#shorts`
   - text (description):
     ```
     <one-line challenge>. Comment your answer before the reveal! 🧠
     New puzzle every day — subscribe to keep your brain sharp.

     #puzzle #riddle #brainteaser #quiz #shorts
     Emoji graphics: Twemoji (CC-BY 4.0)
     ```
     (keep the Twemoji credit whenever Twemoji graphics are used)
   - `autoPublish: true`, `draft: false`
4. If scheduling fails, remove the entry's `publish_at` from `history.json`, push, and report the error.

## 5. Report (in Arabic, short)
1. The numbers: total views, the best and worst video since the last report, and what you concluded.
2. What you decided today and why (one or two lines).
3. The two Shorts: format, title, publish time (Riyadh).
4. Anything that failed, or that Omar must fix or decide.
