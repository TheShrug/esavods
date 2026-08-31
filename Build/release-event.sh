#!/usr/bin/env bash
# `make release EVENT=<manifest>` — take one recovered ESA event from the
# vod-timer's output to rows in the local database.
#
# Local and production run the SAME path: export, stage into storage/app/csv,
# import, verify. That matters because a CSV that looks right has proved
# nothing. Between the file and the site sit a time parser, a run matcher and
# an event lookup, and each of the three can be wrong while the CSV reads
# perfectly — a mistyped event name imports cleanly and creates a second event,
# a missing Scheduled column imports cleanly and folds two runs into one.
# The only check worth having is what ends up in the table.
#
# Nothing here is destructive: the importer only inserts and updates. It is
# still slow — it re-reads every CSV in storage/app/csv, not just the new one —
# so --dry-run stops after the export and leaves the CSVs for inspection.
set -euo pipefail

COMPOSE="${COMPOSE:-docker compose}"
APP_SERVICE="${APP_SERVICE:-app}"
DB_SERVICE="${DB_SERVICE:-db}"
IMAGE="${IMAGE:-esavods/vod-timer:latest}"

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
out_dir="$repo/tools/vod-timer/out"
dry_run=0
manifest=""

usage() {
  echo "usage: Build/release-event.sh <manifest> [--dry-run]" >&2
  echo "       manifests live in tools/vod-timer/events/" >&2
  exit 1
}

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) dry_run=1 ;;
    -h|--help) usage ;;
    -*) echo "error: unknown option $1" >&2; usage ;;
    *)  [ -z "$manifest" ] || usage; manifest="$1" ;;
  esac
  shift
done
[ -n "$manifest" ] || usage
[ -f "$manifest" ] || { echo "error: no manifest at $manifest" >&2; exit 1; }

EVENT=""; ISSUE=""; SCHEDULES=""; ANSWERS=""; INDEX=""
# shellcheck disable=SC1090
. "$manifest"
[ -n "$SCHEDULES" ] || { echo "error: $manifest sets no SCHEDULES" >&2; exit 1; }
INDEX="${INDEX:-review-index.csv}"

# `|| true` is load-bearing: grep exits non-zero on a missing .env or a missing
# key, pipefail promotes that to the assignment's status, and set -e then kills
# the script before it has said a word about why.
env_get() { { grep -E "^$1=" "$repo/.env" 2>/dev/null || true; } | head -1 | cut -d= -f2- | tr -d "\"'\r"; }
DB_NAME="${DB_NAME:-$(env_get DB_DATABASE)}"; DB_NAME="${DB_NAME:-esavods}"
DB_USER="${DB_USER:-$(env_get DB_USERNAME)}"; DB_USER="${DB_USER:-esavods}"

# Docker on Git Bash wants a Windows path in -v, and wants MSYS to keep its
# hands off the container-side half of the mount.
hostpath() { if command -v cygpath >/dev/null 2>&1; then cygpath -w "$1"; else printf '%s' "$1"; fi; }
vodtimer() {
  MSYS_NO_PATHCONV=1 docker run --rm -v "$(hostpath "$out_dir")":/out "$IMAGE" "$@"
}

# A name the filesystem and the CSV directory can both live with:
# "ESA 2026 Winter (One)" -> esa-2026-winter-one
slugify() {
  printf '%s' "$1" | tr '[:upper:]' '[:lower:]' \
    | sed -e 's/[^a-z0-9]\{1,\}/-/g' -e 's/^-//' -e 's/-$//'
}

echo "==> ${EVENT:-release}${ISSUE:+  (issue #$ISSUE)}"
echo

# ---------------------------------------------------------------- preflight

command -v docker >/dev/null || { echo "error: docker is not on PATH" >&2; exit 1; }

# The pre-#55 importer keyed a run on game+category+event+TIME. This workflow
# ships OCR readings and corrects them later, and under that key a correction is
# not a fix — it inserts a second run and leaves the wrong one on the site.
# Releasing from a branch that predates the fix would quietly double the event,
# so refuse now rather than explain it afterwards.
#
# Match on $runKey, the array #55 introduced. Not on "run_date" — the old
# importer assigns $run->run_date too, a paragraph below the lookup that
# ignores it, so that grep passes on exactly the version it is meant to catch.
importer="$repo/app/Console/Commands/ImportCsvs.php"
if ! grep -q 'runKey' "$importer"; then
  echo "error: $importer still keys a run on its time (pre-#55)." >&2
  echo "       Importing here would add a second run for every corrected time" >&2
  echo "       instead of updating the first. Merge master into this branch." >&2
  exit 1
fi

docker image inspect "$IMAGE" >/dev/null 2>&1 || {
  echo "==> building $IMAGE"
  $COMPOSE -f "$repo/tools/vod-timer/docker-compose.yml" build
}

# Fail on a missing input now, not four minutes into the export.
missing=0
while IFS='|' read -r dir name; do
  dir="$(echo "$dir" | xargs)"; [ -n "$dir" ] || continue
  name="$(echo "$name" | xargs)"
  [ -n "$name" ] || { echo "error: schedule '$dir' has no event name" >&2; missing=1; }
  for f in results.csv resolved.csv; do
    [ -f "$out_dir/$dir/$f" ] || { echo "error: no $out_dir/$dir/$f" >&2; missing=1; }
  done
