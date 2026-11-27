"""Document figures must stay legible at the size they declare for print."""

from pathlib import Path
import re
import shutil
import struct
import tempfile
import unittest
import xml.etree.ElementTree as ET

from tools.generators import document_figures as doc

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out" / "doc"


def chunks(png):
    data = png.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    offset, found = 8, {}
    while offset < len(data):
        length, kind = struct.unpack(">I4s", data[offset:offset + 8])
        found.setdefault(kind, data[offset + 8:offset + 8 + length])
        offset += 12 + length
    return found


def printed(svg):
    """Smallest printed text (pt) and printed size (cm) of a committed figure."""
    root = ET.parse(svg).getroot()
    width_cm, height_cm = (float(root.get(k).removesuffix("cm")) for k in ("width", "height"))
    view_width = float(root.get("viewBox").split()[2])
    sizes = [float(el.get("font-size")) for el in root.iter()
             if el.tag.endswith("text") and el.get("font-size") and "".join(el.itertext()).strip()]
    return min(sizes) * width_cm / 2.54 * 72 / view_width, width_cm, height_cm


class DocumentFigureTests(unittest.TestCase):
    def test_every_presentation_and_component_view_has_a_document_figure(self):
        expected = {"logica_expo_01", "logica_expo_02", "logica_expo_03", "fisica_expo_01", "fisica_expo_02",
                    "fisica_expo_03", "c4_expo_2a", "c4_expo_2b", "c4_context", "c4_component_diagnostic",
                    # The Ingestion component view prints in two parts (model/c4_presentation.yml print_parts).
                    "c4_component_ingestion_capture", "c4_component_ingestion_identity"}
        self.assertEqual({f.id for f in doc.figures()}, expected)
        for fid in expected:
            self.assertTrue((OUT / f"{fid}.svg").is_file(), fid)
            self.assertTrue((OUT / f"{fid}.png").is_file(), fid)
        self.assertTrue((OUT / "guia_figuras.md").is_file())

    def test_committed_figures_print_at_least_eight_points_within_a4(self):
        for svg in sorted(OUT.glob("*.svg")):
            smallest, width_cm, height_cm = printed(svg)
            self.assertGreaterEqual(round(smallest, 1), doc.MIN_POINTS, svg.name)
            page = "portrait" if width_cm <= doc.PAGES["portrait"][0] and height_cm <= doc.PAGES["portrait"][1] \
                else "landscape"
            self.assertLessEqual(width_cm, doc.PAGES[page][0] + 0.01, svg.name)
            self.assertLessEqual(height_cm, doc.PAGES[page][1] + 0.01, svg.name)

    def test_png_declares_300_dpi_and_matches_the_printed_width(self):
        for png in sorted(OUT.glob("*.png")):
            found = chunks(png)
            ppm_x, ppm_y, unit = struct.unpack(">IIB", found[b"pHYs"])
            self.assertEqual((ppm_x, ppm_y, unit), (11811, 11811, 1), png.name)
            pixels = struct.unpack(">I", found[b"IHDR"][:4])[0]
            _, width_cm, _ = printed(png.with_suffix(".svg"))
            self.assertAlmostEqual(pixels / doc.PNG_DPI * 2.54, width_cm, delta=0.15, msg=png.name)

    def test_selection_prefers_a_self_contained_legible_figure(self):
        inside = (("portrait", "TB", 2, "label"), 0.6, 15.9, 21.0, 8.1)
        outside = (("landscape", "TB", 0, "label"), 0.8, 20.0, 13.0, 9.5)
        free = (("portrait", "TB", 2, "xlabel"), 0.7, 15.9, 20.0, 8.6)
        too_small = (("portrait", "LR", 2, "label"), 0.3, 15.9, 8.0, 4.0)
        self.assertEqual(doc.choose("x", [outside, free, inside, too_small]), inside)
        self.assertEqual(doc.choose("x", [outside, too_small]), outside)
        with self.assertRaisesRegex(ValueError, "no layout reaches 8.0 pt"):
            doc.choose("x", [too_small])

    def test_c4_document_variant_keeps_curated_layout_without_slide_chrome(self):
        presentation, architecture = doc.logical.load_models(doc.c4_expo.MODEL)
        view, projection = doc.c4_expo.prepare(presentation, architecture)[0]
        slide = doc.c4_expo.generate_dot(presentation, architecture, view, projection)
        printable = doc.c4_expo.generate_dot(presentation, architecture, view, projection, document=True)
        for chrome in ("slide_title", "slide_subtitle", "relation_legend", "slide_footer", "slide_note"):
            self.assertIn(chrome, slide)
            self.assertNotIn(chrome, printable)
        def positions(source):
            found = dict(re.findall(r'\t(\w+) \[label=<.*?pos="([\d.,!]+)"', source))
            return {eid: found[eid] for eid in view["positions"]}
        self.assertEqual(positions(printable), positions(slide))
        self.assertNotIn('POINT-SIZE="12"', printable)

    def test_render_writes_only_to_the_given_directories(self):
        figure = next(f for f in doc.figures() if f.id == "logica_expo_02")
        with tempfile.TemporaryDirectory() as directory:
            out, build = Path(directory) / "out", Path(directory) / "build"
            page, columns, width_cm, height_cm, smallest = doc.render(figure, out, build)
            self.assertEqual(sorted(p.name for p in out.iterdir()), ["logica_expo_02.png", "logica_expo_02.svg"])
            self.assertGreaterEqual(smallest, doc.MIN_POINTS)
            self.assertEqual(chunks(out / "logica_expo_02.png")[b"pHYs"][:4], struct.pack(">I", 11811))

    def test_set_png_dpi_replaces_an_existing_density(self):
        with tempfile.TemporaryDirectory() as directory:
            png = Path(directory) / "figure.png"
            shutil.copy(OUT / "logica_expo_02.png", png)
            doc.set_png_dpi(png, 150)
            self.assertEqual(struct.unpack(">IIB", chunks(png)[b"pHYs"]), (5906, 5906, 1))
            doc.set_png_dpi(png, 300)
            data = png.read_bytes()
            self.assertEqual(data.count(b"pHYs"), 1)


if __name__ == "__main__":
    unittest.main()
