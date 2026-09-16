from __future__ import annotations

from dna_compare.comparisons.populations import compare_populations
from dna_compare.config import Settings
from dna_compare.models import ComparisonBlock


def compare_caste(
    query_index: dict[tuple[str, int], dict],
    *,
    panel,
    settings: Settings,
) -> ComparisonBlock:
    return compare_populations(
        query_index,
        panel=panel,
        settings=settings,
        groups=settings.caste_groups(),
        kind="caste",
    )
