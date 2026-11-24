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

The declaration names are the audited `project_body` paths recorded by the
research workbench in `proof_profile/research/spine-01/spine_milestones.json`.
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

# Declaration names along the two audited project_body paths, root first.
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

# Declarations reachable from the root in the audited export (proof_profile/README.md).
REACHABLE = "1,478,219"
FROZEN_COMMIT = "4e8bb36"

FIXTURES = Path(__file__).resolve().parents[2] / "tests" / "vectors" / "kernel.tsv"
FIXTURE_COUNT = sum(1 for line in FIXTURES.read_text().splitlines() if line)


def p2(x: float, y: float) -> np.ndarray:
    return np.array([x, y, 0.0])


def short(name: str) -> str:
    return name.split(".")[-1] if not name.endswith("Setup.hecke") else "Setup.hecke"


class WhereTheProofUsesIt(Explainer):
    subtitle_size = 28

    def construct(self):
        self.handoff()
        self.proof_size()
        self.dependency_paths()
        self.volume_identity()
        self.hecke_compatibility()
        self.closing()

    # ---------------------------------------------------------------- handoff
    def handoff(self):
        mass_card, hecke_card = handoff_cards()
        source = lines(
            "Two definitions in Alpöge's Lean formalization\nof the Riemann Hypothesis",
            36,
            INK,
            buff=0.2,
        ).move_to(p2(0, -0.2))
        self.say(
            "Part 1 ended on these two worked sums. Both formulas are\n"
            "definitions inside a machine-checked proof.",
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
            "The Lean proof uses the same formulas on its own data.",
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

    # ------------------------------------------------------------- proof size
    def proof_size(self):
        root = code_card("riemannHypothesis", 24, INK).move_to(p2(0, 3.0))
        rng = np.random.default_rng(11)
        layers, edges, dots = [[root.get_bottom()]], VGroup(), VGroup()
        for level, count in enumerate([5, 12, 26, 52, 96, 150], start=1):
            width = 1.6 + 2.05 * level
            y = 3.0 - 0.72 * level
            xs = np.sort(rng.uniform(-width / 2, width / 2, count))
            layer = [p2(x, y + rng.uniform(-0.12, 0.12)) for x in xs]
            for point in layer:
                parent = layers[-1][rng.integers(len(layers[-1]))]
                edges.add(
                    Line(parent, point, color=DIM, stroke_width=1).set_stroke(
                        opacity=0.3
                    )
                )
                dots.add(Dot(point, radius=0.035, color=DIM))
            layers.append(layer)
        tag = Text("dependency graph, schematic", font_size=20, color=DIM).move_to(
            p2(4.9, 3.0)
        )
        count = VGroup(
            Text(REACHABLE, font_size=60, color=GLOW),
            Text(
                "declarations reachable from the top theorem",
                font_size=26,
                color=INK,
            ),
            Text(
                f"audited export of the frozen source, commit {FROZEN_COMMIT}",
                font_size=20,
                color=DIM,
            ),
        ).arrange(DOWN, buff=0.18)
        plate = SurroundingRectangle(
            count,
            color=DIM,
            buff=0.35,
            corner_radius=0.15,
            fill_color=BG,
            fill_opacity=0.94,
        )
        self.say(
            "The proof's top theorem is named riemannHypothesis. About\n"
            "1.5 million declarations sit beneath it.",
            *self.chapter("The proof"),
            FadeIn(root),
            FadeIn(tag),
            LaggedStart(*[Create(edge) for edge in edges], lag_ratio=0.003),
            LaggedStart(*[FadeIn(dot) for dot in dots], lag_ratio=0.003),
            run_time=2.2,
        )
        self.play(FadeIn(VGroup(plate, count).move_to(p2(0, 0.1))), run_time=0.6)
        self.read()
        self.clear_stage()

    # ------------------------------------------------------- dependency paths
    def dependency_paths(self):
        step, origin_x, trunk_y = 0.5, -6.3, 0.4

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

        def name_tag(branch, nodes, name, side, color=INK, size=18):
            node = nodes[[short(n) for n in branch].index(name)]
            node.scale(1.9)
            return mono(name, size, color).next_to(node, side, buff=0.2)

        root_tag = mono("riemannHypothesis", 18, INK).next_to(
            trunk_nodes[0], UP, buff=0.2, aligned_edge=LEFT
        )
        trunk_nodes[0].scale(1.9)
        shared_tag = Text(
            f"shared path: {SHARED_LINKS} links", font_size=22, color=DIM
        ).next_to(trunk_lines, DOWN, buff=0.25)
        self.say(
            "Follow references downward: each declaration refers to the\n"
            "next. One shared dependency path forks into two branches.",
            *self.chapter("Two dependency paths"),
            FadeIn(root_tag),
            LaggedStart(*[Create(s) for s in trunk_lines], lag_ratio=0.5),
            LaggedStart(*[FadeIn(n) for n in trunk_nodes], lag_ratio=0.5),
            FadeIn(shared_tag),
            run_time=1.8,
        )
        self.play(
            LaggedStart(*[Create(s) for s in mass_lines], lag_ratio=0.5),
            LaggedStart(*[FadeIn(n) for n in mass_nodes], lag_ratio=0.5),
            LaggedStart(*[Create(s) for s in hecke_lines], lag_ratio=0.5),
            LaggedStart(*[FadeIn(n) for n in hecke_nodes], lag_ratio=0.5),
            run_time=2.0,
        )
        self.read()

        volume_tag = name_tag(
            MASS_BRANCH, mass_nodes, "volumes_eq_masses_of_unfold", UP
        )
        mass_tag = name_tag(MASS_BRANCH, mass_nodes, "classMass", RIGHT, AMBER, 20)
        mass_count = Text(
            f"{MASS_LINKS} dependency links", font_size=26, color=AMBER
        ).next_to(mass_tag, RIGHT, buff=0.5)
        tie_tag = name_tag(HECKE_BRANCH, hecke_nodes, "heckeTieT", DOWN)
        at_tag = name_tag(HECKE_BRANCH, hecke_nodes, "HeckeAt", UP)
        hecke_tag = name_tag(HECKE_BRANCH, hecke_nodes, "Setup.hecke", RIGHT, BLUE, 20)
        hecke_count = Text(
            f"{HECKE_LINKS} dependency links", font_size=26, color=BLUE
        ).next_to(hecke_tag, DOWN, buff=0.85, aligned_edge=RIGHT)
        self.say(
            f"classMass is reached after {MASS_LINKS} dependency links, Setup.hecke\n"
            f"after {HECKE_LINKS}. The labelled declarations are the ones that matter next.",
            FadeIn(mass_tag),
            FadeIn(mass_count),
            FadeIn(hecke_tag),
            FadeIn(hecke_count),
            FadeIn(volume_tag),
            FadeIn(tie_tag),
            FadeIn(at_tag),
        )
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
            return VGroup(box, MathTex(label, font_size=46, color=INK).move_to(box))

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
        icon_a = grid_icon("A", 1.2).move_to(p2(-5.0, 2.2))
        icon_b = grid_icon("B", 1.2).move_to(p2(-2.2, 2.2))
        f_a = MathTex("f(A)=2", font_size=38, color=AMBER).next_to(
            icon_a, DOWN, buff=0.2
        )
        f_b = MathTex("f(B)=-3", font_size=38, color=BLUE).next_to(
            icon_b, DOWN, buff=0.2
        )
        g_a = MathTex(
            "g(A)", "=", "2", "+", "(-3)", "+", "(-3)", "=", "-4", font_size=42
        ).move_to(p2(-3.6, 0.35))
        for index, color in ((2, AMBER), (4, BLUE), (6, BLUE), (8, GLOW)):
            g_a[index].set_color(color)
        example_tag = Text("the part 1 example", font_size=22, color=DIM).next_to(
            g_a, DOWN, buff=0.15
        )
        self.say(
            "In part 1, mixing the values 2 and −3 forced the new value\n"
            "at A: the sum over A's neighbours, 2 − 3 − 3 = −4.",
            *self.chapter("Hecke becomes a compatibility condition"),
            FadeIn(icon_a),
            FadeIn(icon_b),
            FadeIn(f_a),
            FadeIn(f_b),
            FadeIn(g_a),
            FadeIn(example_tag),
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
            "HeckeAt states that requirement in general: the target readout g\n"
            "equals the normalized neighbour sum of f, for every certified input.",
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
            ).move_to(p2(x, -1.6))
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
        self.say(
            "heckeTieT carries that condition from the original setup to a\n"
            "copied setup used in the series construction.",
            FadeOut(example_tag),
            FadeIn(frame_a),
            FadeIn(title_a),
            FadeIn(equality_a),
            FadeIn(frame_b),
            FadeIn(title_b),
        )
        self.play(Create(carry), FadeIn(carry_tag), run_time=0.7)
        self.play(FadeIn(equality_b, shift=0.4 * RIGHT), run_time=0.8)
        self.read()
        self.say(
            "The same equality holds in both. In the proof, the Hecke sum\n"
            "specifies a readout that survives transport."
        )
        self.read()
        self.clear_stage()

    # ---------------------------------------------------------------- closing
    def closing(self):
        mass_card, hecke_card = handoff_cards()
        take_mass = lines("Mass identifies\na volume", 32, AMBER, buff=0.14)
        take_mass.next_to(mass_card, UP, buff=0.4)
        take_hecke = lines(
            "Hecke specifies a readout\nthat survives transport", 32, BLUE, buff=0.14
        ).next_to(hecke_card, UP, buff=0.4)
        where_mass = mono("volumes_eq_masses_of_unfold", 16, DIM).next_to(
            mass_card, DOWN, buff=0.25
        )
        where_hecke = mono("HeckeAt, heckeTieT", 16, DIM).next_to(
            hecke_card, DOWN, buff=0.25
        )
        split = lines(
            "The proof applies both formulas to its own data.\n"
            "This repository makes them executable, and tests them\n"
            f"on {FIXTURE_COUNT} shared cases in Lean, C and Rust.",
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
            "The other specifies a readout, and that specification\n"
            "survives transport between setups.",
            FadeIn(take_hecke),
            FadeIn(hecke_card),
            FadeIn(where_hecke),
        )
        self.read()
        self.play(FadeIn(split, shift=0.2 * UP), run_time=0.7)
        self.wait(5.0)
