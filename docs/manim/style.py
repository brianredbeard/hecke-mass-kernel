"""Shared palette, text helpers and narration scaffold for the documentation animations."""

import os
from html import escape
from pathlib import Path

from manim import (
    DOWN,
    LEFT,
    UP,
    FadeIn,
    FadeOut,
    MathTex,
    RegularPolygon,
    RoundedRectangle,
    Scene,
    Square,
    Text,
    VGroup,
)

BG = "#0d1117"
PANEL = "#161b22"
AMBER = "#f5a623"
BLUE = "#4aa8ff"
INK = "#e6edf3"
DIM = "#7d8590"
GLOW = "#7ee787"
WARN = "#ff7b72"
CURVE = "#c297ff"

SUBTITLE_Y = -3.12
SECONDS_PER_WORD = 0.3


def lines(
    text: str, size: float = 26, color: str = INK, buff: float = 0.16, **kwargs
) -> VGroup:
    """Centered multi-line text, one `Text` per line."""
    return VGroup(
        *[
            Text(line, font_size=size, color=color, **kwargs)
            for line in text.split("\n")
        ]
    ).arrange(DOWN, buff=buff)


def mono(text: str, size: float = 16, color: str = INK) -> Text:
    return Text(text, font="monospace", font_size=size, color=color)


def code_card(text: str, size: float = 18, color: str = INK) -> VGroup:
    """A line of code on a panel, as it would be typed against the library."""
    label = mono(text, size, color)
    box = RoundedRectangle(
        width=label.width + 0.5,
        height=label.height + 0.36,
        corner_radius=0.1,
        stroke_color=DIM,
        stroke_width=1.5,
        fill_color=PANEL,
        fill_opacity=1,
    )
    return VGroup(box, label)


HANDOFF_MASS = "class_mass([4, 6])  →  5/12"
HANDOFF_HECKE = "hecke(u=1, q=2, k=0, r=2, [0, 1, 1])  →  2"


def handoff_cards() -> tuple[VGroup, VGroup]:
    """The two worked sums, placed identically at the end of part 1 and the start of part 2."""
    mass = code_card(HANDOFF_MASS, 19, AMBER).move_to([-4.2, 1.6, 0])
    hecke = code_card(HANDOFF_HECKE, 18, BLUE).move_to([2.6, 1.6, 0])
    return mass, hecke


def check(size: float = 36) -> MathTex:
    return MathTex(r"\checkmark", font_size=size, color=GLOW)


def grid_icon(letter: str, scale: float = 1.0) -> VGroup:
    """Grid A is drawn as a square (4 turns), grid B as a hexagon (6 turns)."""
    if letter == "A":
        outline = Square(side_length=0.95, color=AMBER, stroke_width=4)
        color = AMBER
    else:
        outline = RegularPolygon(6, radius=0.58, color=BLUE, stroke_width=4)
        color = BLUE
    outline.set_fill(color, opacity=0.18)
    return VGroup(
        outline, Text(letter, font_size=30, color=color, weight="BOLD")
    ).scale(scale)


class Explainer(Scene):
    """A scene with a chapter heading and a subtitle line that paces itself."""

    subtitle_size = 26

    def setup(self):
        self.camera.background_color = BG
        self.subtitle = None
        self.heading = None
        self._said_at = 0.0
        self._reading_time = 0.0
        self._chapter_title = "Opening"
        self._cues = []
        self._poster_time = None

    def mark_poster(self):
        """Pick a fully composed frame for the README thumbnail."""
        self._poster_time = self.time

    def chapter(self, text: str):
        """Replace the small heading in the top-left corner."""
        self._chapter_title = text
        new = Text(text, font_size=20, color=DIM).to_corner(UP + LEFT, buff=0.3)
        animations = [FadeIn(new)]
        if self.heading is not None:
            animations.append(FadeOut(self.heading))
        self.heading = new
        return animations

    def say(self, text: str, *animations, run_time: float = 0.7):
        """Swap the subtitle, optionally alongside other animations."""
        new = lines(text, self.subtitle_size)
        if new.width > 13.4:
            new.scale_to_fit_width(13.4)
        new.move_to([0, SUBTITLE_Y, 0])
        if self.subtitle is not None:
            # Clear the old line first so two captions never overlap.
            self.play(FadeOut(self.subtitle), run_time=0.2)
        self.subtitle = new
        self._cues.append((self.time, self._chapter_title, text))
        self.play(FadeIn(new, shift=0.1 * UP), *animations, run_time=run_time)
        self._said_at = self.time
        self._reading_time = 0.8 + SECONDS_PER_WORD * len(text.split())

    def tear_down(self):
        """Write playback companions when building a complete release video."""
        export = os.environ.get("EXPLAINER_EXPORT_PREFIX")
        if not export:
            return
        if self._poster_time is None:
            raise ValueError("The scene needs a poster frame")
        prefix = Path(export)
        title = prefix.name.replace("_", " ").capitalize()
        vtt = ["WEBVTT", ""]
        transcript = [f"# {title}", ""]
        chapter = None

        def timestamp(seconds):
            minutes, ms = divmod(round(1000 * seconds), 60_000)
            hours, minutes = divmod(minutes, 60)
            return f"{hours:02}:{minutes:02}:{ms // 1000:02}.{ms % 1000:03}"

        ends = [start for start, _, _ in self._cues[1:]] + [self.time]
        for (start, heading, text), end in zip(self._cues, ends, strict=True):
            vtt.extend([f"{timestamp(start)} --> {timestamp(end)}", escape(text), ""])
            if heading != chapter:
                minute, second = divmod(int(start), 60)
                transcript.extend(
                    [
                        f"## {heading}",
                        "",
                        f"[{minute}:{second:02} in the video]({prefix.name}.mp4#t={start:.3f})",
                        "",
                    ]
                )
                chapter = heading
            transcript.extend([" ".join(text.splitlines()), ""])
        prefix.with_suffix(".vtt").write_text("\n".join(vtt), encoding="utf-8")
        prefix.with_suffix(".md").write_text("\n".join(transcript), encoding="utf-8")
        prefix.with_suffix(".poster-time").write_text(f"{self._poster_time:.3f}\n")

    def read(self, extra: float = 0.0):
        """Wait until the current subtitle has been on screen long enough to read."""
        elapsed = self.time - self._said_at
        self.wait(max(0.3, self._reading_time - elapsed) + extra)

    def clear_stage(self, *keep, run_time: float = 0.6):
        """Fade out everything except the heading, the subtitle and `keep`."""
        protected = {self.subtitle, self.heading, *keep}
        leaving = [mob for mob in self.mobjects if mob not in protected]
        if leaving:
            self.play(*[FadeOut(mob) for mob in leaving], run_time=run_time)
