# Brain Snack — daily run

Brain Snack is a faceless English YouTube Shorts channel (youtube.com/@Brain-Snack2) of quick interactive
puzzles hosted by a pink brain mascot. Each daily run makes **two** new Shorts and schedules them on
YouTube through Metricool. The owner has asked for this to run with no approval step.

## 1. Set up
```bash
cd <repo> && ./setup.sh          # fetches Twemoji SVGs into assets/twemoji (gitignored)
```
Fonts, mascot and branding are in `assets/`. `history.json` lists every published puzzle.

## 2. Write two puzzles
**Audience: teens and adults (13+), not children.** The channel is set "not made for kids", so the
puzzles must be pitched at grown-ups: a real challenge for an adult, adult pop culture, adult framing.
Nothing that reads as kids' content — no children's films or cartoons, nursery-level words, toys, or
"easy" animal pairs. Aim for roughly half of adults getting it.

Read `history.json` first. Never repeat an answer, a movie, a word, a riddle or an emoji pair.
Use two **different** types per day and rotate across the week. Types (see `render_short.py` header):

| type | what | rules |
|---|---|---|
| `emoji_guess` | guess the movie / TV series / famous place / profession from 3–4 emojis | adult or all-ages blockbusters and series (Titanic, Inception, The Matrix, Breaking Bad, Jaws, Interstellar…); never animated kids' films; emojis should need a moment's thought, not spell it out |
| `odd_one_out` | grid with one different emoji | subtle pairs that need a sharp eye (😀/😃, 🕐/🕑, 🌑/🌚, ⭐/🌟, 👍/👍🏻); 6×6, `seconds` 10 |
| `riddle` | lateral-thinking or trick riddle, ≤ 4 short lines | clever twist, one unambiguous answer; avoid the famous kids' classics |
| `scramble` | unscramble a 7–10 letter word | everyday adult vocabulary; short `hint`; letters a real shuffle that does not spell the answer |

Hooks and titles challenge adults ("Most adults get this wrong", "Only sharp eyes see it",
"Can you beat 10 seconds?") — never invent statistics like "only 1% can solve this".
Everything must be correct and kind: no politics, religion, violence, gore, brands' logos, or real people.
Numbering continues from the last `number` in `history.json`; save each puzzle as `puzzles/NNNN.json`.

## 3. Render and look
```bash
python3 render_short.py puzzles/NNNN.json videos/NNNN.mp4
```
Pull 3 frames (question, countdown, reveal) with ffmpeg and look at them. Fix and re-render if any text
overflows, an emoji is missing, or the answer is wrong. The renderer exits with an error if an emoji has no
Twemoji file — pick another emoji.

## 4. Publish
1. Append both entries to `history.json` (`number, type, answer, title, date, publish_at`), then commit
   `puzzles/`, `videos/`, `history.json` and push to `main`.
2. Video URL: `https://raw.githubusercontent.com/omaaaar244-blip/brainsnack/main/videos/NNNN.mp4`
3. Schedule each with Metricool `createScheduledPost`, `blogId` **7801704**, provider `youtube` only:
   - slots are **20:00** and **02:00** `Asia/Riyadh` (US lunch / US evening). Use the next two slots after
     now that no `publish_at` in `history.json` already takes; each video gets its own slot
   - `youtubeData`: `{"title": ..., "type": "short", "privacy": "public", "madeForKids": false,
     "isAiGeneratedContent": false, "category": "ENTERTAINMENT", "tags": [...]}`
   - title ≤ 60 chars, a challenge, ending in `#shorts` (e.g. `Can You Guess This Movie From 2 Emojis? #shorts`)
   - text (description):
     ```
     <one-line challenge>. Comment your answer before the reveal! 🧠
     New puzzle every day — subscribe to keep your brain sharp.

     #puzzle #riddle #brainteaser #quiz #shorts
     Emoji graphics: Twemoji (CC-BY 4.0)
     ```
   - `autoPublish: true`, `draft: false`
4. If scheduling fails, remove the entry's `publish_at` from `history.json`, push, and report the error.

## 5. Report
One short summary: the two puzzles, their titles and publish times, and anything that failed.
