"""Document figures (out/figuras/): model rules and the automated print checks.

The end-to-end test renders every figure into a temporary directory and runs the same checks
that tools/generators/figuras.py applies before writing out/figuras: page size, 300 ppp, text of
9 pt or more at insertion width, no split figures, every PNG listed in a README, and intermediate
SVGs free of evidence references, hashes, relationship ids and «Generated» footers.
"""
import copy
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "generators"))

import figuras  # noqa: E402

TOOLS = shutil.which("dot") and shutil.which("java") and (ROOT / "tools" / "plantuml.jar").exists()


def figure(m, fid):
    return next(f for f in m["figures"]["figures"] if f["id"] == fid)


class ModelRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = figuras.models()

    def errors(self, mutate):
        m = copy.deepcopy(self.m)
        mutate(m)
        return "\n".join(figuras.validate(m)[0])

    def test_current_model_is_valid(self):
        errors, specs = figuras.validate(self.m)
        self.assertEqual(errors, [])
        # 15-18 figures as a guide; the owner approved 20 (four class figures and C4 L2 in two).
        self.assertTrue(15 <= len(specs) <= 20, len(specs))

    def test_names_folders_and_orientation(self):
        self.assertIn("part numbers", self.errors(lambda m: figure(m, "clases-ingesta").update(id="clases-ingesta-2")))
        self.assertIn("part numbers", self.errors(lambda m: figure(m, "clases-ingesta").update(id="Clases_Ingesta")))
        self.assertIn("unknown folder", self.errors(lambda m: figure(m, "clases-ingesta").update(folder="99-otras")))
        self.assertIn("landscape is only for Capstone-only figures",
                      self.errors(lambda m: figure(m, "despliegue-dev").update(orientation="landscape")))

    def test_apa_texts(self):
        self.assertIn("must start with", self.errors(lambda m: figure(m, "c4-contexto").update(note="Nota. Algo.")))
        long_note = lambda m: figure(m, "c4-contexto").update(note=figure(m, "c4-contexto")["note"] + " palabra" * 60)
        self.assertIn("max 60", self.errors(long_note))
        url = lambda m: figure(m, "c4-contexto").update(
            note=figure(m, "c4-contexto")["note"] + " https://example.sharepoint.com/x")
        self.assertIn("no URLs", self.errors(url))
        self.assertIn("la Figura N", self.errors(lambda m: figure(m, "c4-contexto").update(call="Una. Dos.")))
        self.assertIn("125 characters", self.errors(lambda m: figure(m, "c4-contexto").update(alt="x" * 126)))
        self.assertIn("sentence case", self.errors(lambda m: figure(m, "c4-contexto").update(title="título.")))

    def test_note_explains_exactly_the_states_drawn(self):
        def drop_amber(m):
            fig = figure(m, "secuencia-diagnostico")
            fig["note"] = fig["note"].replace("ámbar", "gris")
        self.assertIn("«parcial» style", self.errors(drop_amber))

    def test_content_limits(self):
        def too_many_lifelines(m):
            fig = figure(m, "secuencia-inicio-sesion")
            fig["participants"] = fig["participants"] + [dict(fig["participants"][0], id=f"x{i}") for i in range(4)]
        self.assertTrue(self.errors(too_many_lifelines))
        def long_relation(m):
            fig = figure(m, "c4-contexto")
            fig["edges"][0]["label"] = "una relación con muchas más palabras de las permitidas"
        self.assertIn("exceeds", self.errors(long_relation))


@unittest.skipUnless(TOOLS, "Graphviz, Java and tools/plantuml.jar are required to render the figures")
class RenderedFigureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="pipesor-figuras-"))
        cls.out, cls.build = cls.tmp / "out" / "figuras", cls.tmp / "build" / "figuras"
        cls.rows = figuras.generate(cls.out, cls.build)
        cls.doc = figuras.models()["figures"]

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def copy(self):
        target = Path(tempfile.mkdtemp(prefix="pipesor-figuras-copy-", dir=self.tmp))
        shutil.copytree(self.out, target / "out")
        shutil.copytree(self.build, target / "build")
        return target / "out", target / "build"

    def test_every_figure_fits_one_page_at_300_ppp_and_9_points(self):
        self.assertEqual(figuras.check_outputs(self.doc, self.out, self.build), [])
        self.assertEqual(len(self.rows), len(self.doc["figures"]))
        for fid, row in self.rows.items():
            with self.subTest(figure=fid):
                width, height = figuras.PAGES[row["orientation"]]
                self.assertLessEqual(row["width_cm"], width + 1e-6)
                self.assertLessEqual(row["height_cm"], height + 1e-6)
                self.assertGreaterEqual(round(row["min_pt"], 1), figuras.MIN_POINTS)
                self.assertEqual(figuras.png_info(row["png"])[2], figuras.PNG_DPI)

    def test_only_png_and_readme_in_each_folder(self):
        for path in self.out.rglob("*"):
            if path.is_file():
                self.assertIn(path.suffix, {".png", ".md"}, path)
                if path.suffix == ".md":
                    self.assertEqual(path.name, "README.md")
        for folder in self.doc["folders"]:
            self.assertTrue((self.out / folder / "README.md").is_file(), folder)

    def test_checks_catch_violations(self):
        out, build = self.copy()
        png = next(out.rglob("clases-ingesta.png"))
        figuras.set_png_dpi(png, 96)
        shutil.copy(png, png.with_name("clases-ingesta-2.png"))
        (out / "suelta.svg").write_text("<svg/>", encoding="utf-8")
        svg = next(build.rglob("c4-contexto.svg"))
        svg.write_text(svg.read_text(encoding="utf-8").replace("</svg>", "<text>repo:a.java:1 rel_x 0d34716</text></svg>"),
                       encoding="utf-8")
        readme = out / "05-secuencias" / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8").replace("(secuencia-diagnostico.png)", "(x.png)"),
                          encoding="utf-8")
        errors = "\n".join(figuras.check_outputs(self.doc, out, build))
        for expected in ("96 ppp instead of 300", "PNG set differs", "must not contain SVG", "'repo:'", "'rel_'",
                         "secuencia-diagnostico.png: no entry"):
            self.assertIn(expected, errors)

    def test_small_text_is_rejected(self):
        out, build = self.copy()
        svg = next(build.rglob("datos-conocimiento.svg"))
        text = svg.read_text(encoding="utf-8")
        svg.write_text(text.replace("</svg>", '<text font-size="4">diminuto</text></svg>'), encoding="utf-8")
        self.assertIn("datos-conocimiento.png: smallest text", "\n".join(figuras.check_outputs(self.doc, out, build)))


if __name__ == "__main__":
    unittest.main()
