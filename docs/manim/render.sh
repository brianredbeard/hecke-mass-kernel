#!/bin/sh
# Render both films, or pass one scene filename without its extension.
# Run from the repository root. Needs Manim in .venv, LaTeX, and ffmpeg.
set -eu

manim=${MANIM:-.venv/bin/manim}
media=build/manim

render() {
  file=$1
  scene=$2
  release="$media/release/$file"
  mkdir -p "$release"
  prefix="$release/$file"
  EXPLAINER_EXPORT_PREFIX="$prefix" "$manim" render -r 1920,1080 --fps 30 --format mp4 --media_dir "$media" \
    --disable_caching -v WARNING --progress_bar none \
    "docs/manim/$file.py" "$scene"
  master="$media/videos/$file/1080p30/$scene.mp4"
  # H.264 with yuv420p plays everywhere; faststart lets browsers begin before the download ends.
  # Captions are burned into the frames; WebVTT and Markdown transcripts live alongside the MP4.
  ffmpeg -v error -y -i "$master" -map 0:v:0 -an \
    -c:v libx264 -preset veryslow -crf 24 -tune animation -pix_fmt yuv420p \
    -movflags +faststart "$prefix.mp4"
  ffmpeg -v error -y -ss "$(cat "$prefix.poster-time")" -i "$master" -frames:v 1 "$prefix.png"
  cp "$prefix.png" "$prefix.vtt" "$prefix.md" docs/manim/
}

case "${1:-all}" in
  all)
    render what_the_kernel_computes WhatTheKernelComputes
    render where_the_proof_uses_it WhereTheProofUsesIt ;;
  what_the_kernel_computes) render "$1" WhatTheKernelComputes ;;
  where_the_proof_uses_it) render "$1" WhereTheProofUsesIt ;;
  *) echo "Usage: $0 [what_the_kernel_computes|where_the_proof_uses_it]" >&2; exit 2 ;;
esac
