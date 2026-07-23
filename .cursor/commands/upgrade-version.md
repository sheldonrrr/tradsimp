# /upgrade-version — Bump plugin version

Follow the project rule in `.cursor/rules/version-update.mdc` end-to-end.

## Target version

- If the user wrote a version after the command (e.g. `/upgrade-version 3.5.5`), use that `X.Y.Z`.
- Otherwise infer the next semver from the current `PLUGIN_VERSION` in `__init__.py` and the nature of uncommitted/recent work:
  - features → MINOR
  - fixes only → PATCH
  - breaking → MAJOR
- State the chosen version before editing; if ambiguous, ask once.

## Required updates (keep it simple)

1. `__init__.py`
   - `PLUGIN_VERSION_TUPLE = (X, Y, Z)`
   - `PLUGIN_VERSION = 'X.Y.Z'`
   - `PLUGIN_RELEASED` / `PLUGIN_ABOUT_LAST_UPDATED` → today’s date (match existing formats)
2. README version lines (keep in sync):
   - `README.md` → `Current version: X.Y.Z`
   - `README.zh-CN.md` → `当前版本：X.Y.Z`
   - `README.zh-TW.md` → `目前版本：X.Y.Z`
3. `i18n.py` → `Plugin catalog released` date strings if the release date changed

Verify with:

```bash
grep -n "PLUGIN_VERSION\|PLUGIN_VERSION_TUPLE\|PLUGIN_RELEASED\|Current version\|当前版本\|目前版本" __init__.py README.md README.zh-CN.md README.zh-TW.md
```

## After version bump

- Do **not** commit/push unless the user also ran `/push` or asked to commit.
- Do **not** package unless the user also ran `/pack` or asked to package.
- Summarize what changed and the new version.

## Never

- Update only the string and forget `PLUGIN_VERSION_TUPLE` (Calibre reads the tuple)
- Leave README “current version” lines on an old number
