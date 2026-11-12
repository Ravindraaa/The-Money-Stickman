import sys
import unittest
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "production" / "scripts"))
from compile_storyboard import compile_beats, split_script, classify
from scene_renderer import build_hyperframes


class StoryboardCompilerTests(unittest.TestCase):
    def test_chunks_respect_word_limit(self):
        chunks = split_script("Your paycheck arrives. Rent is expensive. Save money every payday.", 5)
        self.assertTrue(chunks)
        self.assertTrue(all(len(chunk.split()) <= 5 for chunk in chunks))

    def test_finance_topics_are_classified(self):
        self.assertEqual(classify("Credit card debt keeps growing."), "debt")
        self.assertEqual(classify("Move money into savings."), "savings")
        self.assertEqual(classify("Rent and utility bills add up."), "bills")

    def test_compiler_preserves_script_words(self):
        script = "Your paycheck arrives. Save money before you spend."
        beats = compile_beats(script, 6)
        compiled = " ".join(item["text"] for item in beats)
        self.assertEqual(compiled, script)

    def test_beats_have_unique_ids_and_visual_metadata(self):
        beats = compile_beats("Money grows. Avoid the debt trap. Build your savings.", 5)
        ids = [item["id"] for item in beats]
        self.assertEqual(len(ids), len(set(ids)))
        for item in beats:
            self.assertTrue(item["kind"])
            self.assertTrue(item["icon"])
            self.assertTrue(item["accent"])
            self.assertTrue(item["action"])

    def test_scene_renderer_builds_timed_hyperframes_compositions(self):
        beats = compile_beats("Credit card debt. Save money every payday.", 5)
        beats[0]["duration"] = 2.4
        beats[1]["duration"] = 2.7
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            total = build_hyperframes(beats, output)
            index = (output / "index.html").read_text(encoding="utf-8")
            scene = (output / "compositions" / "beat-001.html").read_text(encoding="utf-8")
            self.assertAlmostEqual(total, 5.1, places=3)
            self.assertIn('data-start="2.4000"', index)
            self.assertIn('data-duration="2.7000"', index)
            self.assertIn('gsap.timeline', scene)
            self.assertIn('class="stickman"', scene)
            self.assertIn('data-width="1080"', scene)


if __name__ == "__main__":
    unittest.main()
