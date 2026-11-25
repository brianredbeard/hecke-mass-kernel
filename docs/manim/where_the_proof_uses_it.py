"""Where the Lean proof uses the kernel's two sums.

This is the sequel to `what_the_kernel_computes.py`. It opens on the two
worked sums that video ends on and follows each into Alpöge's Lean
formalization of the Riemann Hypothesis.

    classMass    15 dependency links below `riemannHypothesis`.
                 `volumes_eq_masses_of_unfold` uses a double-coset
                 decomposition to identify a volume with the reciprocal sum.
    Setup.hecke  19 dependency links below. `HeckeAt` requires a target
                 readout to equal the normalized Hecke sum, and `heckeTieT`
                 transports that condition to a copied setup.

The declaration names are the two paths listed, with a public source link for
every step, in `docs/dependency-paths.md`.
The wording of what each theorem does follows `docs/primitive-in-the-proof.md`.
The level-11 numbers illustrate the arithmetic; the proof applies the same
formulas to its own data.

Render with `sh docs/manim/render.sh` from the repository root.
"""

from pathlib import Path

import numpy as np
from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Arrow,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    LaggedStart,
    Line,
    MathTex,
    Rectangle,
    ReplacementTransform,
    RoundedRectangle,
    SurroundingRectangle,
    Text,
    TransformFromCopy,
    VGroup,
)
from style import (
    AMBER,
    BG,
    BLUE,
    DIM,
    GLOW,
    INK,
    PANEL,
    Explainer,
    check,
    code_card,
    grid_icon,
    handoff_cards,
    lines,
    mono,
)

# Declaration names along the two paths in docs/dependency-paths.md, root first.
TRUNK = [
    "riemannHypothesis",
    "rhOfAll",
    "allChi",
    "UpperTheory.FinalTheorems.everyCharacter",
    "UpperTheory.FinalTheorems.everyCharacter_of_row",
    "UpperTheory.LiteratureTheorems.every_character_of_literature_of_vWin",
    "UpperTheory.Lit.every_character_of_theta_integrals_local_matching",
    "UpperTheory.Lit.nonempty_hyps_definite_side_of_closed_bound",
    "GlobalTheory.Fc.S0.StageU.hypotheses_nonempty_of_unramified_exponents_alt",
]
MASS_BRANCH = [
    "GlobalTheory.Fc.nonempty_hyps_of_allRows_alt",
    "UpperTheory.Top.classSel",
    "GlobalTheory.Fc.memberTop_final_contextParameters",
    "GlobalTheory.Mem.VolMass.volumes_eq_masses_of_unfold",
    "GlobalTheory.DefiniteDecompObj.doubleCosets_mass",
    "GlobalTheory.DefiniteDecomp.defClassDecomp",
    "GlobalTheory.Mass.classMass",
]
HECKE_BRANCH = [
    "UpperTheory.GalC.final_alt_alt",
    "UpperTheory.GalC.final_of_alt",
    "GlobalTheory.NLink.Final.slot_mv_extension_with_list_geo_cl",
    "GlobalTheory.T.exists_kept_choice_upper_lattice_alt",
    "GlobalTheory.LayerMove.exists_kept_nChoice_thData_upL",
    "GlobalTheory.T.geo_heq_geoHalf_of_same",
    "GlobalTheory.LayerMove.SerUp.ex",
    "GlobalTheory.LayerMove.SerUp.ex._proof_7",
    "GlobalTheory.HeightCounting.SerCopy.heckeTieT",
    "GlobalTheory.SeriesTie.HeckeAt",
    "GlobalTheory.SeriesTie.Setup.hecke",
]
SHARED_LINKS = len(TRUNK) - 1
MASS_LINKS = SHARED_LINKS + len(MASS_BRANCH)
HECKE_LINKS = SHARED_LINKS + len(HECKE_BRANCH)
assert (SHARED_LINKS, MASS_LINKS, HECKE_LINKS) == (8, 15, 19)

FROZEN_COMMIT = "4e8bb36"

