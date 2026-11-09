# Channel strategy & owner's log

The daily run acts as the channel's owner: it reads the numbers, studies the market, decides what to make,
and records every decision here. Newest entries at the top of each section. Keep this file short — condense
old log lines into "Lessons" once they are settled.

## Lessons (what the data says so far)
- Visual hunt beats text. Week 1: "Only Sharp Eyes Can Spot The Different Smile" (odd_one_out) = 967 views,
  ~74% of all channel views. Emoji movie guess 201 / 29; riddle 54; scramble 64.
- Zero comments on every video so far despite "comment your answer" — the CTA is not working yet. 11-09: testing a
  low-effort comment ask (type 5 letters) instead.

## Market notes (vidIQ outliers)
- 2026-11-09: vidIQ 0 credits -> WebSearch. Roundups again name Friend Group POV skits, before/after reveals,
  hard-hook Shorts under 60 s; engagement/interactive formats (would-you-rather, this-or-that) and oddly satisfying
  loops remain evergreen faceless outliers. No hard view numbers available.
- 2026-11-08: vidIQ 0 credits (resets 12-02) -> WebSearch. November roundups: "Friend Group POV" skits (the friend who
  makes the plans / keeps the group together) trending; hard hook in second one; November = seasonal/cozy autumn content;
  faceless text-on-screen explainers and text/chat stories keep working. No hard view numbers in the sources.
- 2026-11-06: vidIQ 0 credits (resets 12-02) -> WebSearch. Oct/Nov roundups: faceless explainers with clear
  captions, meme-template animations, POV skits, myth-breaking Shorts and countdown/ranking lists named as the
  working formats; hard hook in the first second (payoff/surprise, no intro); seasonal/cozy content in November.
- 2026-11-05: vidIQ balance 0 credits (resets 2026-12-02) -> WebSearch only. Faceless-Shorts studies: single
  facts / quick tips at 13-18 s with a curiosity-gap hook and a payoff near the loop point; "find the number"
  single-image hunts still everywhere in eye-test content.
- 2026-11-04, Shorts, "brain teaser / test your eyes", channels < 200K subs: the breakouts are
  **very short (6–8 s) single-image visual challenges** that loop: "how many 7s are in this photo"
  (991K, 124x), "Be honest, what did you see at first glance?" (3.1M, 116x), "find the number 02",
  "I see 7 cats, do you?", "how many 15s are there". Also "Can Gen Z work out this EASY question?"
  (611K) — a simple maths/logic question framed as a generational challenge.
- Takeaway: shorter videos + a single image to scan + a counting/finding question. Our videos are 14–17 s.

## Experiments queue (optional ideas)
1. Shorter odd_one_out: `seconds` 5–6 so the whole video is ~9–10 s and loops.
2. New type "find the hidden character": a grid of one glyph with one look-alike (8 among 3s, O among Q,
   rn among m) — the market's "find the number" format. Needs a text-glyph mode in render_short.py.
3. New type "count": "How many ▲ do you see?" — a scene of overlapping emojis/shapes; answer revealed.
4. Simple-but-tricky maths with ONE correct answer (e.g. 8 − 2 × 3 + 1 = 3), framed "Most adults get this wrong".

## Decision log
- 2026-11-09: Metricool still null (only the 6 oldest rows), vidIQ 0 -> no numbers for a 4th run; #13/#14 confirmed
  published. Two new kinds: #15 interactive "Would you rather" x5 (renderers/wyr.py, 19 s) aimed at our zero-comment
  problem ("comment your 5 letters"), and #16 satisfying sorting race bubble vs quick sort (renderers/sort.py, real
  computed comparison counts, generated tones, 24 s). Watch: comments on #15.
- 2026-11-08: Metricool still null for every video (only the 6 oldest rows listed, no views), vidIQ 0 -> still no
  numbers; the 11-07 run did not happen (no commit), so #11/#12 published from the 11-06 run. Followed the market:
  #13 "friend group POV" as an animated group-chat text story (new renderers/chat.py, COMEDY, 22 s) and #14 seasonal
  autumn science explainer, a drawn leaf changing colour (new renderers/leaf.py, generated chords, EDUCATION, 23 s).
  Next: get real numbers (Metricool lag is now >5 days, consider vidIQ once credits reset 12-02) and compare genres.
- 2026-11-06: no numbers yet (Metricool views null, only 6 rows; vidIQ 0). Kept the daily genre rotation with
  two new formats/looks: #11 cooking recipe card (renderers/recipe.py, cream card + generated marimba, 24 s,
  HOWTO_STYLE) and #12 myth-buster list (renderers/myth.py, navy + MYTH stamp, 27 s, EDUCATION). Shared helpers
  in renderers/common.py. Next: compare recipe/myth/story/scale once views arrive (~11-08).
- 2026-11-05 (Omar): "change everything as if I started a new channel — content about anything, varied every
  day: weird facts one day, cooking another, animation + music + something sad that touches the heart...
  not only these, your choice." -> rotate genres daily, two different kinds per day. #10 Venus fact replaced
  by an animated heartfelt story with generated piano (renderers/story.py). Next run: try cooking.
- 2026-11-05 (Omar, again): "I told you to change the content - why is it still the same?" -> NO MORE PUZZLES
  of any kind (find-the-odd, emoji guess, riddle, scramble). The channel is now a facts/explainer channel
  (space, science, the world), visual formats like scale lists and one-line facts. #9 "find the 8" was
  replaced before publishing by a scale list (renderers/scale.py, light travel time).
- 2026-11-05: Metricool views still null (2-3 day lag), vidIQ 0 credits -> no fresh numbers; acting on the
  11-04 market notes. New minimal black-screen identity (renderers/minimal.py, Inter font): #9 find_glyph
  "find the 8 among Bs", 8 s loop (experiment 2 + shorter); #10 first "fact" Short (Venus spin vs year), 16 s,
  EDUCATION. Compare both vs odd_one_out once numbers arrive.
- 2026-11-04 (Omar): puzzles are not important — any topic, any identity, any style. Find what is
  breaking out on Shorts every day and make our own version fast. The experiments queue is optional.
- 2026-11-04 (superseded by the line above): odd_one_out every day; riddle/scramble ≤ 2×/week.