done <<EOF
$SCHEDULES
EOF
[ "$missing" -eq 0 ] || exit 1

answers=""
if [ -n "$ANSWERS" ] && [ -f "$out_dir/$ANSWERS" ] && [ -f "$out_dir/$INDEX" ]; then
  answers="$ANSWERS"
  echo "==> human answers: $(grep -cE '^[0-9]' "$out_dir/$answers" || true) in $ANSWERS"
else
  echo "==> no human answers yet — shipping the OCR's own reading of every run"
fi

# ------------------------------------------------- assemble and export CSVs

rel="$out_dir/release"
rm -rf "$rel"; mkdir -p "$rel"

# An array, not a string: event names contain spaces, and a space-separated
# list of "dir|name|slug" word-splits straight through the middle of one.
specs=()
while IFS='|' read -r dir name; do
  dir="$(echo "$dir" | xargs)"; [ -n "$dir" ] || continue
  name="$(echo "$name" | xargs)"
  slug="$(slugify "$name")"
  echo
  echo "==> $name  <- out/$dir"

  final="$dir/final.csv"
  if [ -n "$answers" ]; then
    # apply matches on video_id, so an answer for the other schedule simply
    # finds no row here. Running the whole answers file against each schedule
    # is therefore correct, and saves splitting a list the reviewer sees as one.
    vodtimer apply "/out/$dir/results.csv" --index "/out/$INDEX" \
      --answers "/out/$answers" --out "/out/$final"
  else
    cp "$out_dir/$dir/results.csv" "$out_dir/$final"
  fi

  vodtimer export "/out/$final" --resolved "/out/$dir/resolved.csv" \
    --event-name "$name" --out "/out/release/$slug.csv"
  specs+=("$dir|$name|$slug")
done <<EOF
$SCHEDULES
EOF

# ------------------------------------------------------------------ report
#
# What is about to be published, by how much the tool trusts it — and the list
# of runs going out on a reading nobody has confirmed, which is the thing that
# makes shipping a guess safe rather than merely fast.

echo
MSYS_NO_PATHCONV=1 docker run --rm -i --entrypoint python \
  -v "$(hostpath "$out_dir")":/out "$IMAGE" - "$EVENT" "${specs[@]}" <<'PY'
import csv, sys

def rows(path):
    with open(path, encoding="utf8") as fh:
        return list(csv.DictReader(fh))

event, specs = sys.argv[1], sys.argv[2:]
unvouched, totals, impossible = [], {}, []

for spec in specs:
    d, name, slug = spec.split("|")
    meta = {r["video_id"]: r for r in rows(f"/out/{d}/resolved.csv") if r.get("video_id")}
    with open(f"/out/release/{slug}.csv", encoding="utf8") as fh:
        shipped = {r["Youtube"] for r in csv.DictReader(fh, delimiter=";") if r.get("Youtube")}

    tiers = {}
    for r in rows(f"/out/{d}/final.csv"):
        vid = r.get("video_id", "")
        conf = (r.get("confidence") or "").strip() or "unread"
        if vid not in shipped:
            conf = "NOT SHIPPED (no time)"
        tiers[conf] = tiers.get(conf, 0) + 1
        # An OCR read longer than the video it came from is the real form of
        # "that time is impossible" — an absolute ceiling is not, because ESA
        # runs six-hour games and a long run is not a wrong one. `batch` rejects
        # these already, so one arriving here means a hand-edited CSV.
        #
        # A human answer is exempt, for the reason cmd_export is: ESA splits a
        # long run over several VODs and the timer shows the cumulative total,
        # so Skies of Arcadia 100% Part 5/6 really does read 20:30:31 inside a
        # four-hour video. Failing the release over a time a person read off the
        # screen would make the reviewer's answer unshippable.
        if vid in shipped and (r.get("source") or "ocr") == "ocr":
            dur = float(r.get("duration") or 0)
            secs = float(r.get("final_seconds") or 0)
            if dur and secs > dur:
                impossible.append((name, r.get("game", ""), r.get("final_time", ""), dur, vid))

        # high measured at 99% against ground truth, and human is a person's
        # own eyes. Everything else goes on the list to be corrected later.
        if vid in shipped and conf not in ("high", "human"):
            m = meta.get(vid, {})
            unvouched.append((name, m.get("game") or r.get("game", ""),
                              m.get("category", ""), r.get("final_time", ""), conf, vid))
    totals[name] = (len(shipped), tiers)

print("==> what this release publishes")
for name, (n, tiers) in totals.items():
    print(f"\n    {name}: {n} run(s)")
    for conf, count in sorted(tiers.items(), key=lambda kv: -kv[1]):
        print(f"      {count:>4}  {conf}")

