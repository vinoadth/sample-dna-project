import unittest
from io import BytesIO
from pathlib import Path

from dna_compare.models import AnalysisResult
from dna_compare.service import AnalysisService
from dna_compare.vcf_parser import parse_vcf

FIXTURE = Path(__file__).resolve().parents[1] / "data" / "samples" / "demo.snps.vcf"


class VcfAndApiTests(unittest.TestCase):
    def test_parse_skips_indels_and_normalizes_chrom(self):
        summary, index = parse_vcf(FIXTURE)
        self.assertEqual(summary.sample_id, "DEMO1")
        self.assertEqual(summary.n_snps, 7)
        self.assertEqual(summary.n_non_snp_skipped, 1)
        self.assertIn(("1", 752566), index)
        self.assertIn(("3", 12345), index)
        self.assertEqual(index[("1", 752566)]["dosage_alt"], 1.0)
        self.assertEqual(index[("1", 891021)]["dosage_alt"], 2.0)
        self.assertEqual(summary.preview[0].rsid, "rs3094315")

    def test_parse_from_bytes_for_future_api_upload(self):
        payload = FIXTURE.read_bytes()
        summary, index = parse_vcf(BytesIO(payload), preview_limit=3)
        self.assertEqual(summary.n_snps, 7)
        self.assertEqual(len(summary.preview), 3)
        self.assertIn(("X", 2699624), index)

    def test_analyze_json_shape(self):
        service = AnalysisService()
        result = service.analyze(
            FIXTURE,
            filename="demo.snps.vcf",
            compare_hominin_flag=False,
            compare_caste_flag=False,
            compare_populations_flag=False,
            compare_ancestry_flag=False,
        )
        self.assertIsInstance(result, AnalysisResult)
        payload = result.to_dict()
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["source_filename"], "demo.snps.vcf")
        self.assertIn("preview", payload["vcf"])
        self.assertEqual(payload["hominin"]["kind"], "hominin")
        self.assertEqual(payload["caste"]["kind"], "caste")
        self.assertEqual(payload["populations"]["kind"], "populations")
        self.assertEqual(payload["ancestry"]["kind"], "ancestry")

    def test_ancestry_aadr_labels_exist(self):
        from dna_compare.config import ANCESTRY_AADR_POPS, default_settings
        from dna_compare.eigenstrat import AadrPanel

        panel = AadrPanel(default_settings())
        if not panel.available:
            self.skipTest("AADR HO panel not present")
        present = {rec.population for rec in panel.inds()}
        for label, pops in ANCESTRY_AADR_POPS.items():
            self.assertTrue(any(pop in present for pop in pops), f"{label} missing {pops}")


if __name__ == "__main__":
    unittest.main()
