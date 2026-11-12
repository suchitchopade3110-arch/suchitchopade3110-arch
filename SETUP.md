# Setup

This folder is the whole profile repo (`suchitchopade3110-arch/suchitchopade3110-arch`).

1. Copy everything here into the profile repo and push to `main`. The existing `snake.yml` workflow can stay; the new README does not use the snake.
2. In the repo, open Settings, Actions, General and set Workflow permissions to "Read and write".
3. Open the Actions tab and run "Render README cards" once. After that it runs daily and keeps the contribution numbers current.

## Changing anything

All the words live in `data/profile.json`: name, tagline, status line, the six job tiles, the kit, the record row and the link buttons. Edit it, push, and the workflow redraws the cards and `README.md`. Do not edit `README.md` by hand; it is generated.

Colours are the `THEMES` table at the top of `scripts/render_cards.py`.

## Running it locally

    python scripts/render_cards.py            # writes cards/ and README.md
    STATIC=1 python scripts/render_cards.py   # writes preview/ with animations frozen at the end state

No packages needed, Python 3.9 or newer. `scripts/fetch_contributions.py` needs a `GITHUB_TOKEN` in the environment.

## Notes

- Job tile descriptions wrap at 31 characters and show three lines at most, so keep them under about 90 characters.
- The fonts cover basic Latin only. Other characters fall back to a system font.
- The four claims in the hero panel are an illustration of claim-level checking, not live data. They are the `CLAIMS` list in `render_cards.py`.
