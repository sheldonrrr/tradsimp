# /push — Commit all local work, then push

When this command is triggered (slash `/push`, Git/diff-tab **Push**, or the same intent in chat), the **default** is:

**Commit every current worktree change that belongs in the repo, then push to the tracked remote** (usually `main` → `origin/main`).

Do **not** treat “push existing commits only” / “do not create new commits” as the default in this project. If there are uncommitted or untracked files, stage, commit, and push them in the same run.

## Steps (do all of them)

1. Run in parallel:
   - `git status`
   - `git diff` and `git diff --staged`
   - `git log -5 --oneline` (match recent style, but prefer readable English)
   - `git branch -vv` (confirm upstream, e.g. `main` tracking `origin/main`)
2. Stage **all** intended project files (`git add -A` scoped to the repo, or add the listed paths). Include new files that are part of the work.
   - **Never** stage secrets (`.env`, credentials, API keys)
   - **Never** stage: `dist/`, `__pycache__/`, `*.pyc`, editor junk
3. If there is nothing to commit and the branch is already in sync with the remote, say so and stop.
4. If there are changes, draft a commit message that is:
   - **English**
   - **Readable** with connecting words (e.g. “Add … after …”, “Fix … when …”, “Update … for …”)
   - 1–2 short sentences focusing on **why**, not a file dump
   - Examples:
     - `Add bilingual annotation with converted text on the primary line.`
     - `Fix nested bilingual markup when re-converting the same book.`
     - `Update OpenCC dictionaries for regional phrase coverage.`
5. Commit with a HEREDOC (see user git rules). Do **not** amend unless the user asked and amend rules are satisfied.
6. Push to the remote tracking branch:
   - Default: current branch is `main` → `git push` (or `git push -u origin HEAD` if upstream is missing)
   - **Never** `--force` / `--force-with-lease` unless the user explicitly asks
7. Report: commit subject, branch, remote result (and PR URL only if one was requested).

## Stop and ask if

- The branch is not `main` and the user did not say which remote branch to use
- Push would require force, or conflicts with remote
- Only secret/credential files are present

## Do not

- Update git config
- Skip hooks
- Leave uncommitted project work behind after a successful `/push`
- Push unrelated untracked junk (build zips under `dist/`, `__pycache__`, `.env`)
