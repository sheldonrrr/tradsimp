# /push — Save progress and push to remote

Commit the current worktree progress with a **readable English** commit message, then push to the tracked remote branch (usually `main` → `origin/main`).

## Steps (do all of them)

1. Run in parallel:
   - `git status`
   - `git diff` and `git diff --staged`
   - `git log -5 --oneline` (match recent style, but prefer readable English)
   - `git branch -vv` (confirm upstream, e.g. `main` tracking `origin/main`)
2. Stage relevant changes (`git add` for intended files). **Never** stage secrets (`.env`, credentials, API keys).
3. Draft a commit message that is:
   - **English**
   - **Readable** with connecting words (e.g. “Add … after …”, “Fix … when …”, “Update … for …”)
   - 1–2 short sentences focusing on **why**, not a file dump
   - Examples:
     - `Add bilingual annotation with converted text on the primary line.`
     - `Fix nested bilingual markup when re-converting the same book.`
     - `Update OpenCC dictionaries for regional phrase coverage.`
4. Commit with a HEREDOC (see user git rules). Do **not** amend unless the user asked and amend rules are satisfied.
5. Push to the remote tracking branch:
   - Default expectation: current branch is `main` → `git push -u origin HEAD` (or `git push` when upstream exists)
   - **Never** `--force` / `--force-with-lease` unless the user explicitly asks
6. Report: commit subject, branch, remote result (and PR URL only if one was requested).

## Stop and ask if

- There are no changes to commit
- The branch is not `main` and the user did not say which remote branch to use
- Push would require force, or conflicts with remote
- Only secret/credential files are present

## Do not

- Update git config
- Skip hooks
- Push unrelated untracked junk (build zips under `dist/`, `__pycache__`, `.env`)
