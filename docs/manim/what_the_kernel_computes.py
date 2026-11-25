"""Two small sums, one deep connection: what the kernel computes, from zero.

The scenes form one chain, each consuming what the previous one produced:

    symmetry and mass -> weighted balance -> zero-mean pattern
        -> Hecke eigenvalue -> modular form -> point counts

The level-11 data lives in `CLASSES` below. Everything shown on screen (the
mass 5/12, the table (1 2; 3 0), the pattern (2, -3), the eigenvalue -2, the
curve's point counts, the modular form's coefficients and the number of
fixture rows) is computed from that data or from repository files and
asserted at import time.

Render with `sh docs/manim/render.sh` from the repository root.
"""

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import gcd
from pathlib import Path

import numpy as np
from manim import (
    DEGREES,
    DL,
    DOWN,
    DR,
    LEFT,
    RIGHT,
    UL,
    UP,
    UR,
    Arc,
    Arrow,
    Create,
    CurvedArrow,
    Dot,
    FadeIn,
    FadeOut,
    Indicate,
    LaggedStart,
    Line,
    MathTex,
    MoveToTarget,
    Rectangle,
    RoundedRectangle,
    Square,
    SurroundingRectangle,
    Text,
    Transform,
    VGroup,
)
from style import (
    AMBER,
    BG,
    BLUE,
    CURVE,
    DIM,
    GLOW,
    INK,
    PANEL,
    WARN,
    Explainer,
    check,
    code_card,
    grid_icon,
    lines,
    handoff_cards,
    mono,
)

# ------------------------------------------------------------------ the data


@dataclass(frozen=True)
class ArithmeticClass:
    """One class at level 11: its symmetry count and its neighbours at the prime 2."""

    name: str
    symmetry_order: int
    neighbours: tuple[str, ...]

    @property
    def mass(self) -> Fraction:
        return Fraction(1, self.symmetry_order)


CLASSES = (
    ArithmeticClass("A", 4, ("A", "B", "B")),
    ArithmeticClass("B", 6, ("A", "A", "A")),
)
MASS = sum(c.mass for c in CLASSES)
MATRIX = tuple(
    tuple(source.neighbours.count(target.name) for target in CLASSES)
    for source in CLASSES
)
assert MASS == Fraction(5, 12) == Fraction(11 - 1, 24)
assert MATRIX == ((1, 2), (3, 0))
for i, source in enumerate(CLASSES):
    for j, target in enumerate(CLASSES):
        assert source.mass * MATRIX[i][j] == target.mass * MATRIX[j][i]

