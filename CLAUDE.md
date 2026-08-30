# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this
repository.

esavods.com — a Laravel 12 app (PHP `^8.3`) deployed to production via Coolify, on push to
`master`.

## Local dev interface

`make` is the interface, and it lives **inside the devcontainer** — PHP and `make` are neither of
them on the Windows host. The fleet-wide table and reasoning live in the `homelab` vault at
`Conventions/Local Dev Interface.md`; restated here because that vault is private.

| | |
| --- | --- |
| `make` | List the targets. `.DEFAULT_GOAL := help` |
| `make build` | Build the dev image |
| `make test` | The suite, against a throwaway Postgres — see the warning below |
| `make run` | Serve on **8001**, Postgres on **55401**, URL printed last |
| `make database download restore migrate` | Newest R2 dump → local database → schema forward |

**Ports 8001 / 55401 are assigned, not defaulted.** `PORT=` and **`DB_HOST_PORT=`** override. This
repo moved off 8080, and its Postgres off 5432 — which speedrunwr also publishes, so they could not
previously run at the same time.

`DB_HOST_PORT`, not `DB_PORT`: compose substitutes from this repo's `.env`, where Laravel's
`DB_PORT=5432` is the *internal* connection port.

> [!CAUTION]
> **Never run the suite through the `app` service.** `docker compose run app php artisan test` can
> wipe a real database. `env_file: .env` puts `DB_*` into the container's real OS environment;
> Laravel's `env()` reads `$_SERVER` while PHPUnit's `<env name="DB_CONNECTION" value="sqlite"/>`
> only sets `$_ENV`/`putenv()`, so `phpunit.xml` never wins — `force="true"` included. That is #22.
>
> `make test` uses the separate `test` service: no `env_file`, an explicit environment block, and a
> **tmpfs** `test-db`. It also logs to stderr, because it runs as root over the shared bind mount
> and a file log leaves a root-owned `storage/logs/laravel.log` that php-fpm cannot write —
> `make run` then 500s and the cause is nowhere near the symptom.

`make database download` reads the nightly backup from R2, not a live `pg_dump` over SSH. It wants
the **read-only** fleet R2 token at `~/.config/homelab/backups.env` — not this repo's `.env`.
`backups/` is gitignored: those dumps are production data.

The postgres client is pinned to **`postgresql16-client`**, matching the server. `pg_restore`
rebuilds the dump's SQL preamble from the *client's* version, so a floating 18.x client emits
`SET transaction_timeout` that the 16.x server rejects.

## Work queue

Work lives in this repo's **GitHub Issues**, one issue per item, with exactly one `type:` label
— `feat` (epic), `tckt` (atomic unit of work), `bug`, `chore`, `spike` (time-boxed
investigation whose output is knowledge). Status is the issue's own state: open with no
`status:` label is queued, `status: active` / `status: blocked` say the rest, `done` is closed as
*completed*, `dropped` is closed as *not planned*. The body follows the `## Goal` /
`## Acceptance criteria` / `## Notes` convention; this repo has no issue template, so nothing
scaffolds that shape — it is convention only.

## Branches and pull requests

Two levels:

- **`master` is production *and* the integration branch**, and the base for everything. Nothing
  is committed to it directly — `.github/workflows/deploy.yml` runs on every push to `master`,
  so merging the PR *is* the release. (Docs- and markdown-only commits are `paths-ignore`d and
  do not trigger a rebuild.)
- **A working branch per issue**, cut from `master` and merged back through a pull request.
  `.github/workflows/ci.yml` runs `artisan test` against a throwaway Postgres 16 service on
  every non-`master` branch, on pull requests, and on manual dispatch, so the PR is where a
  failure gets caught before it can reach the live site.

**The gate is thinner than it looks.** `ci.yml` runs `artisan test`, but `tests/` is still the
stock Laravel `ExampleTest` stubs — there is no real suite yet. So "CI is green" currently means
"the app boots, migrates, and a stub assertion passed," not "the change is safe." It will catch
a boot failure, a syntax error, a broken migration — it will not catch a logic bug. Because
trunk-based means merging the PR *is* the release, with no staging beat in between, that gap
matters: don't read a green check as more assurance than it gives.

Name the branch:

```
TheShrug/<issue>-<type>-<slug>
```

```
^TheShrug/[0-9]+-(tckt|feat|bug|chore|spike)-[a-z0-9]+(-[a-z0-9]+)*$
```

- `<issue>` is the **issue number in this repo** — not a PR number. A PR number doesn't exist
  yet when the branch is cut, and renaming a branch after opening the PR detaches it from its
  head.
- `<type>` matches the issue's one `type:` label.
- `<slug>` is lowercase `a-z0-9-`; `.` and `_` collapse to `-`; aim for ≤ 40 characters. The issue
  holds the full title, so this is a handle, not a summary.

So issue #12 `type: tckt` "Fix the footer year" becomes `TheShrug/12-tckt-fix-footer-year`.

**No issue, no branch** — the number is mandatory, so every branch traces back to the queue.
This replaces the old `chore/<slug>` / `feat/<slug>` convention and, deliberately, the "or
whatever an agent's worktree already gave you" escape hatch: a tool that names a branch from a
task description is a branch that has lost its link to the queue.

Branches are grandfathered **by date, not by a list** — the policy was adopted 2026-08-16, and a
branch whose last commit predates that could not have complied. Never rename a branch that
already has an open PR. **Reference the issue number in the PR title too**, so the two link up
even for grandfathered branches.

Five branches in this repo predate the policy — all Dependabot's own `dependabot/...` names.
Leave them exactly as they are: they're grandfathered by date, and Dependabot doesn't read this
file, so it will keep opening branches in its own format regardless. That's expected, not drift.

**Cut from `origin/master`, and fetch first.** A branch cut from a stale local `master` starts
life missing merged work and will conflict with it later. The stale base also lies to you at
close-out: `git branch -d` compares against whatever `master` currently is, so a genuinely
merged branch refuses to delete and looks unmerged. Fast-forward the base rather than reaching
for `-D`, which skips the check entirely and would delete an unmerged branch just as happily:

```sh
git checkout master && git merge --ff-only origin/master
git branch -d <branch>          # now succeeds, and still checks
```

The fleet-wide policy and its reasoning live in the `homelab` vault at
`Conventions/Branching.md`. It's restated here rather than linked because that vault is private
and this repo is public.
