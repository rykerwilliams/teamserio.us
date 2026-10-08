#!/usr/bin/env bash
#
# prep-images.sh — three-way image prep for the GitHub Pages migration.
#
# Published GitHub Pages sites are capped at 1 GB. This sorts every image into
# one of three buckets:
#
#   EXEMPT   decklist photos (deck-*), post headers/splash images, site logos
#            and avatars. Left untouched — these are read, zoomed or shown
#            full-width, so resolution matters more than bytes.
#   ARCHIVE  DSLR shots (DSC_*). The full-resolution original is copied to
#            assets/originals/ (excluded from the Jekyll build, so it costs
#            nothing against the 1 GB cap) and then the published copy is
#            resized. Originals stay downloadable via jsDelivr.
#   RESIZE   everything else. Capped at --max px on the long edge.
#
# Dry run by default; nothing is written without --apply.
#
# Usage:
#   script/prep-images.sh                          # dry run, whole library
#   script/prep-images.sh --path assets/images/2025/08/16/KSI2
#   script/prep-images.sh --path <dir> --apply
#   script/prep-images.sh --apply --max 2048 --quality 82
#
# Re-running is safe: files already within the cap are skipped, and an original
# that is already archived is never overwritten.

# NB: deliberately NOT `set -e`. This walks hundreds of files; one unreadable
# image must not abort the batch. Failures are counted and reported per file.
set -uo pipefail

MAX=2560
QUALITY=85
# Some files in this library have malformed JFIF headers (e.g. negative density)
# that make ImageMagick spin indefinitely. Hard-cap every invocation.
IDENTIFY_TIMEOUT=15
CONVERT_TIMEOUT=90
IM_LIMITS=(-limit memory 512MiB -limit map 1GiB -limit time 60)
SCOPE="assets/images"
ORIGINALS="assets/originals"
APPLY=0
USE_DOCKER=1
IMAGE="teamserio-imageprep:v2"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply)     APPLY=1; shift ;;
    --path)      SCOPE="${2%/}"; shift 2 ;;
    --max)       MAX="$2"; shift 2 ;;
    --quality)   QUALITY="$2"; shift 2 ;;
    --no-docker) USE_DOCKER=0; shift ;;
    -h|--help)   sed -n '2,30p' "$0" | sed 's/^# \?//'; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

# Run from the repo root. git may be absent inside the container, where the
# working directory is already the mounted repo.
if command -v git >/dev/null 2>&1; then
  root="$(git rev-parse --show-toplevel 2>/dev/null || true)"
  [[ -n "$root" ]] && cd "$root"
fi

# ---------------------------------------------------------------- imagemagick
# The project box has no ImageMagick and no passwordless sudo, so fall back to a
# small local container image. --user keeps written files owned by the caller.
if ! command -v identify >/dev/null 2>&1; then
  if [[ $USE_DOCKER -eq 1 ]] && command -v docker >/dev/null 2>&1; then
    if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
      echo "==> ImageMagick not found locally; building $IMAGE (one time)"
      docker build -q -t "$IMAGE" - >/dev/null <<'DOCKERFILE'
FROM debian:bookworm-slim
RUN apt-get update -qq \
 && apt-get install -y -qq --no-install-recommends imagemagick libvips-tools \
 && rm -rf /var/lib/apt/lists/*
DOCKERFILE
    fi
    echo "==> running inside $IMAGE"
    exec docker run --rm \
      --user "$(id -u):$(id -g)" \
      -v "$PWD:/repo" -w /repo \
      "$IMAGE" \
      bash script/prep-images.sh --no-docker --path "$SCOPE" --max "$MAX" \
        --quality "$QUALITY" $([[ $APPLY -eq 1 ]] && echo --apply)
  fi
  echo "ERROR: needs ImageMagick (apt install imagemagick) or Docker." >&2
  exit 1
fi

[[ -d "$SCOPE" ]] || { echo "ERROR: no such path: $SCOPE" >&2; exit 1; }

# ------------------------------------------------------- exempt: header images
# Derived from front matter rather than hardcoded, so new posts are covered
# automatically. Values look like "../assets/images/..." or "./assets/...".
HEADERS="$(mktemp)"; trap 'rm -f "$HEADERS"' EXIT
grep -rhoE '^[[:space:]]*(header_img|og_image|image)[[:space:]]*:[[:space:]]*[^#]+' \
     _posts _pages _config.yml index.md 2>/dev/null \
  | sed -E 's/^[^:]*:[[:space:]]*//; s/^["'"'"']//; s/["'"'"'][[:space:]]*$//' \
  | sed -E 's#^\.\./##; s#^\./##; s#^/##' \
  | sed -E 's/[[:space:]]+$//' \
  | sort -u > "$HEADERS"