# The simplest whole-number pattern whose mass-weighted average is zero.
_d_a, _d_b = (c.symmetry_order for c in CLASSES)
MODE = (_d_a // gcd(_d_a, _d_b), -_d_b // gcd(_d_a, _d_b))
MIXED = tuple(sum(a * b for a, b in zip(row, MODE)) for row in MATRIX)
EIGENVALUE = Fraction(MIXED[0], MODE[0])
assert MODE == (2, -3) and MIXED == (-4, 6)
assert sum(c.mass * v for c, v in zip(CLASSES, MODE)) == 0
assert all(y == EIGENVALUE * x for x, y in zip(MODE, MIXED)) and EIGENVALUE == -2


def halving_rule(p: int, a: int, b: int) -> tuple[int, int]:
    """The rule a*x + b*y = 0 mod p, named by its smallest rescaling of (a, b)."""
    return min(((k * a) % p, (k * b) % p) for k in range(1, p))


def halving_rules(p: int) -> list[tuple[int, int]]:
    """The distinct sublattices of index p in the plane, one per rule."""
    pairs = [pair for pair in product(range(p), repeat=2) if pair != (0, 0)]
    return sorted({halving_rule(p, a, b) for a, b in pairs})


# The local model of a neighbour: keep the points (x, y) with a*x + b*y even.
HALVINGS = ((1, 0), (0, 1), (1, 1))
NEIGHBOUR_PRIMES = (2, 3, 5, 7, 13)
assert sorted(HALVINGS) == halving_rules(2)
assert all(len(halving_rules(p)) == p + 1 for p in NEIGHBOUR_PRIMES)
assert all(len(c.neighbours) == 2 + 1 for c in CLASSES)
# Balance a/4 = b/6 with at most three arrows each way and some crossing arrow.
assert [
    (a, b)
    for a in range(1, 4)
    for b in range(1, 4)
    if CLASSES[0].mass * a == CLASSES[1].mass * b
] == [(MATRIX[0][1], MATRIX[1][0])]


def curve_points(p: int) -> int:
    """Points of y^2 + y = x^3 - x^2 - 10x - 20 mod p, with the point at infinity."""
    affine = sum(
        (y * y + y - (x**3 - x * x - 10 * x - 20)) % p == 0
        for x in range(p)
        for y in range(p)
    )
    return affine + 1


def form_coefficients(limit: int) -> list[int]:
    """Coefficients a_1..a_limit of q * prod (1 - q^n)^2 (1 - q^(11n))^2."""
    series = [1] + [0] * limit
    for n in range(1, limit + 1):
        for step in (n, n, 11 * n, 11 * n):
            if step > limit:
                continue
            for k in range(limit, step - 1, -1):
                series[k] -= series[k - step]
    return series[:limit]


PRIMES = (2, 3, 5, 7, 13, 17, 19)
CURVE_GAPS = [p + 1 - curve_points(p) for p in PRIMES]
FORM = form_coefficients(20)
FORM_AT_PRIMES = [FORM[p - 1] for p in PRIMES]
assert CURVE_GAPS == FORM_AT_PRIMES == [-2, -1, 1, -2, 4, -2, 0]
assert FORM[1] == EIGENVALUE

FIXTURES = Path(__file__).resolve().parents[2] / "tests" / "vectors" / "kernel.tsv"
_rows = [line.rstrip("\n") for line in FIXTURES.read_text().splitlines() if line]
FIXTURE_COUNT = len(_rows)
assert "hecke\t2/3 7 0 4 1/2 -2/3\t-1/4" in _rows
assert "mass\t4 6\t5/12" in _rows

EQUATION = (r"y^2+y", "=", r"x^3-x^2-10x-20")

# --------------------------------------------------------------- the drawing


def p2(x: float, y: float) -> np.ndarray:
    return np.array([x, y, 0.0])


def turn(bits: tuple) -> tuple:
    """Rotate a corner marking by a quarter turn."""
    return bits[-1:] + bits[:-1]


def families() -> list[list[tuple]]:
    """The 16 corner markings grouped by quarter turns, most symmetric first."""
    seen, result = set(), []
    for bits in product((0, 1), repeat=4):
        if bits in seen:
            continue
        family, current = [], bits
        while current not in family:
            family.append(current)
            current = turn(current)
        seen.update(family)
        result.append(family)
    return sorted(result, key=lambda family: (len(family), sum(family[0])))


def marking(bits: tuple, size: float = 0.85) -> VGroup:
    """A square with each corner switched on (filled) or off (hollow)."""
    square = Square(side_length=size, color=DIM, stroke_width=2.5)
    dots = VGroup()
    for bit, corner in zip(bits, (UR, UL, DL, DR)):
        dot = Dot(square.get_corner(corner), radius=0.17 * size)
        dot.set_fill(INK if bit else BG, opacity=1)
        dot.set_stroke(INK if bit else DIM, width=2)
        dots.add(dot)
    return VGroup(square, dots)


def chip(letter: str, size: float = 0.5) -> VGroup:
    """A small tile naming the class a neighbour lands on."""
    color = AMBER if letter == "A" else BLUE
    tile = RoundedRectangle(
        width=size,
        height=size,
        corner_radius=0.08,
        stroke_color=color,
        stroke_width=2,
        fill_color=color,
        fill_opacity=0.25,
    )
    return VGroup(tile, Text(letter, font_size=24, color=color, weight="BOLD"))


def panel(title: str, body: str, color: str, width=3.5, height=1.7) -> VGroup:
    """A titled box for the bridge and architecture diagrams."""
    frame = RoundedRectangle(
        width=width,
        height=height,
        corner_radius=0.15,
        stroke_color=color,
        stroke_width=3,
        fill_color=PANEL,
        fill_opacity=1,
    )
    heading = Text(title, font_size=26, color=color, weight="BOLD")
    text = lines(body, 22, INK, buff=0.12)
    content = VGroup(heading, text).arrange(DOWN, buff=0.22).move_to(frame)
    return VGroup(frame, content)


RULE_COLORS = ("#39c5cf", "#f778ba", "#e3b341", "#a5d6a7")


def lattice(
    rule=None, color: str = INK, spacing: float = 0.3, reach: int = 3
) -> VGroup:
    """A window onto the integer grid; points failing `rule` shrink to faint specks."""
    dots = VGroup()
    for x, y in product(range(-reach, reach + 1), repeat=2):
        kept = rule is None or rule(x, y)
        dot = Dot(
            p2(spacing * x, spacing * y),
            radius=0.3 * spacing if kept else 0.1 * spacing,
        )
        dot.set_fill(color if kept else DIM, opacity=1 if kept else 0.6)
        dots.add(dot)
    return dots


def self_loop(node: VGroup, color: str, width: float = 3) -> Arc:
    loop = Arc(
        radius=0.38,
        start_angle=-50 * DEGREES,
        angle=280 * DEGREES,
        color=color,
        stroke_width=width,
    ).move_to(node.get_top() + 0.3 * UP)
    loop.add_tip(tip_length=0.16, tip_width=0.16)
    return loop


def neighbour_graph(scale: float, centre: np.ndarray) -> VGroup:
    """Classes A and B with one arrow per neighbour at the prime 2."""
    node_a = grid_icon("A").move_to(p2(-1.7, 0))
    node_b = grid_icon("B").move_to(p2(1.7, 0))
    loop = self_loop(node_a, AMBER)

    def arrow(start, end, bend, color):
        return CurvedArrow(
            start, end, angle=bend, color=color, stroke_width=3, tip_length=0.16
        )

    a_right = node_a.get_right() + 0.1 * RIGHT
    b_left = node_b.get_left() + 0.1 * LEFT
    from_a = VGroup(
        loop,
        arrow(a_right + 0.25 * UP, b_left + 0.25 * UP, -0.5, AMBER),
        arrow(a_right + 0.4 * UP, b_left + 0.4 * UP, -1.2, AMBER),
    )
    from_b = VGroup(
        arrow(b_left + 0.05 * DOWN, a_right + 0.05 * DOWN, -0.15, BLUE),
        arrow(b_left + 0.25 * DOWN, a_right + 0.25 * DOWN, -0.7, BLUE),
        arrow(b_left + 0.4 * DOWN, a_right + 0.4 * DOWN, -1.3, BLUE),
    )
    return VGroup(node_a, node_b, from_a, from_b).scale(scale).move_to(centre)


class WhatTheKernelComputes(Explainer):
    subtitle_size = 28

    def construct(self):
        self.hook()
        self.fair_counting()
        self.level_eleven_mass()
        self.neighbours_from_lattice()
        self.count_rules()
        self.classify_neighbours()
        self.loop_is_not_identity()
        self.neighbour_table()
        self.normalization()
        self.balance()
        self.derive_eigenvector()
        self.apply_operator()
        self.point_count()
        self.modular_form_connection()
        self.compare_primes()
        self.architecture()
        self.closing()

    # ------------------------------------------------------------------- hook
    def hook(self):
        title = Text("Two problems. One unexpected answer.", font_size=46, color=INK)
        title.move_to(p2(0, 3.1))
        graph = neighbour_graph(1.25, p2(-3.6, 1.35))
        left_label = Text("mix numbers between neighbours", font_size=26, color=BLUE)
        left_label.move_to(p2(-3.6, -0.15))
        left_sub = Text("a pattern gets scaled by", font_size=22, color=DIM)
        left_sub.move_to(p2(-3.6, -0.65))
        equation = MathTex(*EQUATION, font_size=44, color=CURVE).move_to(p2(3.6, 1.35))
        right_label = Text("count solutions of an equation", font_size=26, color=CURVE)
        right_label.move_to(p2(3.6, -0.15))
        right_sub = Text("baseline minus point count", font_size=22, color=DIM)
        right_sub.move_to(p2(3.6, -0.65))
        divider = Line(p2(0, 2.4), p2(0, -2.0), color=DIM, stroke_width=1.5)
        left_answer = MathTex("-2", font_size=84, color=GLOW).move_to(p2(-3.6, -1.55))
        right_answer = MathTex("3-5=", "-2", font_size=84, color=INK)
        right_answer[1].set_color(GLOW)
        right_answer.move_to(p2(3.6, -1.55))

        self.say(
            "Two computations that look unrelated: mixing numbers between\n"
            "neighbours, and counting the solutions of an equation.",
            FadeIn(title),
            FadeIn(graph),
            FadeIn(left_label),
            FadeIn(equation),
            FadeIn(right_label),
            FadeIn(divider),
            run_time=1.0,
        )
        self.play(
            FadeIn(left_sub),
            FadeIn(right_sub),
            FadeIn(left_answer),
            FadeIn(right_answer),
            run_time=0.8,
        )
        self.mark_poster()
        self.read()
        merged = MathTex("-2", font_size=110, color=GLOW).move_to(p2(0, -1.55))
        self.say(
            "Both reveal the same number, −2. This video explains why,\n"
            "and shows the two small sums underneath.",
            FadeOut(divider),
            FadeOut(left_answer),
            FadeOut(right_answer),
            FadeOut(left_sub),
            FadeOut(right_sub),
        )
        self.play(FadeIn(merged, scale=1.3), run_time=0.6)
        self.read()
        self.clear_stage()

    # ---------------------------------------------------------- fair counting
    def fair_counting(self):
        groups = families()
        marks = {bits: marking(bits) for family in groups for bits in family}
        for index, bits in enumerate(product((0, 1), repeat=4)):
            row, column = divmod(index, 4)
            marks[bits].move_to(p2(-2.0 + 1.35 * column, 2.55 - 1.35 * row))
        self.say(
            "Start with a square. Switch each corner on or off:\n16 markings.",
            *self.chapter("Part 1 of 4: fair counting"),
            LaggedStart(
                *[FadeIn(mark, scale=0.7) for mark in marks.values()], lag_ratio=0.04
            ),
            run_time=1.3,
        )
        frames = VGroup(
            *[
                SurroundingRectangle(marks[bits], color=AMBER, buff=0.12)
                for bits in groups[3]
            ]
        )
        self.read()
        self.say(
            "Rotating the square turns these four into each other.\n"
            "They are one pattern, seen from four sides.",
            LaggedStart(*[Create(frame) for frame in frames], lag_ratio=0.2),
            run_time=1.0,
        )
        self.read()

        row_y = [2.6 - 0.8 * i for i in range(len(groups))]
        moves = []
        for y, family in zip(row_y, groups):
            for k, bits in enumerate(family):
                mark = marks[bits]
                mark.generate_target()
                mark.target.scale(0.5).move_to(p2(-6.3 + 0.8 * k, y))
                moves.append(MoveToTarget(mark))
        columns = {"copies": -1.5, "symmetries": 1.0, "weight": 3.4}
        headers = VGroup(
            *[
                Text(name, font_size=26, color=DIM).move_to(p2(x, 3.3))
                for name, x in columns.items()
            ]
        )
        copies, symmetries, weights = VGroup(), VGroup(), VGroup()
        for y, family in zip(row_y, groups):
            order = 4 // len(family)
            copies.add(
                Text(str(len(family)), font_size=34, color=INK).move_to(
                    p2(columns["copies"], y)
                )
            )
            symmetries.add(
                Text(str(order), font_size=34, color=AMBER).move_to(
                    p2(columns["symmetries"], y)
                )
            )
            weight = "1" if order == 1 else rf"\tfrac{{1}}{{{order}}}"
            weights.add(
                MathTex(weight, font_size=46, color=AMBER).move_to(
                    p2(columns["weight"], y)
                )
            )
        self.say(
            "Sorted by rotation, 6 patterns remain. A pattern's symmetries are\n"
            "the rotations that leave it unchanged, 'no turn' included.",
            FadeOut(frames),
            *moves,
            FadeIn(headers[:2]),
            LaggedStart(*[FadeIn(item) for item in copies], lag_ratio=0.1),
            LaggedStart(*[FadeIn(item) for item in symmetries], lag_ratio=0.1),
            run_time=1.8,
        )
        self.read()

        def row_box(i):
            members = VGroup(
                *[marks[bits] for bits in groups[i]], copies[i], symmetries[i]
            )
            return SurroundingRectangle(members, color=GLOW, buff=0.1)

        def row_product(i):
            count, order = len(groups[i]), 4 // len(groups[i])
            noun_c = "copy" if count == 1 else "copies"
            noun_s = "symmetry" if order == 1 else "symmetries"
            text = MathTex(
                rf"{count}\text{{ {noun_c}}}\times{order}\text{{ {noun_s}}}",
                "=",
                "4",
                font_size=32,
                color=INK,
            )
            text[2].set_color(GLOW)
            return text.move_to(p2(4.5, row_y[i]))

        focus, focus_text = row_box(3), row_product(3)
        self.say(
            "Take one row: 4 copies, 1 symmetry. The product is 4,\n"
            "the number of rotations. That is true of every row.",
            Create(focus),
            FadeIn(focus_text),
        )
        self.read()
        for i in (2, 0):
            self.play(
                Transform(focus, row_box(i)),
                Transform(focus_text, row_product(i)),
                run_time=0.7,
            )
            self.wait(0.9)

        derived = lines("1 ÷ symmetries\n= copies ÷ 4", 24, AMBER, buff=0.12).move_to(
            p2(5.55, 1.2)
        )
        total_line = Line(p2(2.7, -1.82), p2(4.1, -1.82), color=DIM, stroke_width=2)
        total = MathTex("4", font_size=54, color=GLOW).move_to(
            p2(columns["weight"], -2.2)
        )
        total_label = Text("total", font_size=26, color=DIM).next_to(
            total, LEFT, buff=0.35
        )
        known = MathTex(r"=16\div 4", font_size=46, color=GLOW).next_to(
            total, RIGHT, buff=0.25
        )
        self.say(
            "So weigh each pattern by (1 ÷ symmetries), its share of the\n"
            "four rotations, and sum the weights.",
            FadeOut(focus),
            FadeOut(focus_text),
            FadeIn(headers[2]),
            FadeIn(derived),
            LaggedStart(
                *[FadeIn(item, shift=0.2 * RIGHT) for item in weights], lag_ratio=0.1
            ),
            run_time=1.4,
        )
        self.play(Create(total_line), FadeIn(total), FadeIn(total_label), run_time=0.7)
        self.read()
        self.say(
            "The total is 16 ÷ 4 = 4, known before listing anything.\n"
            "This weighted count is called the mass.",
            FadeIn(known, shift=0.2 * LEFT),
        )
        self.read()

        lost = VGroup(
            *[marks[bits] for bits in groups[4]], copies[4], symmetries[4], weights[4]
        )
        comparison = MathTex(
            r"\text{found }3", "<", r"\text{expected }4", font_size=42
        ).move_to(p2(3.4, -2.2))
        comparison[0].set_color(WARN)
        self.say(
            "Leave out this pattern and its weight disappears. The list now\n"
            "accounts for only 3 of the expected mass of 4.",
            FadeOut(lost),
            FadeOut(total_label),
            FadeOut(total),
            FadeOut(known),
            FadeIn(comparison),
        )
        self.read()
        self.play(
            FadeIn(lost),
            FadeOut(comparison),
            FadeIn(total_label),
            FadeIn(total),
            FadeIn(known),
            run_time=0.6,
        )
        card = code_card("class_mass([4, 4, 2, 1, 1, 1])  →  4", 24).move_to(
            p2(-3.4, -2.2)
        )
        self.say(
            "That sum is the kernel's first function: hand it the symmetry\n"
            "counts and it adds their reciprocals as an exact fraction.",
            FadeIn(card, shift=0.2 * UP),
        )
        self.read()
        self.clear_stage()

    # ------------------------------------------------------- level-11 example
    def level_eleven_mass(self):
        unit = 24.0  # frame units per unit of mass, so 5/12 spans 10
        left = -unit * 5 / 24
        bar_y, height = 0.75, 1.0
        split = left + unit / 4

        bridge = lines(
            "the real objects: ideal classes in a quaternion algebra (discriminant 11)",
            20,
            DIM,
        ).move_to(p2(0, 3.05))
        icon_a = grid_icon("A", 1.3).move_to(p2(left + 0.8, -0.85))
        note_a = MathTex(
            r"\text{4 symmetries}\;\to\;\tfrac14", font_size=40, color=AMBER
        ).next_to(icon_a, RIGHT, buff=0.3)
        icon_b = grid_icon("B", 1.3).move_to(p2(split + 0.9, -0.85))
        note_b = MathTex(
            r"\text{6 symmetries}\;\to\;\tfrac16", font_size=40, color=BLUE
        ).next_to(icon_b, RIGHT, buff=0.3)
        self.say(
            "Number theory has the same problem with harder objects. Each has\n"
            "finitely many symmetries. We draw the first one found as A.",
            FadeIn(bridge),
            FadeIn(icon_a, scale=0.8),
            FadeIn(note_a),
        )
        self.read()

        target = Rectangle(
            width=unit * 5 / 12, height=height, stroke_color=INK, stroke_width=3
        ).move_to(p2(0, bar_y))
        target_label = Text(
            "Eichler's mass formula: the total must be (11 − 1) ÷ 24 = 5/12",
            font_size=26,
            color=INK,
        ).next_to(target, UP, buff=0.25)
        piece_a = Rectangle(
            width=unit / 4,
            height=height,
            stroke_width=0,
            fill_color=AMBER,
            fill_opacity=0.9,
        ).move_to(p2(left + unit / 8, bar_y))
        gap = Text("missing 1/6", font_size=28, color=WARN).move_to(
            p2(split + unit / 12, bar_y)
        )
        self.say(
            "A classical formula fixes the total mass in advance: 5/12.\n"
            "A alone weighs 1/4, so something is still missing.",
            FadeIn(target),
            FadeIn(target_label),
        )
        self.play(FadeIn(piece_a, shift=0.3 * RIGHT), FadeIn(gap), run_time=0.8)
        self.read()

        piece_b = Rectangle(
            width=unit / 6,
            height=height,
            stroke_width=0,
            fill_color=BLUE,
            fill_opacity=0.9,
        ).move_to(p2(split + unit / 12, bar_y))
        total = MathTex(
            r"\tfrac14", "+", r"\tfrac16", "=", r"\tfrac{5}{12}", font_size=56
        ).move_to(p2(4.9, -2.1))
        total[0].set_color(AMBER)
        total[2].set_color(BLUE)
        total[4].set_color(GLOW)
        done = check(56).next_to(total, RIGHT, buff=0.3)
        card = code_card("class_mass([4, 6])  →  5/12", 17).move_to(p2(-4.3, -2.1))
        self.say(
            "The search finds B, with 6 symmetries. 1/4 + 1/6 = 5/12.\n"
            "The total is reached.",
            FadeIn(icon_b, scale=0.8),
            FadeIn(note_b),
        )
        self.play(
            FadeIn(piece_b, shift=0.3 * RIGHT),
            FadeOut(gap),
            FadeIn(total),
            FadeIn(card),
            run_time=0.8,
        )
        self.read()
        condition = lines(
            "valid, distinct classes\nwith correct symmetry orders", 20, GLOW, buff=0.1
        ).move_to(p2(0.75, -2.1))
        self.say(
            "Provided the classes are valid, distinct and correctly weighted,\n"
            "the list is complete. A and B stay with us from here on.",
            FadeIn(condition),
        )
        self.play(FadeIn(done, scale=1.5), run_time=0.4)
        self.read()
        self.clear_stage()

    # ------------------------------------------------- what a neighbour is
    def neighbours_from_lattice(self):
        big = lattice(spacing=0.48).move_to(p2(0, 0.7))
        origin = Square(side_length=0.4, color=GLOW, stroke_width=3).move_to(big)
        origin_label = MathTex(r"(0,0)", font_size=34, color=GLOW).next_to(
            big, DOWN, buff=0.18
        )
        tag = Text("integer lattice", font_size=24, color=DIM)
        tag.move_to(p2(0, 2.9))
        self.say(
            "To picture a neighbour, start with an integer lattice.\n"
            "The marked point is the origin, with coordinates (0, 0).",
            *self.chapter("Part 2 of 4: mixing over neighbours"),
            FadeIn(tag),
            LaggedStart(*[FadeIn(d, scale=0.5) for d in big], lag_ratio=0.01),
            Create(origin),
            FadeIn(origin_label),
            run_time=1.2,
        )
        self.read()

        xs = (-5.1, -1.6, 1.7, 5.0)
        top_y = 1.0
        original = Text("original", font_size=24, color=INK).move_to(p2(xs[0], -0.45))
        arrow = Arrow(
            p2(xs[0] + 1.2, top_y), p2(xs[1] - 1.2, top_y), color=DIM, stroke_width=4
        )
        step = Text("keep half", font_size=20, color=DIM).next_to(arrow, UP, buff=0.1)
        self.say(
            "At the prime 2, keep half the lattice, including the origin.\n"
            "The sum of any two retained points must also be retained.",
            FadeOut(tag),
            FadeOut(origin_label),
            big.animate.scale(0.3 / 0.48).move_to(p2(xs[0], top_y)),
            origin.animate.scale(0.3 / 0.48).move_to(p2(xs[0], top_y)),
            FadeIn(original),
            FadeIn(arrow),
            FadeIn(step),
        )
        self.read()

        odd = lattice(lambda u, v: u % 2 == 1, WARN).move_to(p2(xs[1], top_y))
        missing_origin = origin.copy().set_color(WARN).set_fill(BG, opacity=1)
        missing_origin.move_to(odd)
        odd_label = Text("odd columns", font_size=24, color=WARN).next_to(
            odd, DOWN, buff=0.24
        )
        self.say(
            "Try the odd columns. Their spacing is regular, but the origin\n"
            "falls in the gap. This choice fails the sublattice test.",
            FadeIn(odd),
            FadeIn(odd_label),
            Create(missing_origin),
        )
        self.read()

        names = ("keep even x", "keep even y", "keep even x + y")
        formulas = (r"x\equiv 0", r"y\equiv 0", r"x+y\equiv 0")
        panels = VGroup()
        for (a, b), color, x, name, formula in zip(
            HALVINGS, RULE_COLORS, xs[1:], names, formulas
        ):
            grid = lattice(lambda u, v, a=a, b=b: (a * u + b * v) % 2 == 0, color)
            grid.move_to(p2(x, top_y))
            kept_origin = origin.copy().move_to(grid)
            label = Text(name, font_size=24, color=color).move_to(p2(x, -0.45))
            rule = MathTex(formula + r"\pmod 2", font_size=32, color=INK).move_to(
                p2(x, -1.0)
            )
            panels.add(VGroup(grid, kept_origin, label, rule))
        heading = Text("exactly three ways", font_size=30, color=INK).move_to(
            p2(1.7, 2.75)
        )
        self.say(
            "Three index-two sublattices qualify. Each keeps the origin and\n"
            "satisfies one of these parity rules.",
            FadeOut(odd),
            FadeOut(odd_label),
            FadeOut(missing_origin),
            LaggedStart(*[FadeIn(panel) for panel in panels], lag_ratio=0.5),
            FadeIn(heading),
            run_time=2.2,
        )
        self.read()
        model = lines(
            "a model of one prime: the real objects are grids in four dimensions",
            20,
            DIM,
        ).move_to(p2(0, -1.85))
        self.say(
            "The left grid models one prime. Each parity rule picks out\n"
            "one of its three neighbours at the prime 2.",
            FadeIn(model),
        )
        self.read()
        self.clear_stage()

    # ------------------------------------------------------- p + 1 neighbours
    def count_rules(self):
        headline = MathTex(
            r"\text{every rule: }",
            r"a\,x+b\,y",
            r"\ \text{is divisible by }p",
            font_size=40,
            color=INK,
        ).move_to(p2(0, 2.85))
        headline[1].set_color(GLOW)

        def pair_grid(p, centre, spacing, radius, colors):
            dots = VGroup()
            for a, b in product(range(p), repeat=2):
                dot = Dot(
                    centre
                    + p2(spacing * (a - (p - 1) / 2), spacing * (b - (p - 1) / 2)),
                    radius=radius,
                )
                dot.set_fill(
                    DIM if (a, b) == (0, 0) else colors[halving_rule(p, a, b)],
                    opacity=1,
                )
                dots.add(dot)
            return dots

        two = pair_grid(2, p2(-4.5, 0.95), 1.5, 0.2, dict(zip(HALVINGS, RULE_COLORS)))
        two_labels = VGroup(
            *[
                MathTex(f"({a},{b})", font_size=30, color=INK).next_to(
                    dot, DOWN, buff=0.12
                )
                for dot, (a, b) in zip(two, product(range(2), repeat=2))
            ]
        )
        two_labels[0].set_color(DIM)
        two_title = Text("p = 2", font_size=26, color=INK).move_to(p2(-4.5, 2.2))
        two_note = lines("3 nonzero pairs (a, b)\n3 rules", 22, DIM, buff=0.1).move_to(
            p2(-4.5, -1.2)
        )
        self.say(
            "Why three? Each rule says that some combination a·x + b·y is even.\n"
            "Mod 2 there are four pairs (a, b), and three of them are not zero.",
            FadeIn(headline),
            FadeIn(two_title),
            FadeIn(two),
            FadeIn(two_labels),
            FadeIn(two_note),
        )
        self.read()

        three = pair_grid(
            3, p2(-0.3, 0.75), 0.85, 0.2, dict(zip(halving_rules(3), RULE_COLORS))
        )
        three_title = Text("p = 3", font_size=26, color=INK).move_to(p2(-0.3, 2.2))
        three_note = lines(
            "8 nonzero pairs, 2 per rule\n4 rules", 22, DIM, buff=0.1
        ).move_to(p2(-0.3, -1.2))
        self.say(
            "For another prime p, ask that a·x + b·y be divisible by p. Doubling\n"
            "(a, b) gives the same rule, so at p = 3, 8 pairs make 4 rules.",
            FadeIn(three_title),
            FadeIn(three),
            FadeIn(three_note),
        )
        self.read()

        formula = MathTex(
            r"\frac{p^2-1}{p-1}", "=", "p+1", font_size=50, color=INK
        ).move_to(p2(4.4, 1.75))
        formula[2].set_color(GLOW)
        table = VGroup(
            Text("prime", font_size=22, color=DIM),
            *[MathTex(str(p), font_size=36, color=INK) for p in NEIGHBOUR_PRIMES],
            Text("neighbours", font_size=22, color=DIM),
            *[
                MathTex(str(len(halving_rules(p))), font_size=36, color=GLOW)
                for p in NEIGHBOUR_PRIMES
            ],
        ).arrange_in_grid(rows=2, buff=(0.3, 0.3))
        table.move_to(p2(4.3, 0.1))
        self.say(
            "In general: p² − 1 nonzero pairs, p − 1 per rule, so p + 1 rules.\n"
            "An object has p + 1 neighbours at the prime p.",
            FadeIn(formula),
            FadeIn(table),
        )
        self.read()
        caveat = lines(
            "for the objects in this video:\nevery prime except 11",
            22,
            DIM,
            buff=0.1,
        ).move_to(p2(4.3, -1.2))
        self.say(
            "So 'three neighbours at the prime 2' is 2 + 1. For our objects\n"
            "the rule holds at every prime except 11.",
            FadeIn(caveat),
        )
        self.read()
        self.clear_stage()

    # ------------------------------------------------- objects versus classes
    def classify_neighbours(self):
        columns = (-5.3, -1.6, 3.6)
        headers = VGroup(
            *[
                Text(text, font_size=24, color=DIM).move_to(p2(x, 3.0))
                for text, x in zip(
                    ("one object", "build its 3 neighbours", "classify each"), columns
                )
            ]
        )
        rows = []
        for letter, y in zip("AB", (1.85, 0.1)):
            icon = grid_icon(letter, 1.2).move_to(p2(columns[0], y))
            built = VGroup(
                *[
                    lattice(
                        lambda u, v, a=a, b=b: (a * u + b * v) % 2 == 0,
                        INK,
                        spacing=0.16,
                        reach=2,
                    )
                    for a, b in HALVINGS
                ]
            ).arrange(RIGHT, buff=0.45)
            built.move_to(p2(columns[1], y))
            build = Arrow(
                icon.get_right(), built.get_left(), color=DIM, stroke_width=4, buff=0.25
            )
            neighbours = CLASSES["AB".index(letter)].neighbours
            chips = VGroup(*[chip(c, 0.62) for c in neighbours]).arrange(
                RIGHT, buff=0.35
            )
            chips.move_to(p2(columns[2], y))
            sort = Arrow(
                built.get_right(),
                chips.get_left(),
                color=DIM,
                stroke_width=4,
                buff=0.25,
            )
            rows.append((icon, build, built, sort, chips))

        icon, build, built, sort, chips = rows[0]
        self.say(
            "Now the real objects. Take one object of class A and build\n"
            "its three neighbours at the prime 2.",
            FadeIn(headers[:2]),
            FadeIn(icon),
            FadeIn(build),
            LaggedStart(*[FadeIn(g, scale=0.7) for g in built], lag_ratio=0.3),
            run_time=1.4,
        )
        self.read()

        before, after = marking((1, 0, 0, 0), 0.6), marking((0, 1, 0, 0), 0.6)
        before.move_to(p2(-5.6, -1.75))
        after.move_to(p2(-4.0, -1.75))
        turned = Arrow(
            before.get_right(), after.get_left(), color=DIM, stroke_width=3, buff=0.15
        )
        recall = lines(
            "recall the squares:\na different marking, the same pattern",
            22,
            DIM,
            buff=0.1,
        ).next_to(after, RIGHT, buff=0.4)
        self.say(
            "They are three different objects. But part 1 taught us to ask\n"
            "a second question: which class does each one belong to?",
            FadeIn(before),
            FadeIn(after),
            FadeIn(turned),
            FadeIn(recall),
        )
        self.read()
        self.say(
            "For A, one neighbour is equivalent to A itself and two are\n"
            "equivalent to B. Different objects can share a class.",
            FadeIn(headers[2]),
            FadeIn(sort),
            LaggedStart(*[FadeIn(c, scale=0.6) for c in chips], lag_ratio=0.3),
            run_time=1.4,
        )
        self.read()

        icon, build, built, sort, chips = rows[1]
        self.say(
            "Do the same for an object of class B: all three of its\n"
            "neighbours are equivalent to A.",
            FadeIn(icon),
            FadeIn(build),
            FadeIn(built),
            FadeIn(sort),
            LaggedStart(*[FadeIn(c, scale=0.6) for c in chips], lag_ratio=0.3),
            run_time=1.4,
        )
        self.read()
        note = lines(
            "schematic: the workbench builds\nthe objects and tests equivalence",
            22,
            GLOW,
            buff=0.1,
        ).move_to(p2(3.9, -1.75))
        self.say(
            "The count of three came from the prime. These labels did not:\n"
            "an upstream program, the workbench, has to compute them.",
            FadeIn(note),
        )
        self.read()
        self.clear_stage()

    # ------------------------------------------------ a loop is not "nothing"
    def loop_is_not_identity(self):
        left_x, right_x = -3.6, 3.5
        graph = neighbour_graph(1.0, p2(right_x, 0.95))
        node_a, node_b, from_a, from_b = graph
        right_title = Text("one step at the prime 2", font_size=28, color=INK).move_to(
            p2(right_x, 2.85)
        )
        right_table = MathTex(
            r"\begin{pmatrix}1&2\\3&0\end{pmatrix}", font_size=46, color=INK
        ).move_to(p2(right_x, -1.0))
        right_note = Text(
            "build and classify three neighbours", font_size=22, color=DIM
        ).move_to(p2(right_x, -1.95))
        self.say(
            "Draw one arrow per neighbour, pointing at its class.\n"
            "Three arrows leave A and three leave B.",
            FadeIn(right_title),
            FadeIn(node_a),
            FadeIn(node_b),
        )
        self.play(
            LaggedStart(*[Create(a) for a in [*from_a, *from_b]], lag_ratio=0.25),
            run_time=1.8,
        )
        self.read()

        still_a = grid_icon("A").move_to(p2(left_x - 1.2, 0.75))
        still_b = grid_icon("B").move_to(p2(left_x + 1.2, 0.75))
        still = VGroup(
            still_a, still_b, self_loop(still_a, INK), self_loop(still_b, INK)
        )
        left_title = Text("doing nothing", font_size=28, color=INK).move_to(
            p2(left_x, 2.85)
        )
        left_table = MathTex(
            r"\begin{pmatrix}1&0\\0&1\end{pmatrix}", font_size=46, color=INK
        ).move_to(p2(left_x, -1.0))
        left_note = Text(
            "leave each object unchanged", font_size=22, color=DIM
        ).move_to(p2(left_x, -1.95))
        divider = Line(p2(0, 3.0), p2(0, -2.2), color=DIM, stroke_width=1.5)
        self.say(
            "The loop at A does not mean 'do nothing'. Doing nothing\n"
            "would be a different picture, with a loop on every class.",
            Indicate(from_a[0], color=GLOW),
            FadeIn(left_title),
            FadeIn(still),
            FadeIn(left_note),
            FadeIn(divider),
        )
        self.read()
        self.say(
            "The loop is a real step whose result is equivalent to A. None of\n"
            "B's three steps comes back to B, so B has no loop.",
            FadeIn(left_table),
            FadeIn(right_table),
            FadeIn(right_note),
        )
        self.read()
        self.clear_stage()

    # -------------------------------------------------------- neighbour table
    def neighbour_table(self):
        graph = neighbour_graph(1.35, p2(-3.5, 1.75))
        node_a, node_b, from_a, from_b = graph
        self.say(
            "Now turn the arrows into numbers. Each class has its list of\n"
            "three neighbours, already sorted into classes.",
            *self.chapter("The Brandt matrix"),
            FadeIn(node_a),
            FadeIn(node_b),
        )
        self.play(
            LaggedStart(*[Create(a) for a in from_a], lag_ratio=0.3), run_time=1.0
        )
        self.play(
            LaggedStart(*[Create(a) for a in from_b], lag_ratio=0.3), run_time=1.0
        )
        list_y = -0.15
        label_a = Text("A's neighbours", font_size=24, color=DIM).move_to(
            p2(node_a.get_x(), list_y)
        )
        label_b = Text("B's neighbours", font_size=24, color=DIM).move_to(
            p2(node_b.get_x(), list_y)
        )
        list_a = VGroup(*[chip(c) for c in CLASSES[0].neighbours]).arrange(
            RIGHT, buff=0.14
        )
        list_a.next_to(label_a, DOWN, buff=0.2)
        list_b = VGroup(*[chip(c) for c in CLASSES[1].neighbours]).arrange(
            RIGHT, buff=0.14
        )
        list_b.next_to(label_b, DOWN, buff=0.2)
        self.play(
            FadeIn(label_a),
            FadeIn(label_b),
            LaggedStart(
                *[FadeIn(c, scale=0.6) for c in [*list_a, *list_b]], lag_ratio=0.12
            ),
            run_time=1.2,
        )
        self.read()

        col_x = {"A": 3.35, "B": 5.55}
        row_y = {"A": 1.75, "B": 0.05}
        edges_x, edges_y = (2.25, 4.45, 6.65), (2.6, 0.9, -0.8)
        headers = VGroup(
            Text("lands on A", font_size=24, color=AMBER).move_to(p2(col_x["A"], 2.9)),
            Text("lands on B", font_size=24, color=BLUE).move_to(p2(col_x["B"], 2.9)),
            Text("from A", font_size=24, color=AMBER).move_to(p2(1.45, row_y["A"])),
            Text("from B", font_size=24, color=BLUE).move_to(p2(1.45, row_y["B"])),
        )
        frame = VGroup(
            *[
                Line(p2(edges_x[0], y), p2(edges_x[2], y), color=DIM, stroke_width=2)
                for y in edges_y
            ],
            *[
                Line(p2(x, edges_y[0]), p2(x, edges_y[2]), color=DIM, stroke_width=2)
                for x in edges_x
            ],
        )
        cell = Rectangle(
            width=2.2, height=1.7, stroke_color=GLOW, stroke_width=4
        ).move_to(p2(col_x["B"], row_y["A"]))
        samples = [1 if name == "B" else 0 for name in CLASSES[0].neighbours]
        assert sum(samples) == MATRIX[0][1]
        ticks = VGroup(
            *[
                MathTex(str(value), font_size=44, color=GLOW).next_to(
                    tile, DOWN, buff=0.18
                )
                for value, tile in zip(samples, list_a)
            ]
        )
        self.say(
            "Build a table one cell at a time. Start at A. Mark each\n"
            "neighbour that lands on B: 0, 1, 1.",
            FadeIn(headers),
            FadeIn(frame),
            Create(cell),
        )
        self.play(
            LaggedStart(*[FadeIn(t, shift=0.1 * DOWN) for t in ticks], lag_ratio=0.4),
            run_time=1.2,
        )
        self.read()

        def settle(chips, source, target):
            spread = 0.6
            start = -spread * (len(chips) - 1) / 2
            return [
                c.animate.move_to(
                    p2(col_x[target] + start + spread * i, row_y[source] + 0.4)
                )
                for i, c in enumerate(chips)
            ]

        counts = {
            (source, target): MathTex(
                str(MATRIX[i][j]),
                font_size=60,
                color=INK if MATRIX[i][j] else DIM,
            ).move_to(p2(col_x[target], row_y[source] - 0.35))
            for i, source in enumerate("AB")
            for j, target in enumerate("AB")
        }
        card = code_card("hecke(u=1, q=2, k=0, r=2, [0, 1, 1])  →  2", 19).move_to(
            p2(-3.3, -2.1)
        )
        self.say(
            "Add the marks, 0 + 1 + 1 = 2, and divide by a scale, here 1.\n"
            "That is one call of the kernel's second function.",
            *settle([list_a[1], list_a[2]], "A", "B"),
            FadeIn(counts[("A", "B")], scale=1.4),
            FadeIn(card, shift=0.2 * UP),
        )
        self.read()
        rest = [counts[key] for key in (("A", "A"), ("B", "A"), ("B", "B"))]
        self.say(
            "Every other cell is another call. The finished table is known\n"
            "as the Brandt matrix. Assembling it is the caller's job.",
            FadeOut(ticks),
            FadeOut(cell),
            FadeOut(label_a),
            FadeOut(label_b),
            *settle([list_a[0]], "A", "A"),
            *settle(list(list_b), "B", "A"),
            LaggedStart(*[FadeIn(c, scale=1.4) for c in rest], lag_ratio=0.2),
            run_time=1.2,
        )
        self.read()
        self.clear_stage()

    # ---------------------------------------------------------- normalization
    def normalization(self):
        formula = MathTex(
            r"\texttt{hecke}",
            "=",
            r"\frac{v_1+v_2+\cdots}{u\cdot q^{\,k\lfloor r/2\rfloor}}",
            font_size=64,
            color=INK,
        ).move_to(p2(0, 2.1))
        formula[0].set_color(BLUE)
        top = Text("add the samples", font_size=24, color=DIM).next_to(
            formula[2], RIGHT, buff=0.5
        )
        top.shift(0.45 * UP)
        bottom = Text("divide by the scale", font_size=24, color=DIM).next_to(
            formula[2], RIGHT, buff=0.5
        )
        bottom.shift(0.45 * DOWN)
        self.say(
            "There the scale was 1. In general it is built from parameters\n"
            "the caller supplies, and the samples need not be 0 or 1.",
            FadeIn(formula),
            FadeIn(top),
            FadeIn(bottom),
        )
        self.read()

        card = code_card("hecke(u=2/3, q=7, k=0, r=4, [1/2, -2/3])  →  -1/4", 22)
        card.move_to(p2(0, 0.0))
        worked = MathTex(
            r"\frac{\tfrac12-\tfrac23}{\tfrac23\cdot 7^{\,0}}",
            "=",
            r"\frac{-\tfrac16}{\tfrac23}",
            "=",
            r"-\tfrac14",
            font_size=52,
        ).move_to(p2(0, -1.45))
        worked[4].set_color(GLOW)
        source = mono("a row of tests/vectors/kernel.tsv", 16, DIM).next_to(
            card, UP, buff=0.15
        )
        self.say(
            "With fractions in, the answer is an exact fraction out,\n"
            "never a rounded decimal.",
            FadeIn(card, shift=0.2 * UP),
            FadeIn(source),
            FadeIn(worked),
        )
        self.read(0.5)
        self.clear_stage()

    # ---------------------------------------------------------------- balance
    def balance(self):
        self.icon_a = grid_icon("A", 1.5).move_to(p2(-3.6, 1.55))
        self.icon_b = grid_icon("B", 1.5).move_to(p2(3.6, 1.55))
        forth = Arrow(
            p2(-2.5, 1.85), p2(2.5, 1.85), color=AMBER, stroke_width=6, buff=0
        )
        back = Arrow(p2(2.5, 1.25), p2(-2.5, 1.25), color=BLUE, stroke_width=6, buff=0)
        forth_label = Text(
            "2 of A's neighbours are B", font_size=26, color=AMBER
        ).next_to(forth, UP, buff=0.12)
        back_label = Text(
            "3 of B's neighbours are A", font_size=26, color=BLUE
        ).next_to(back, DOWN, buff=0.12)
        loop = Arc(
            radius=0.42,
            start_angle=-50 * DEGREES,
            angle=280 * DEGREES,
            color=AMBER,
            stroke_width=5,
        ).move_to(self.icon_a.get_top() + 0.32 * UP)
        loop.add_tip(tip_length=0.2, tip_width=0.2)
        loop_label = Text("1 lands back in A", font_size=24, color=AMBER).next_to(
            loop, LEFT, buff=0.2
        )
        self.links = VGroup(forth, back, forth_label, back_label, loop, loop_label)
        self.mass_a = MathTex(r"\text{mass }\tfrac14", font_size=44, color=AMBER)
        self.mass_a.next_to(self.icon_a, DOWN, buff=0.2)
        self.mass_b = MathTex(r"\text{mass }\tfrac16", font_size=44, color=BLUE)
        self.mass_b.next_to(self.icon_b, DOWN, buff=0.2)
        self.say(
            "Now connect the two functions. A counts B twice among its\n"
            "neighbours; B counts A three times. It looks lopsided.",
            FadeIn(self.icon_a),
            FadeIn(self.icon_b),
            Create(forth),
            Create(back),
            Create(loop),
            FadeIn(forth_label),
            FadeIn(back_label),
            FadeIn(loop_label),
        )
        self.read()

        self.balanced = MathTex(
            r"\tfrac14\times 2",
            "=",
            r"\tfrac16\times 3",
            font_size=60,
            color=INK,
        ).move_to(p2(0, -0.75))
        self.balanced[0].set_color(AMBER)
        self.balanced[2].set_color(BLUE)
        tick = check(56).next_to(self.balanced, RIGHT, buff=0.35)
        self.balanced.add(tick)
        self.say(
            "Weigh each side by its mass from part 1: 1/4 × 2 = 1/6 × 3.\n"
            "The table is exactly balanced by the masses.",
            FadeIn(self.mass_a),
            FadeIn(self.mass_b),
            FadeIn(self.balanced, shift=0.2 * UP),
        )
        self.read()
        bounds = MathTex(
            r"3n_{AB}=2n_{BA},\qquad 0\le n_{AB},n_{BA}\le 3",
            font_size=37,
            color=INK,
        ).move_to(p2(0, -1.55))
        choices = MathTex(
            r"(n_{AB},n_{BA})\in\{",
            r"(0,0)",
            ",",
            r"(2,3)",
            r"\}",
            font_size=40,
            color=INK,
        ).move_to(p2(0, -2.14))
        self.say(
            "Call the two crossing counts n_AB and n_BA. Each has to be a\n"
            "whole number from 0 to 3. Two pairs satisfy the balance equation.",
            FadeIn(bounds),
            FadeIn(choices),
        )
        self.read()
        strike = Line(choices[1].get_left(), choices[1].get_right(), color=WARN)
        self.say(
            "The table has an edge from A to B. That rules out (0, 0).\n"
            "The crossing counts must be 2 and 3, leaving one loop at A.",
            Indicate(forth, color=GLOW),
            Create(strike),
            choices[3].animate.set_color(GLOW),
        )
        self.read()
        self.play(FadeOut(bounds), FadeOut(choices), FadeOut(strike), run_time=0.4)

    # ----------------------------------------------------- derive eigenvector
    def derive_eigenvector(self):
        # Mixing (a, b) gives (a + 2b, 3a); its mass-weighted sum is tripled.
        a, b = Fraction(5), Fraction(-7)
        mixed = (
            MATRIX[0][0] * a + MATRIX[0][1] * b,
            MATRIX[1][0] * a + MATRIX[1][1] * b,
        )
        before = CLASSES[0].mass * a + CLASSES[1].mass * b
        assert CLASSES[0].mass * mixed[0] + CLASSES[1].mass * mixed[1] == 3 * before

        preserved = MathTex(
            r"\tfrac14\underbrace{(a+2b)}_{\text{new A}}",
            "+",
            r"\tfrac16\underbrace{(3a)}_{\text{new B}}",
            "=",
            r"3\left(\tfrac14\,a+\tfrac16\,b\right)",
            font_size=46,
            color=INK,
        ).move_to(p2(0, -0.8))
        preserved[0].set_color(AMBER)
        preserved[2].set_color(BLUE)
        preserved[4].set_color(GLOW)
        self.say(
            "Put any numbers a and b on A and B, and mix. Because of that\n"
            "balance, the mass-weighted sum just triples.",
            self.balanced.animate.scale(0.7).move_to(p2(0, 0.35)),
            FadeIn(preserved, shift=0.2 * UP),
        )
        self.read()

        average = MathTex(
            r"\tfrac14\,a", "+", r"\tfrac16\,b", "=", "0", font_size=48, color=INK
        )
        average[0].set_color(AMBER)
        average[2].set_color(BLUE)
        cleared = MathTex(r"\Longrightarrow\;", "3a+2b=0", font_size=48, color=INK)
        mode = MathTex(
            r"\Longrightarrow\;",
            rf"(a,\,b)\ \text{{is a multiple of}}\ ({MODE[0]},\,{MODE[1]})",
            font_size=48,
            color=INK,
        )
        mode[1].set_color(GLOW)
        self.derivation = VGroup(average, cleared, mode).arrange(RIGHT, buff=0.35)
        if self.derivation.width > 12.8:
            self.derivation.scale_to_fit_width(12.8)
        self.derivation.move_to(p2(0, -2.05))
        self.preserved = preserved
        self.say(
            "So a weighted sum of zero stays zero. The patterns with\n"
            "that property are the multiples of 2 on A, −3 on B.",
            FadeIn(average),
        )
        self.play(FadeIn(cleared), run_time=0.6)
        self.play(FadeIn(mode), run_time=0.6)
        self.read()

    # --------------------------------------------------------- apply operator
    def apply_operator(self):
        self.clear_stage()

        def destination_row(source, y):
            row = VGroup(*[chip(name, 0.75) for name in source.neighbours])
            row.arrange(RIGHT, buff=0.7).move_to(p2(0, y))
            label = Text(f"From {source.name}", font_size=31, color=INK)
            label.next_to(row, LEFT, buff=0.8)
            return row, label

        def chip_values(row, values):
            labels = VGroup()
            for tile, value in zip(row, values):
                labels.add(
                    MathTex(str(value), font_size=45).next_to(tile, DOWN, buff=0.13)
                )
            return labels

        a, b = CLASSES
        row_a, label_a = destination_row(a, 2.15)
        indicator = chip_values(row_a, [int(name == "B") for name in a.neighbours])
        answer = MathTex(rf"= {MATRIX[0][1]}", font_size=62, color=BLUE)
        answer.next_to(row_a, RIGHT, buff=0.6)
        role = Text("matrix entry", font_size=24, color=BLUE).next_to(answer, DOWN)
        self.say(
            "Keep A’s three destinations in place. Counting arrivals at B gives\n"
            "0 + 1 + 1 = 2, one entry in the matrix.",
            FadeIn(row_a),
            FadeIn(label_a),
            FadeIn(indicator),
            FadeIn(answer),
            FadeIn(role),
        )
        self.read()

        values = dict(zip((a.name, b.name), MODE))
        new_values = chip_values(row_a, [values[name] for name in a.neighbours])
        new_answer = MathTex(rf"= {MIXED[0]}", font_size=62, color=GLOW).move_to(answer)
        new_role = Text("output at A", font_size=24, color=GLOW).next_to(
            new_answer, DOWN
        )
        self.say(
            "Now give A the value 2 and B the value −3. On the same three\n"
            "destinations, the new values add to −4. That is the output at A.",
            Transform(indicator, new_values),
            Transform(answer, new_answer),
            Transform(role, new_role),
        )
        self.read()

        row_b, label_b = destination_row(b, 0.23)
        values_b = chip_values(row_b, [values[name] for name in b.neighbours])
        answer_b = MathTex(rf"= {MIXED[1]}", font_size=62, color=GLOW)
        answer_b.next_to(row_b, RIGHT, buff=0.6)
        role_b = Text("output at B", font_size=24, color=GLOW).next_to(answer_b, DOWN)
        self.say(
            "From B, all three neighbours land on A, so the second output is 6.\n"
            "Compare the entire output vector with the one we put in.",
            FadeIn(row_b),
            FadeIn(label_b),
            FadeIn(values_b),
            FadeIn(answer_b),
            FadeIn(role_b),
        )
        self.read()

        outcome = MathTex(r"(-4,\,6)", "=", "-2", r"(2,\,-3)", font_size=64)
        outcome.move_to(p2(0, -1.45))
        outcome[2].set_color(GLOW)
        self.say(
            "Both coordinates are multiplied by −2. This common scale factor\n"
            "is the Hecke eigenvalue at the prime 2.",
            FadeIn(outcome),
        )
        self.read(0.5)
        self.clear_stage()

    # ------------------------------------------------------------ point count
    def point_count(self):
        memory = VGroup(
            Text("neighbour mixing at 2:", font_size=24, color=DIM),
            MathTex(r"\times(-2)", font_size=46, color=GLOW),
        ).arrange(RIGHT, buff=0.25)
        memory_box = SurroundingRectangle(
            memory, color=DIM, buff=0.2, corner_radius=0.1
        )
        self.memory = VGroup(memory_box, memory).move_to(p2(4.35, 2.85))
        equation = MathTex(*EQUATION, font_size=48, color=CURVE).move_to(p2(-2.9, 2.85))
        self.say(
            "Now the other side: an equation that appears to have\n"
            "nothing to do with our neighbour graph.",
            *self.chapter("Part 3 of 4: counting points on the curve"),
            FadeIn(self.memory),
            FadeIn(equation, shift=0.2 * UP),
        )
        self.read()

        reduced = MathTex(
            r"y(y+1)", r"\equiv", r"x^2(x-1)", r"\pmod 2", font_size=52, color=CURVE
        ).move_to(p2(2.9, 1.35))

        def spot(x, y):
            return p2(-5.0 + 2.1 * x, -1.2 + 1.8 * y)

        axes = VGroup(
            Line(p2(-6.1, -2.0), p2(-1.9, -2.0), color=DIM, stroke_width=2),
            Line(p2(-6.1, -2.0), p2(-6.1, 1.4), color=DIM, stroke_width=2),
        )
        ticks = VGroup(
            *[
                MathTex(f"x={x}", font_size=30, color=DIM).move_to(
                    spot(x, 0) + 0.55 * DOWN + 0.55 * RIGHT
                )
                for x in (0, 1)
            ],
            *[
                MathTex(f"y={y}", font_size=30, color=DIM).move_to(
                    p2(-6.6, spot(0, y)[1])
                )
                for y in (0, 1)
            ],
        )
        pairs = list(product((0, 1), repeat=2))
        spots = VGroup()
        for pair in pairs:
            x, y = pair
            assert (y * (y + 1)) % 2 == 0 == (x * x * (x - 1)) % 2
            dot = Dot(spot(*pair), radius=0.28).set_fill(BG, opacity=1)
            dot.set_stroke(DIM, width=3)
            spots.add(dot)
        self.say(
            "Work mod 2: x and y are 0 or 1, and even numbers vanish.\n"
            "The equation simplifies, leaving four pairs to try.",
            FadeIn(reduced, shift=0.2 * UP),
            FadeIn(axes),
            FadeIn(ticks),
            FadeIn(spots),
        )
        self.read()

        facts = VGroup(
            MathTex(r"y(y+1)=0\text{ for }y=0,1", font_size=40, color=INK),
            MathTex(r"x^2(x-1)=0\text{ for }x=0,1", font_size=40, color=INK),
        ).arrange(DOWN, buff=0.25)
        facts.move_to(p2(2.9, 0.1))
        self.say(
            "Both sides are 0 whatever you plug in,\nso all four pairs are solutions.",
            FadeIn(facts),
        )
        self.play(
            LaggedStart(
                *[
                    dot.animate.set_fill(GLOW, opacity=1).set_stroke(GLOW)
                    for dot in spots
                ],
                lag_ratio=0.3,
            ),
            run_time=1.4,
        )
        self.read()

        infinity = Dot(p2(-3.95, 1.75), radius=0.28, color=CURVE)
        infinity_label = MathTex(r"\infty", font_size=44, color=CURVE).next_to(
            infinity, RIGHT, buff=0.2
        )
        count = MathTex(r"4+1=5\text{ points}", font_size=44, color=INK).move_to(
            p2(2.9, -1.05)
        )
        gap = MathTex("2+1", "-", "5", "=", "-2", font_size=64, color=INK).move_to(
            p2(2.9, -1.95)
        )
        gap[4].set_color(GLOW)
        self.say(
            "The completed curve has one more point, at infinity: 5 in all.\n"
            "An elliptic curve mod p has about p + 1 points.",
            FadeIn(infinity, scale=1.5),
            FadeIn(infinity_label),
            FadeIn(count),
        )
        self.read()
        self.say(
            "Expected 2 + 1, found 5. The gap is −2:\n"
            "the same number the neighbour graph produced.",
            FadeIn(gap, shift=0.2 * UP),
        )
        self.play(
            Indicate(gap[4], color=GLOW, scale_factor=1.5),
            Indicate(memory[1], color=GLOW, scale_factor=1.4),
            run_time=1.2,
        )
        self.read()
        self.clear_stage()

    # ------------------------------------------------ modular form connection
    def modular_form_connection(self):
        classes = panel(
            "Ideal classes A, B", "mixing table\nscale factors", BLUE, 4.4, 1.9
        ).move_to(p2(-4.3, 2.0))
        curve = panel(
            "Elliptic curve", "point counts mod p\nbaseline − count", CURVE, 4.4, 1.9
        ).move_to(p2(4.3, 2.0))
        terms = []
        for n, a in enumerate(FORM[:5], start=1):
            power = "q" if n == 1 else f"q^{n}"
            size = "" if abs(a) == 1 else str(abs(a))
            sign = "-" if a < 0 else ("+" if n > 1 else "")
            terms.append(f"{sign}{size}{power}")
        series = MathTex("f", "=", *terms, r"+\cdots", font_size=56, color=INK)
        series.move_to(p2(0, -0.6))
        series[3].set_color(GLOW)
        form_frame = SurroundingRectangle(
            series, color=GLOW, buff=0.35, corner_radius=0.15, stroke_width=3
        )
        form_title = Text(
            "a modular form of level 11", font_size=26, color=GLOW, weight="BOLD"
        ).next_to(form_frame, UP, buff=0.15)
        product_note = MathTex(
            r"f=q\prod_{n\ge 1}(1-q^n)^2(1-q^{11n})^2",
            font_size=34,
            color=DIM,
        ).next_to(form_frame, DOWN, buff=0.3)
        left_arrow = Arrow(
            classes.get_bottom(),
            form_frame.get_corner(UL) + 1.6 * RIGHT + 0.5 * UP,
            color=INK,
            stroke_width=4,
            buff=0.1,
        )
        right_arrow = Arrow(
            curve.get_bottom(),
            form_frame.get_corner(UR) + 1.6 * LEFT + 0.5 * UP,
            color=INK,
            stroke_width=4,
            buff=0.1,
        )
        self.say(
            "Why the same number? Both computations read one hidden object:\n"
            "a modular form of level 11, written here as a power series.",
            FadeIn(classes),
            FadeIn(curve),
            FadeIn(form_frame),
            FadeIn(form_title),
            FadeIn(series),
            FadeIn(product_note),
            run_time=1.0,
        )
        self.play(Create(left_arrow), Create(right_arrow), run_time=0.7)
        self.read()
        ring = SurroundingRectangle(series[3], color=GLOW, buff=0.1)
        identity = MathTex(
            r"\text{Hecke eigenvalue at 2}",
            "=",
            "a_2",
            "=",
            "3-5",
            font_size=48,
            color=INK,
        ).move_to(product_note)
        identity[0].set_color(BLUE)
        identity[2].set_color(GLOW)
        identity[4].set_color(CURVE)
        self.say(
            "Call its coefficient of q² a₂. Both routes compute a₂ = −2:\n"
            "one as a scale factor, one from point counts. It is a theorem.",
            Create(ring),
            FadeOut(product_note),
            FadeIn(identity),
        )
        self.read(1.0)
        self.clear_stage()

    # --------------------------------------------------------- compare primes
    def compare_primes(self):
        base_y, step, pitch = 0.55, 0.5, 1.45
        baseline = Line(p2(-3.0, base_y), p2(6.7, base_y), color=DIM, stroke_width=2)
        legend = VGroup(
            lines("curve:\np + 1 − points", 24, CURVE, buff=0.1),
            lines("series:\ncoefficient of q^p", 24, GLOW, buff=0.1),
        ).arrange(DOWN, buff=0.5)
        legend.move_to(p2(-5.1, 0.6))
        groups = VGroup()
        for i, (p, gap, coefficient) in enumerate(
            zip(PRIMES, CURVE_GAPS, FORM_AT_PRIMES)
        ):
            x = -2.2 + pitch * i
            pair = VGroup()
            for offset, value, color in (
                (-0.24, gap, CURVE),
                (0.24, coefficient, GLOW),
            ):
                bar = Rectangle(
                    width=0.42,
                    height=max(0.06, step * abs(value)),
                    stroke_width=0,
                    fill_color=color,
                    fill_opacity=0.95,
                )
                bar.move_to(
                    p2(x + offset, base_y), aligned_edge=DOWN if value >= 0 else UP
                )
                pair.add(bar)
            sign = 1 if gap >= 0 else -1
            value = MathTex(str(gap), font_size=40, color=INK).move_to(
                p2(x, base_y + step * gap + 0.35 * sign)
            )
            prime = MathTex(f"p={p}", font_size=32, color=DIM).move_to(p2(x, -1.35))
            groups.add(VGroup(pair, value, prime))
        credit = lines(
            "Both series are computed independently in this scene: one by counting points, one by expanding the product.",
            18,
            DIM,
        ).move_to(p2(0.6, -2.05))
        self.say(
            "These bars compare curve counts with series coefficients.\n"
            "We computed the neighbour table only at p = 2.",
            FadeIn(baseline),
            FadeIn(legend),
            FadeIn(credit),
        )
        for group in groups:
            self.play(FadeIn(group, shift=0.15 * UP), run_time=0.4)
        self.read()
        self.say(
            "They agree at every prime of good reduction: for this curve,\n"
            "every prime except 11. The neighbour side matches by theorem."
        )
        self.read()
        self.clear_stage()

    # ----------------------------------------------------------- architecture
    def architecture(self):
        a, b = CLASSES
        rows = [item.neighbours for item in CLASSES]
        unique = [tuple(dict.fromkeys(row)) for row in rows]
        weights = [item.mass / MASS for item in CLASSES]
        forward, reverse = (
            Fraction(row.count(target), len(row))
            for row, target in zip(rows, (b.name, a.name))
        )
        faulty_forward, faulty_reverse = (
            Fraction(row.count(target), len(row))
            for row, target in zip(unique, (b.name, a.name))
        )
        assert weights == [Fraction(3, 5), Fraction(2, 5)]
        assert weights[0] * forward == weights[1] * reverse == Fraction(2, 5)
        assert weights[0] * faulty_forward == Fraction(3, 10)
        assert weights[1] * faulty_reverse == Fraction(2, 5)

        def vertex(item, j, weight, x):
            icon = grid_icon(item.name, 0.95).move_to(p2(x, 1.8))
            point = MathTex(f"j={j}", font_size=36).next_to(icon, UP, buff=0.15)
            label = Text(f"weight {weight}", font_size=25).next_to(
                icon, DOWN, buff=0.15
            )
            tiles = VGroup(*[chip(name, 0.5) for name in item.neighbours])
            tiles.arrange(RIGHT, buff=0.1).move_to(p2(x, 0.05))
            return icon, point, label, tiles

        icon_a, point_a, label_a, chips_a = vertex(a, 1, weights[0], -4.8)
        icon_b, point_b, label_b, chips_b = vertex(b, 0, weights[1], 4.8)
        title = Text("Checking a supersingular isogeny graph", font_size=34).move_to(
            p2(0, 3.0)
        )
        self.say(
            "We used Gross’s table at level 11. The Rust example finds these edges\n"
            "independently from the roots of a modular polynomial modulo 11.",
            *self.chapter("Part 4 of 4: the software"),
            FadeIn(title),
            FadeIn(icon_a),
            FadeIn(icon_b),
            FadeIn(point_a),
            FadeIn(point_b),
            FadeIn(chips_a),
            FadeIn(chips_b),
        )
        self.read()

        def flow(weight, probability, color, y):
            return MathTex(
                rf"{weight}\ \times\ {probability}\ =\ {weight * probability}",
                font_size=43,
                color=color,
            ).move_to(p2(0, y))

        forth = Arrow(p2(-3.5, 1.55), p2(3.5, 1.55), color=AMBER, buff=0)
        back = Arrow(p2(3.5, 0.85), p2(-3.5, 0.85), color=BLUE, buff=0)
        flow_a = flow(weights[0], forward, AMBER, 1.98)
        flow_b = flow(weights[1], reverse, BLUE, 0.37)
        formula = Text(
            "flow = vertex weight × chance of crossing", font_size=27
        ).move_to(p2(0, -1.08))
        self.say(
            "Divide each mass by 5/12 to get its share. Starting at A, two of\n"
            "three edges cross. From B, all cross. The flows agree at 2/5.",
            FadeIn(label_a),
            FadeIn(label_b),
            Create(forth),
            Create(back),
            FadeIn(flow_a),
            FadeIn(flow_b),
            FadeIn(formula),
        )
        self.read()
        wrong = flow(weights[0], faulty_forward, WARN, 1.98)
        self.say(
            "Now export each destination just once. From A, the chance of crossing\n"
            "drops to one half. The flows disagree: 3/10 one way, 2/5 the other.",
            FadeOut(chips_a[2]),
            FadeOut(chips_b[1]),
            FadeOut(chips_b[2]),
            Transform(flow_a, wrong),
        )
        self.read()
        self.play(FadeOut(formula), run_time=0.35)
        command = code_card(
            "cargo run --locked --manifest-path examples/rust/Cargo.toml --example isogeny_graph",
            size=17,
        ).move_to(p2(0, -1.15))
        if command.width > 13.1:
            command.scale_to_fit_width(13.1)
        self.say(
            "Run this example from the repository root. The kernel evaluates the\n"
            "supplied lists exactly. The balance check exposes the lost edges.",
            FadeIn(command),
        )
        self.read(0.5)
        self.clear_stage()

    # ---------------------------------------------------------------- closing
    def closing(self):
        title = Text("From a table entry to an eigenvalue", font_size=42, color=INK)
        title.move_to(p2(0, 3.0))
        mass_card, hecke_card = handoff_cards()
        mass_label = Text("total class mass", font_size=26, color=AMBER).next_to(
            mass_card, DOWN
        )
        entry_label = Text(
            "one matrix entry: A to B", font_size=26, color=BLUE
        ).next_to(hecke_card, DOWN)
        result = MathTex(
            r"\underbrace{(-4,\,6)}_{\text{whole output}}",
            "=",
            r"\underbrace{-2}_{\text{eigenvalue}}",
            r"(2,\,-3)",
            font_size=53,
        ).move_to(p2(0, -0.35))
        result[2].set_color(GLOW)
        self.say(
            "Counting B destinations gives the entry 2. Mixing the whole vector\n"
            "gives the factor −2, the same number we found by counting points.",
            *self.chapter("Recap"),
            FadeIn(title),
            FadeIn(mass_card),
            FadeIn(hecke_card),
            FadeIn(mass_label),
            FadeIn(entry_label),
            FadeIn(result),
        )
        self.read()
        verification = Text(
            f"Lean generates {FIXTURE_COUNT} fixtures. C and Rust replay them.",
            font_size=28,
            color=INK,
        ).move_to(p2(0, -1.72))
        self.say(
            "Lean proves properties of the arithmetic on supplied tables.\n"
            "The next film traces the two formulas through Alpöge’s Lean source.",
            FadeIn(verification),
        )
        self.read(1.0)