if unvouched:
    with open("/out/release/unvouched.md", "w", encoding="utf8") as fh:
        fh.write(f"## {event} — runs shipped on an unconfirmed time\n\n")
        fh.write("Every run below is live with the time the OCR read. None reached "
                 "the `high` tier and none has been checked by a person, so each is "
                 "a candidate for correction. Re-importing a corrected time updates "
                 "the run in place (#55), so a fix is a CSV edit and a re-import, "
                 "not a delete.\n\n")
        for name, game, cat, t, conf, vid in unvouched:
            fh.write(f"- **{game}** — {cat} ({name}) — shipped `{t}` "
                     f"({conf}) — https://youtu.be/{vid}\n")
    print(f"\n==> {len(unvouched)} run(s) ship on an unconfirmed time")
    print("    listed in out/release/unvouched.md — post it on the event's issue")

if impossible:
    print("\n!! these times are longer than the video they came from:", file=sys.stderr)
    for name, game, t, dur, vid in impossible:
        h = f"{int(dur)//3600}:{int(dur)%3600//60:02d}:{int(dur)%60:02d}"
        print(f"   {game} ({name}) — {t} out of a {h} video — "
              f"https://youtu.be/{vid}", file=sys.stderr)
    sys.exit(1)
PY

if [ "$dry_run" -eq 1 ]; then
  echo
  echo "==> --dry-run: stopping before the import"
  echo "    CSVs are in tools/vod-timer/out/release/ — nothing was staged"
  exit 0
fi

# --------------------------------------------------------- stage and import

$COMPOSE ps --services --filter status=running 2>/dev/null | grep -qx "$APP_SERVICE" || {
  echo "error: the '$APP_SERVICE' service is not running in this checkout." >&2
  echo "       start it with 'make run' from $repo" >&2
  exit 1
}

echo
echo "==> staging into storage/app/csv/"
for f in "$rel"/*.csv; do
  cp "$f" "$repo/storage/app/csv/"
  echo "    $(basename "$f")  $(( $(wc -l < "$f") - 1 )) run(s)"
done

echo
echo "==> importing (reads every CSV in storage/app/csv, so this takes a while)"
$COMPOSE exec -T "$APP_SERVICE" php artisan runCsv:import >/dev/null
echo "    done"

# ---------------------------------------------------------------- verify
#
# The import exits 0 whether or not the rows are sane, so ask the table.

psql_() { $COMPOSE exec -T "$DB_SERVICE" psql -U "$DB_USER" -d "$DB_NAME" "$@"; }

names=""
while IFS='|' read -r _ name; do
  name="$(echo "$name" | xargs)"; [ -n "$name" ] || continue
  names="$names${names:+, }'$(printf '%s' "$name" | sed "s/'/''/g")'"
done <<EOF
$SCHEDULES
EOF

echo
echo "==> in the database"
psql_ -c "select e.name, count(*) as runs, min(r.time) as min, max(r.time) as max,
                 count(*) filter (where r.youtube_vod_id is null) as no_vod
          from runs r join events e on e.id = r.event_id
          where e.name in ($names) group by e.name order by e.name;"

# A time of 0 is always a parse failure — the importer splits on ':' and sums
# whatever it got, so a malformed cell imports perfectly happily as nothing.
bad="$(psql_ -tAc "select count(*) from runs r join events e on e.id = r.event_id
                   where e.name in ($names) and r.time <= 0;" | tr -d ' \r')"
if [ "${bad:-0}" -gt 0 ]; then
  echo
  echo "!! $bad run(s) imported with no time — fix the CSV and re-import." >&2
  echo "   Do not patch the database; the CSV is the artifact of record." >&2
  psql_ -c "select e.name, g.name, r.category, r.time, r.youtube_vod_id
            from runs r join events e on e.id = r.event_id join games g on g.id = r.game_id
            where e.name in ($names) and r.time <= 0;"
  exit 1
fi

# Deliberately a warning, not a failure. An earlier version failed anything over
# six hours, which broke on Ghost of Yotei — a real 6:07:44 run, inside a 6:14:59
# video, agreed on by both confirmations. Long is not wrong, and the check that
# a time is impossible belongs upstream where the VOD's own length is known.
long="$(psql_ -tAc "select count(*) from runs r join events e on e.id = r.event_id
                    where e.name in ($names) and r.time > 28800;" | tr -d ' \r')"
[ "${long:-0}" -eq 0 ] || echo "!! $long run(s) are over eight hours — worth a glance" >&2

# Two runs on one VOD means the resolver matched the same video twice, and at
# least one of those two times belongs to the other run.
dupes="$(psql_ -tAc "select count(*) from (select r.youtube_vod_id from runs r
                      join events e on e.id = r.event_id
                      where e.name in ($names) and r.youtube_vod_id is not null
                      group by r.youtube_vod_id having count(*) > 1) d;" | tr -d ' \r')"
[ "${dupes:-0}" -eq 0 ] || echo "!! $dupes VOD(s) are used by more than one run — check the resolve step" >&2

echo
echo "==> released locally. Commit the CSVs in storage/app/csv/ on this branch."
echo "    Merging the PR deploys, and the container's entrypoint runs"
echo "    'php artisan runCsv:import' itself on boot (#43), so production"
echo "    needs no manual step."
