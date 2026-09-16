import unittest
from io import StringIO

from dna_compare.comparisons.haplogroups import (
    best_sample_haplogroup,
    collapse_mt_haplogroup,
    collapse_y_haplogroup,
    compare_haplogroups,
    score_mt_markers,
    score_y_markers,
)
from dna_compare.config import default_settings
from dna_compare.vcf_parser import parse_vcf

M17_CONFLICT_VCF = """##fileformat=VCFv4.2
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	TEST1
Y	15026424	rs2032624	A	C	.	PASS	.	GT	0
Y	21733165	rs3908	D	I	.	PASS	.	GT	1
Y	14969634	rs2032604	T	G	.	PASS	.	GT	0
"""

R1A1_VCF = """##fileformat=VCFv4.2
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	TEST1
Y	15581983	rs2032658	A	G	.	PASS	.	GT	1
Y	15026424	rs2032624	A	C	.	PASS	.	GT	1
Y	21733165	rs3908	D	I	.	PASS	.	GT	1
"""


class HaplogroupTests(unittest.TestCase):
    def test_collapse_r1a1_and_vellalar_style_labels(self):
        self.assertEqual(collapse_y_haplogroup("R1a1a1"), "R1a1 (M17)")
        self.assertEqual(collapse_y_haplogroup("R1a1a1b2a2~"), "R1a1 (M17)")
        self.assertEqual(collapse_y_haplogroup("L1a1b"), "L (M20)")
        self.assertEqual(collapse_y_haplogroup("J2b2a2b1a~"), "J2 (M172)")
        self.assertIsNone(collapse_y_haplogroup("n/a (female)"))
        self.assertIsNone(collapse_y_haplogroup(".."))

    def test_m17_indel_conflicts_when_m173_ancestral(self):
        _summary, index = parse_vcf(StringIO(M17_CONFLICT_VCF))
        self.assertIn(("Y", 21733165), index)
        calls = {c.marker: c for c in score_y_markers(index)}
        self.assertEqual(calls["M173"].status, "ancestral")
        self.assertEqual(calls["M17"].status, "conflict")
        self.assertIsNone(best_sample_haplogroup(list(calls.values())))

    def test_derived_m17_with_r_and_r1(self):
        _summary, index = parse_vcf(StringIO(R1A1_VCF))
        calls = score_y_markers(index)
        self.assertEqual(best_sample_haplogroup(calls), "R1a1 (M17)")

    def test_compare_includes_aadr_percent_rows_when_anno_present(self):
        settings = default_settings()
        _summary, index = parse_vcf(StringIO(M17_CONFLICT_VCF))
        result = compare_haplogroups(index, settings=settings)
        if not settings.aadr_anno.exists():
            self.skipTest("AADR .anno not present")
        labels = [row.haplogroup for row in result.rows]
        self.assertIn("R1a1 (M17)", labels)
        vellalar = next(row for row in result.rows if row.haplogroup == "R1a1 (M17)").groups["Vellalar"]
        self.assertEqual(vellalar.n, 0)
        self.assertGreater(vellalar.n_called, 0)
        tamil = next(row for row in result.rows if row.haplogroup == "R1a1 (M17)").groups["Tamil"]
        self.assertGreater(tamil.n, 0)

    def test_collapse_mt_takes_first_aadr_token(self):
        self.assertEqual(collapse_mt_haplogroup("M36d;M "), "M36d")
        self.assertEqual(collapse_mt_haplogroup("R8a2"), "R8a2")
        self.assertIsNone(collapse_mt_haplogroup("n/a (<2x)"))
        self.assertIsNone(collapse_mt_haplogroup(".."))

    def test_mt_r_derived_when_m_ancestral(self):
        vcf = """##fileformat=VCFv4.2
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	TEST1
MT	10400	rs28358278	C	T	.	PASS	.	GT	0
MT	12705	R	C	T	.	PASS	.	GT	0
MT	12308	U	A	G	.	PASS	.	GT	0
MT	14766	rs3135031	C	T	.	PASS	.	GT	1
"""
        _summary, index = parse_vcf(StringIO(vcf))
        calls = {c.haplogroup: c for c in score_mt_markers(index)}
        self.assertEqual(calls["M (10400T)"].status, "ancestral")
        self.assertEqual(calls["R (12705C)"].status, "derived")
        self.assertEqual(calls["U (12308G)"].status, "ancestral")
        self.assertEqual(calls["HV (14766C)"].status, "ancestral")
        self.assertEqual(best_sample_haplogroup(list(calls.values()), (
            "R8 (13215C)", "U (12308G)", "M (10400T)", "R (12705C)",
        )), "R (12705C)")

    def test_compare_mt_counts_only_groups_with_anno_calls(self):
        settings = default_settings()
        _summary, index = parse_vcf(StringIO(M17_CONFLICT_VCF))
        result = compare_haplogroups(index, settings=settings)
        if not settings.aadr_anno.exists():
            self.skipTest("AADR .anno not present")
        labels = [row.haplogroup for row in result.mt_rows]
        self.assertIn("R (12705C)", labels)
        self.assertIn("M (10400T)", labels)
        r_row = next(row for row in result.mt_rows if row.haplogroup == "R (12705C)")
        m_row = next(row for row in result.mt_rows if row.haplogroup == "M (10400T)")
        called = [name for name, cell in r_row.groups.items() if cell.n_called]
        self.assertTrue(called)
        self.assertTrue(any("dash means" in note.lower() or "no mt haplogroup" in note.lower() for note in result.mt_notes))
        joined = " ".join(result.status_notes).lower()
        self.assertIn("derived = yes", joined)
        self.assertIn("ancestral = no", joined)
        self.assertIn("no-call", joined)
        self.assertIn("conflict", joined)
        self.assertFalse(any("derived = yes" in (n or "").lower() for n in result.notes + result.mt_notes))
        # Vellalar/VLR is one HO label that happens to have mt filled in.
        if "Vellalar" in r_row.groups and r_row.groups["Vellalar"].n_called:
            self.assertEqual(r_row.groups["Vellalar"].n, 5)
            self.assertEqual(m_row.groups["Vellalar"].n, 4)


if __name__ == "__main__":
    unittest.main()
