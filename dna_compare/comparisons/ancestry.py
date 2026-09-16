from __future__ import annotations

from dna_compare.comparisons.populations import compare_populations
from dna_compare.config import Settings
from dna_compare.models import ComparisonBlock

ANCESTRY_NOTES = [
    "Least-squares mix of overlapping Human Origins SNPs against deep AADR sources — not qpAdm and not a date.",
    "Steppe_Yamnaya / Steppe_Sintashta are Bronze Age pastoralist proxies. Iran_Neolithic and Indus_Periphery are farmer / IVC-related. AASI_Onge is an Andamanese proxy for South Asian hunter-gatherer-related ancestry.",
    "These weights are a separate model from the caste and population charts.",
]


def compare_ancestry(
    query_index: dict[tuple[str, int], dict],
    *,
    panel,
    settings: Settings,
) -> ComparisonBlock:
    block = compare_populations(
        query_index,
        panel=panel,
        settings=settings,
        groups=settings.ancestry_groups(),
        kind="ancestry",
    )
    extras = [note for note in block.notes if note.startswith("No AADR") or note.startswith("Only ")]
    block.notes = ANCESTRY_NOTES + extras
    return block