FIXTURES = Path(__file__).resolve().parents[2] / "tests" / "vectors" / "kernel.tsv"
FIXTURE_COUNT = sum(1 for line in FIXTURES.read_text().splitlines() if line)


def p2(x: float, y: float) -> np.ndarray:
    return np.array([x, y, 0.0])


class WhereTheProofUsesIt(Explainer):
    subtitle_size = 28

    def construct(self):
        self.handoff()
        self.dependency_paths()
        self.volume_identity()
        self.hecke_compatibility()
        self.closing()

    # ---------------------------------------------------------------- handoff
    def handoff(self):
        mass_card, hecke_card = handoff_cards()
        source = lines(
            "Two paths from riemannHypothesis\nin Alpöge's Lean source",
            36,
            INK,
            buff=0.2,
        ).move_to(p2(0, -0.2))
        self.say(
            "We followed two chains of references from the declaration\n"
            "named riemannHypothesis in Alpöge’s Lean source.",
            FadeIn(mass_card),
            FadeIn(hecke_card),
            FadeIn(source, shift=0.2 * UP),
        )
        self.read()

        role_mass = Text("Volume identity", font_size=34, color=AMBER).next_to(
            mass_card, DOWN, buff=0.45
        )
        role_hecke = Text("Hecke compatibility", font_size=34, color=BLUE).next_to(
            hecke_card, DOWN, buff=0.45
        )
        caveat = lines(
            "The level-11 example illustrates the arithmetic.\n"
            "The formalization uses its own data.",
            26,
            INK,
            buff=0.15,
        ).move_to(p2(0, -1.4))
        self.say(
            "In the proof, the first enters a volume identity and the second\n"
            "a compatibility condition. This video follows each one in.",
            FadeOut(source),
            FadeIn(role_mass, shift=0.2 * DOWN),
            FadeIn(role_hecke, shift=0.2 * DOWN),
            FadeIn(caveat),
        )
        self.read(0.5)
        self.clear_stage()

    # ------------------------------------------------------- dependency paths
    def dependency_paths(self):
        # The equality is a verbatim excerpt of line 80 in the frozen source.
        filename = mono("AdmQAdmissibleConjugatePairPlaces.lean", 22, DIM)
        citation = Text(f"line 80 · commit {FROZEN_COMMIT}", font_size=22, color=DIM)
        header = VGroup(filename, citation).arrange(DOWN, buff=0.14).move_to(p2(0, 2.2))
        excerpt = VGroup(
            mono("rd g =", 35),
            mono("ρ.hecke", 35, BLUE),
            mono("i j b k P R z (rd f)", 35),
        ).arrange(RIGHT, buff=0.24)
        excerpt.move_to(p2(0, 0.85))
        highlight = SurroundingRectangle(excerpt[1], color=BLUE, buff=0.09)
        edge = VGroup(
            code_card("HeckeAt", 24),
            Arrow(LEFT, RIGHT, color=BLUE),
            code_card("Setup.hecke", 24, BLUE),
        ).arrange(RIGHT, buff=0.18)
        edge.move_to(p2(0, -0.9))
        self.say(
            "In the definition of HeckeAt, rd g is the value being specified.\n"
            "On the right, ρ.hecke applies the Hecke operator to rd f.",
            *self.chapter("Reading a source reference"),
            FadeIn(header),
            FadeIn(excerpt),
            Create(highlight),
        )
        self.read()
        self.say(
            "That reference gives one edge from HeckeAt to Setup.hecke.\n"
            "Watch where it sits in the two paths we traced.",
            FadeIn(edge),
        )
        self.read()
        step, origin_x, trunk_y = 0.46, -6.25, 0.4

        def branch_points(count, direction):
            return [
                p2(
                    origin_x + step * (SHARED_LINKS + i),
                    trunk_y + direction * 0.6 * min(i, 2),
                )
                for i in range(1, count + 1)
            ]

        trunk_points = [p2(origin_x + step * i, trunk_y) for i in range(len(TRUNK))]
        mass_points = branch_points(len(MASS_BRANCH), 1)
        hecke_points = branch_points(len(HECKE_BRANCH), -1)

        def chain(points, color, start=None):
            path = ([start] if start is not None else []) + points
            segments = VGroup(
                *[
                    Line(a, b, color=color, stroke_width=4)
                    for a, b in zip(path, path[1:])
                ]
            )
            nodes = VGroup(*[Dot(point, radius=0.07, color=color) for point in points])
            return segments, nodes

        trunk_lines, trunk_nodes = chain(trunk_points, INK)
        mass_lines, mass_nodes = chain(mass_points, AMBER, trunk_points[-1])
        hecke_lines, hecke_nodes = chain(hecke_points, BLUE, trunk_points[-1])

        root_tag = mono("riemannHypothesis", 23, INK).next_to(
            trunk_nodes[0], UP, buff=0.2, aligned_edge=LEFT
        )
        trunk_nodes[0].scale(1.9)
        shared_tag = Text(
            f"{SHARED_LINKS} shared links", font_size=24, color=INK
        ).next_to(trunk_lines, DOWN, buff=0.25)
        last_link = VGroup(hecke_nodes[-2], hecke_lines[-1], hecke_nodes[-1])
        last_link.set_color(GLOW)
        self.say(
            "The highlighted reference ends the blue path. Both paths start\n"
            "at riemannHypothesis and share their first eight links.",
            *self.chapter("Two paths from the root declaration"),
            FadeOut(header),
            FadeOut(excerpt),
            FadeOut(highlight),
            ReplacementTransform(edge, last_link),
            FadeIn(root_tag),
            LaggedStart(*[Create(s) for s in trunk_lines], lag_ratio=0.5),
            LaggedStart(*[FadeIn(n) for n in trunk_nodes], lag_ratio=0.5),
            FadeIn(shared_tag),
            run_time=1.8,
        )
        self.play(
            LaggedStart(*[Create(s) for s in mass_lines], lag_ratio=0.5),
            LaggedStart(*[FadeIn(n) for n in mass_nodes], lag_ratio=0.5),
            LaggedStart(*[Create(s) for s in hecke_lines[:-1]], lag_ratio=0.5),
            LaggedStart(*[FadeIn(n) for n in hecke_nodes[:-2]], lag_ratio=0.5),
            run_time=2.0,
        )
        self.read()

        def endpoint(node, role, name, count, color):
            return (
                VGroup(
                    Text(role, font_size=35, color=color, weight="BOLD"),
                    mono(f"{name} · {count} links", 20, INK),
                )
                .arrange(DOWN, buff=0.15, aligned_edge=LEFT)
                .next_to(node, RIGHT, buff=0.2)
            )

        mass_tag = endpoint(
            mass_nodes[-1], "Volume identity", "classMass", MASS_LINKS, AMBER
        )
        hecke_tag = endpoint(
            hecke_nodes[-1], "Hecke condition", "Setup.hecke", HECKE_LINKS, BLUE
        )
        at_tag = mono("HeckeAt", 19, GLOW).next_to(hecke_nodes[-2], UP, buff=0.16)
        self.say(
            f"The two paths shown have {MASS_LINKS} and {HECKE_LINKS} links. What does\n"
            "each definition contribute to the argument?",
            FadeIn(mass_tag),
            FadeIn(hecke_tag),
            FadeIn(at_tag),
        )
        self.mark_poster()
        self.read(0.5)
        self.clear_stage()

    # -------------------------------------------------------- volume identity
    def volume_identity(self):
        width, height, bar_y = 10.0, 1.1, 1.75
        left = -width / 2

        def piece(start, share, color, opacity, label):
            box = Rectangle(
                width=width * share,
                height=height,
                stroke_color=BG,
                stroke_width=3,
                fill_color=color,
                fill_opacity=opacity,
            ).move_to(p2(left + width * (start + share / 2), bar_y))
            ink = BG if opacity >= 0.9 else INK
            return VGroup(box, MathTex(label, font_size=46, color=ink).move_to(box))

        example = VGroup(
            piece(0, 0.6, AMBER, 0.9, r"\tfrac14"),
            piece(0.6, 0.4, BLUE, 0.9, r"\tfrac16"),
        )
        example_tag = Text(
            "part 1: the masses of A and B", font_size=24, color=DIM
        ).next_to(example, UP, buff=0.2)
        self.say(
            "In part 1, the masses of A and B filled a bar:\n1/4 + 1/6 = 5/12.",
            *self.chapter("Mass becomes a volume identity"),
            FadeIn(example),
            FadeIn(example_tag),
        )
        self.read()

        shares = (0.36, 0.26, 0.2, 0.18)
        labels = (r"\tfrac{1}{d_1}", r"\tfrac{1}{d_2}", r"\tfrac{1}{d_3}", r"\cdots")
        general, start = VGroup(), 0.0
        for i, (share, label) in enumerate(zip(shares, labels)):
            general.add(piece(start, share, AMBER, 0.3 + 0.15 * (i % 2), label))
            start += share
        general_tag = Text(
            "the proof: a volume, one piece per double-coset class",
            font_size=24,
            color=INK,
        ).next_to(general, UP, buff=0.2)
        definition = MathTex(
            r"d_i=\text{ the order of the symmetry group of class } i",
            font_size=34,
            color=DIM,
        ).next_to(general, DOWN, buff=0.25)
        self.say(
            "The proof has the same picture with its own data: a volume cut\n"
            "into one piece per double-coset class, each of size 1 ÷ d.",
            ReplacementTransform(example, general),
            FadeOut(example_tag),
            FadeIn(general_tag),
            FadeIn(definition),
        )
        self.read()

        identity = MathTex(
            r"\text{volume}",
            "=",
            r"\frac{1}{d_1}+\frac{1}{d_2}+\frac{1}{d_3}+\cdots",
            font_size=54,
            color=INK,
        ).move_to(p2(0, -1.0))
        identity[2].set_color(AMBER)
        sum_tag = mono("classMass", 22, AMBER).next_to(identity[2], DOWN, buff=0.25)
        source = mono("volumes_eq_masses_of_unfold", 18, DIM).next_to(
            identity, UP, buff=0.2
        )
        self.say(
            "The theorem volumes_eq_masses_of_unfold uses that decomposition:\n"
            "the volume equals the sum of the reciprocal symmetry orders.",
            FadeIn(identity, shift=0.2 * UP),
            FadeIn(source),
        )
        self.read()
        self.say(
            "That sum is classMass. In the proof, mass identifies a volume.",
            FadeIn(sum_tag, shift=0.1 * UP),
        )
        self.read()
        self.clear_stage()

    # ----------------------------------------------------- hecke compatibility
    def hecke_compatibility(self):
        destinations = VGroup(*(grid_icon(label) for label in "ABB"))
        destinations.arrange(RIGHT, buff=0.65).move_to(p2(-3.55, 1.6))
        row_tag = Text("Neighbours of A", font_size=27).next_to(
            destinations, UP, buff=0.25
        )

        def values(numbers):
            return VGroup(
                *[
                    MathTex(str(n), font_size=46, color=color).next_to(
                        chip, DOWN, buff=0.24
                    )
                    for chip, n, color in zip(
                        destinations, numbers, [AMBER, BLUE, BLUE]
                    )
                ]
            )

        indicators, samples = values([0, 1, 1]), values([2, -3, -3])
        entry = MathTex(r"0+1+1=2", font_size=47).move_to(p2(-3.55, -0.60))
        output = MathTex(r"g(A)=2-3-3=-4", font_size=47).move_to(entry)
        self.say(
            "Keep A’s three neighbours in view. Counting the B destinations\n"
            "gives the matrix entry 2.",
            *self.chapter("Hecke becomes a compatibility condition"),
            FadeIn(destinations),
            FadeIn(row_tag),
            FadeIn(indicators),
            FadeIn(entry),
        )
        self.read()
        self.say(
            "Now read the function at the same neighbours. Its values are\n"
            "2, −3 and −3. They give the new value at A, which is −4.",
            ReplacementTransform(indicators, samples),
            ReplacementTransform(entry, output),
        )
        self.read()

        card = RoundedRectangle(
            width=6.6,
            height=3.0,
            corner_radius=0.2,
            stroke_color=BLUE,
            stroke_width=3,
            fill_color=PANEL,
            fill_opacity=1,
        ).move_to(p2(3.5, 1.55))
        card_title = mono("HeckeAt", 24, BLUE).move_to(p2(3.5, 2.65))
        condition = MathTex(
            r"g(x)",
            "=",
            r"\frac{1}{u\cdot q^{\,k\lfloor r/2\rfloor}}\sum_{\gamma}f(x\gamma)",
            font_size=40,
            color=INK,
        ).move_to(p2(3.5, 1.55))
        condition[2].set_color(BLUE)
        scope = Text(
            "for every certified local input", font_size=24, color=INK
        ).move_to(p2(3.5, 0.45))
        self.say(
            "HeckeAt requires the target value to agree with the normalized\n"
            "neighbour sum for every certified local input.",
            FadeIn(card),
            FadeIn(card_title),
            FadeIn(condition),
            FadeIn(scope),
        )
        self.read()

        def setup(label, x):
            frame = RoundedRectangle(
                width=5.6,
                height=1.2,
                corner_radius=0.15,
                stroke_color=DIM,
                stroke_width=2.5,
            ).move_to(p2(x, 0.5))
            title = Text(label, font_size=22, color=INK).next_to(frame, UP, buff=0.12)
            equality = VGroup(
                MathTex(r"g=\text{normalized sum of }f", font_size=36, color=BLUE),
                check(40),
            ).arrange(RIGHT, buff=0.3)
            equality.move_to(frame)
            return frame, title, equality

        frame_a, title_a, equality_a = setup("original setup", -3.6)
        frame_b, title_b, equality_b = setup(
            "copied setup used in the series construction", 3.6
        )
        carry = Arrow(
            frame_a.get_right(),
            frame_b.get_left(),
            buff=0.1,
            color=GLOW,
            stroke_width=5,
        )
        carry_tag = mono("heckeTieT", 16, GLOW).next_to(carry, UP, buff=0.08)
        self.clear_stage()
        self.say(
            "The series construction copies the setup. The lemma heckeTieT\n"
            "carries the same equality across to the copy.",
            FadeIn(frame_a),
            FadeIn(title_a),
            FadeIn(equality_a),
            FadeIn(frame_b),
            FadeIn(title_b),
        )
        self.play(Create(carry), FadeIn(carry_tag), run_time=0.7)
        self.play(TransformFromCopy(equality_a, equality_b), run_time=1.2)
        self.read()
        self.clear_stage()

    # ---------------------------------------------------------------- closing
    def closing(self):
        mass_card, hecke_card = handoff_cards()
        take_mass = lines("Mass identifies\na volume", 32, AMBER, buff=0.14)
        take_mass.next_to(mass_card, UP, buff=0.4)
        take_hecke = lines(
            "The copied setup preserves\nthe Hecke condition", 32, BLUE, buff=0.14
        ).next_to(hecke_card, UP, buff=0.4)
        where_mass = mono("volumes_eq_masses_of_unfold", 16, DIM).next_to(
            mass_card, DOWN, buff=0.25
        )
        where_hecke = mono("HeckeAt, heckeTieT", 16, DIM).next_to(
            hecke_card, DOWN, buff=0.25
        )
        split = lines(
            "The formalization uses its own data.\n"
            f"Lean generates {FIXTURE_COUNT} finite-table examples\n"
            "for the C and Rust tests.",
            26,
            INK,
            buff=0.16,
        ).move_to(p2(0, -1.05))
        self.say(
            "So that is where the two sums enter the proof.\nOne identifies a volume.",
            *self.chapter("What each sum does"),
            FadeIn(take_mass),
            FadeIn(mass_card),
            FadeIn(where_mass),
        )
        self.read()
        self.say(
            "The other specifies the value of a transformed form.\n"
            "The same condition holds in the copied setup.",
            FadeIn(take_hecke),
            FadeIn(hecke_card),
            FadeIn(where_hecke),
        )
        self.read()
        self.play(FadeIn(split, shift=0.2 * UP), run_time=0.7)
        self.wait(5.0)
