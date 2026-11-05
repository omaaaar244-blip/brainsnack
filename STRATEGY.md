# Channel strategy & owner's log

The daily run acts as the channel's owner: it reads the numbers, studies the market, decides what to make,
and records every decision here. Newest entries at the top of each section. Keep this file short — condense
old log lines into "Lessons" once they are settled.

## Lessons (what the data says so far)
- Visual hunt beats text. Week 1: "Only Sharp Eyes Can Spot The Different Smile" (odd_one_out) = 967 views,
  ~74% of all channel views. Emoji movie guess 201 / 29; riddle 54; scramble 64.
- Zero comments on every video so far despite "comment your answer" — the CTA is not working yet.

## Market notes (vidIQ outliers)
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