is_header() { grep -qxF "$1" "$HEADERS"; }

classify() {                         # $1 = repo-relative path -> bucket name
  local path="$1" base; base="$(basename "$path")"
  shopt -s nocasematch
  if [[ "$base" == deck-* ]];                     then shopt -u nocasematch; echo EXEMPT;  return; fi
  if [[ "$path" == assets/images/site/* ]];       then shopt -u nocasematch; echo EXEMPT;  return; fi
  if [[ "$path" == assets/images/avatars/* ]];    then shopt -u nocasematch; echo EXEMPT;  return; fi
  shopt -u nocasematch
  if is_header "$path";                           then echo EXEMPT;  return; fi
  shopt -s nocasematch
  if [[ "$base" == DSC_* ]];                      then shopt -u nocasematch; echo ARCHIVE; return; fi
  shopt -u nocasematch
  echo RESIZE
}

# Fallback encoder. vipsthumbnail writes its own file, so render to a scratch
# path and move it into place only on success.
vips_resize() {                      # $1 = source, $2 = destination
  command -v vipsthumbnail >/dev/null 2>&1 || return 1
  local out="$2.vips.jpg"
  if timeout "$CONVERT_TIMEOUT" vipsthumbnail "$1" --size "${MAX}x${MAX}" \
       --rotate -o "$out[Q=$QUALITY,strip]" >/dev/null 2>&1 && [[ -s "$out" ]]; then
    mv "$out" "$2"; return 0
  fi
  rm -f "$out"; return 1
}

human() { awk -v b="$1" 'BEGIN{ if(b<1048576) printf "%.0f KB", b/1024; else printf "%.1f MB", b/1048576 }'; }

trap 'echo "  !! unexpected failure at line $LINENO: $BASH_COMMAND" >&2' ERR

n_exempt=0 n_skip=0 n_resize=0 n_archive=0 n_fail=0 n_vips=0
failed_list=()
b_before=0 b_after=0 b_archived=0
shown=0

printf "%s\n" "mode:    $([[ $APPLY -eq 1 ]] && echo APPLY || echo 'DRY RUN (no files written)')"
printf "%s\n" "scope:   $SCOPE"
printf "%s\n" "target:  max ${MAX}px long edge, quality ${QUALITY}, EXIF stripped"
printf "%s\n\n" "headers: $(wc -l < "$HEADERS") path(s) exempted from front matter"

while IFS= read -r -d '' f; do
  size_before=$(stat -c%s "$f")
  bucket="$(classify "$f")"

  if [[ "$bucket" == EXEMPT ]]; then
    n_exempt=$((n_exempt+1)); b_before=$((b_before+size_before)); b_after=$((b_after+size_before))
    continue
  fi

  # cheap dimension read. NB: `identify -format` emits no trailing newline, so
  # piping it into `read` returns EOF(1) and would trip `set -e`.
  dims="$(timeout "$IDENTIFY_TIMEOUT" identify -ping -format '%w %h' "$f[0]" 2>/dev/null || echo '0 0')"
  w="${dims%% *}"; h="${dims##* }"
  if [[ -z "$w" || "$w" == 0 || -z "$h" ]]; then
    echo "  !! SKIPPED (unreadable or timed out, likely a malformed header): ${f#assets/images/}"
    n_fail=$((n_fail+1)); failed_list+=("$f"); continue
  fi
  long=$(( w > h ? w : h ))

  # Nothing to do if it already fits. Checked before archiving, so we never
  # store an "original" that is byte-identical to the published copy.
  if (( long <= MAX )); then
    n_skip=$((n_skip+1)); b_before=$((b_before+size_before)); b_after=$((b_after+size_before))
    continue
  fi

  # Archive the full-resolution original before touching it. Idempotent: an
  # existing archived original is never overwritten, so re-runs cannot clobber
  # a true original with an already-resized copy.
  if [[ "$bucket" == ARCHIVE ]]; then
    dest="$ORIGINALS/${f#assets/images/}"
    if [[ ! -f "$dest" ]]; then
      if [[ $APPLY -eq 1 ]]; then
        mkdir -p "$(dirname "$dest")"
        cp -p "$f" "$dest" || { echo "  !! archive copy failed: $f"; n_fail=$((n_fail+1)); continue; }
      fi
      b_archived=$((b_archived+size_before)); n_archive=$((n_archive+1))
    fi
  fi

  if [[ $APPLY -eq 1 ]]; then
    tmp="$(dirname "$f")/.prep-$$-$(basename "$f")"
    # -auto-orient BEFORE -strip, or EXIF rotation is lost
    if timeout "$CONVERT_TIMEOUT" convert "${IM_LIMITS[@]}" "$f[0]" -auto-orient \
         -resize "${MAX}x${MAX}>" -strip -interlace Plane -quality "$QUALITY" "$tmp" \
         2>/dev/null && [[ -s "$tmp" ]]; then
      mv "$tmp" "$f"
      size_after=$(stat -c%s "$f")
    elif vips_resize "$f" "$tmp"; then
      # ImageMagick chokes on some malformed JPEGs (e.g. a JFIF density of
      # 65000 dots/cm) where it either spins past its time limit or aborts on
      # an assertion. libvips reads the same files in about a second.
      mv "$tmp" "$f"
      size_after=$(stat -c%s "$f")
      echo "  (recovered via libvips: ${f#assets/images/})"
      n_vips=$((n_vips+1))
    else
      rm -f "$tmp"
      echo "  !! SKIPPED (both ImageMagick and libvips failed, left untouched): ${f#assets/images/}"
      n_fail=$((n_fail+1)); failed_list+=("$f"); size_after=$size_before
      b_before=$((b_before+size_before)); b_after=$((b_after+size_before)); continue
    fi
  else
    # dry run: measure into a temp file so the projection is real, not guessed
    tmp="$(mktemp --suffix=".$(basename "$f" | sed 's/.*\.//')")"
    if timeout "$CONVERT_TIMEOUT" convert "${IM_LIMITS[@]}" "$f[0]" -auto-orient \
         -resize "${MAX}x${MAX}>" -strip -interlace Plane -quality "$QUALITY" "$tmp" \
         2>/dev/null && [[ -s "$tmp" ]]; then
      size_after=$(stat -c%s "$tmp")
    elif vips_resize "$f" "$tmp"; then
      size_after=$(stat -c%s "$tmp"); n_vips=$((n_vips+1))
      echo "  (would recover via libvips: ${f#assets/images/})"
    else
      echo "  !! SKIPPED (both ImageMagick and libvips failed, would be left untouched): ${f#assets/images/}"
      size_after=$size_before; n_fail=$((n_fail+1)); failed_list+=("$f")
      rm -f "$tmp"
      b_before=$((b_before+size_before)); b_after=$((b_after+size_before)); continue
    fi
    rm -f "$tmp"
  fi

  n_resize=$((n_resize+1))
  b_before=$((b_before+size_before)); b_after=$((b_after+size_after))

  if (( shown < 12 )); then
    printf "  %-7s %5dpx  %9s -> %9s  %s\n" \
      "$bucket" "$long" "$(human $size_before)" "$(human $size_after)" "${f#assets/images/}"
    shown=$((shown+1))
  fi
done < <(find "$SCOPE" -type f \
           \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \) -print0 | sort -z)

(( n_resize > 12 )) && printf "  ... and %d more\n" $((n_resize - 12))

echo
echo "------------------------------------------------------------"
printf "exempt (untouched)      %4d\n" "$n_exempt"
printf "already within cap      %4d\n" "$n_skip"
printf "resized                 %4d\n" "$n_resize"
printf "originals archived      %4d  (%s -> %s)\n" "$n_archive" "$(human $b_archived)" "$ORIGINALS"
(( n_vips > 0 )) && printf "recovered via libvips   %4d\n" "$n_vips"
(( n_fail > 0 )) && printf "failed                  %4d\n" "$n_fail"
if (( ${#failed_list[@]} > 0 )); then
  echo
  echo "These files need manual attention (left completely untouched):"
  for ff in "${failed_list[@]}"; do echo "  - $ff"; done
  echo "  Likely a malformed JPEG header. Try re-exporting, or:"
  echo "    convert broken.jpg -strip fixed.jpg"
fi
echo "------------------------------------------------------------"
printf "published bytes   %10s -> %10s" "$(human $b_before)" "$(human $b_after)"
if (( b_before > 0 )); then
  awk -v b="$b_before" -v a="$b_after" 'BEGIN{ printf "   (%.1f%% smaller)\n", 100-(a*100/b) }'
else echo; fi
[[ $APPLY -eq 0 ]] && echo && echo "Dry run — nothing written. Re-run with --apply to commit these changes to disk."
exit 0
