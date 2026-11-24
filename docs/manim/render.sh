#!/bin/sh
# Render every documentation animation to docs/manim/<name>.mp4 with a poster frame <name>.png.
# Run from the repository root. Needs Manim in .venv, LaTeX, and ffmpeg.
set -eu

manim=${MANIM:-.venv/bin/manim}
media=build/manim

render() {
  file=$1
  scene=$2
  poster_at=$3
  "$manim" render -r 1920,1080 --fps 30 --format mp4 --media_dir "$media" \
    --disable_caching -v WARNING --progress_bar none \
    "docs/manim/$file.py" "$scene"
  master="$media/videos/$file/1080p30/$scene.mp4"
  # H.264 with yuv420p plays everywhere; faststart lets browsers begin before the download ends.
  ffmpeg -v error -y -i "$master" -an \
    -c:v libx264 -preset veryslow -crf 24 -tune animation -pix_fmt yuv420p \
    -movflags +faststart "docs/manim/$file.mp4"
  ffmpeg -v error -y -ss "$poster_at" -i "$master" -frames:v 1 "docs/manim/$file.png"
}

render what_the_kernel_computes WhatTheKernelComputes 110
render where_the_proof_uses_it WhereTheProofUsesIt 45
