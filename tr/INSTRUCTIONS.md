# Task: translate Japanese RPG dialogue to English (Samurai Shodown RPG, PS1)

You get a JSON batch file. Each item:
- `id`
- `pages`: list of {portrait, jp}. Each page is one text box in the game (2 lines). `\n` in jp is a line break. `portrait` is a speaker face id (hex) — same id = same speaker; use the context lines to work out who it is.
- `choice` (or null): a Yes/No-style question (`kind: question`, `question`, `options`) or a menu (`kind: menu`, `options`).
- `context`: neighbouring lines from the same scene. Lines with `en` already have the official English translation (by MoriyaMug) — match their tone, terminology and character voices. `{"self": true}` marks where the current item sits.

Write ONE JSON object to the output file: `{"<id>": {"pages": ["...", ...], "question": "...", "options": ["...", ...]}, ...}` (omit question/options when there is no choice).

Rules:
1. Exactly one English string per JP page, same order. Keep each page short: it is shown in a box of 2 lines x 32 characters, so aim for <= 64 characters per page (up to ~90 is tolerated; it will spill into another box). Do NOT put line breaks in your strings; wrapping is automatic.
2. `{NAME}` is the party leader's name inserted by the game. Keep every `{NAME}` exactly as many times as in the JP, in a natural position. Japanese 殿/様 after it is usually dropped.
3. Characters allowed: A-Z a-z 0-9 space . , ! ? ' - ( ) : /   ONLY. No double quotes (use ' instead), no ; & ~ * or ellipsis character (write ...), no accents (Tres bien, not Très), no Japanese.
4. Choice question <= 32 chars, each option <= 16 chars (e.g. Yes / No, Buy / Don't buy, Eat / Don't eat). For menus keep the order of options.
5. Drop furigana readings in parentheses after names, e.g. 綾女（あやめ） -> Ayame. Keep （...） that marks inner thoughts as (...).
6. Money 金１００ -> 100GP. Keep numbers as in JP.
7. Use the glossary spellings (GLOSSARY.md). Keep character voice: Galford/Earthquake sprinkle English, Cham Cham and Pak Pak speak cutely/broken, Charlotte is formal, Wan-Fu style speakers end with 'aru' habit -> render lightly ('...you see', 'yes?'), dialect speakers -> casual. Grunts/laughs: transliterate (Hahaha, Grr..., Ugh!).
8. Translate meaning naturally, like a professional game localization of the 90s, not word-for-word. Don't add content.

When done, run: `python3 -I check.py batch_XX.json out_XX.json` in the same folder and fix every reported error until it prints `errors 0`.
