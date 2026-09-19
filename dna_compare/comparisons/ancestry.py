from __future__ import annotations

import numpy as np

from dna_compare.comparisons.populations import _query_allele1_freq
from dna_compare.comparisons.qpadm import qpadm_weights
from dna_compare.config import Settings
from dna_compare.models import ComparisonBlock, PopulationEstimate

ANCESTRY_NOTES = [
    "qpAdm-style 3-source mix on overlapping Human Origins SNPs using f4 statistics and outgroups.",
    "Steppe_MLBA is Sintashta (the usual South Asian Steppe proxy). Indus_Periphery is Shahr-i Sokhta BA. AASI_Onge is Andamanese Onge, a stand-in for South Asian hunter-gatherer-related ancestry.",
    "Bars are one model that sums to 100%. Not a date, not qpAdm from ADMIXTOOLS2, and not every SNP in the VCF.",
]

ANCESTRY_5_NOTES = [
    "qpAdm-style 5-source mix: the 3 South Asian sources plus Anatolia_N (Turkey_N / Barcin-related farmer) and East_Asian (Dai).",
    "Han and French are left out of this model's outgroups so they do not sit on both sides of the f4 equations.",
    "For most Tamil / South Indian kits East_Asian and Anatolia_N should be small. A large leftover there means the 3-source bars are absorbing something else.",
    "A second model that also sums to 100%. Not ADMIXTOOLS2, not a date, and not every SNP in the VCF.",
]


def _load_freq(panel, pops: tuple[str, ...], notes: list[str], label: str) -> np.ndarray | None:
    try:
        return panel.population_allele1_freq(pops)
    except KeyError:
        notes.append(f"No AADR samples for {label} ({', '.join(pops)})")
        return None


def _aligned_columns(
    query_index: dict[tuple[str, int], dict],
    panel,
    freq_arrays: list[np.ndarray],
) -> tuple[np.ndarray, list[np.ndarray]]:
    target: list[float] = []
    columns: list[list[float]] = [[] for _ in freq_arrays]
    for snp in panel.snps():
        row = query_index.get((snp.chrom, snp.pos))
        if row is None:
            continue
        qv = _query_allele1_freq(row, snp.allele1, snp.allele2)
        if qv is None:
            continue
        vals = [float(freq[snp.index]) for freq in freq_arrays]
        if any(not np.isfinite(val) for val in vals):
            continue
        target.append(qv)
        for i, val in enumerate(vals):
            columns[i].append(val)
    return np.asarray(target, dtype=float), [np.asarray(col, dtype=float) for col in columns]


def _fit_ancestry_model(
    query_index: dict[tuple[str, int], dict],
    *,
    panel,
    groups: dict[str, tuple[str, ...]],
    right_pops: tuple[str, ...],
    kind: str,
    notes: list[str],
) -> ComparisonBlock:
    if panel is None or not panel.available:
        return ComparisonBlock(
            kind=kind,
            available=False,
            notes=["AADR HO panel not found under data/references/aadr/."],
        )

    source_freqs: list[np.ndarray] = []
    kept_labels: list[str] = []
    for label, pops in groups.items():
        freq = _load_freq(panel, pops, notes, label)
        if freq is not None:
            source_freqs.append(freq)
            kept_labels.append(label)
    if len(kept_labels) < 2:
        return ComparisonBlock(kind=kind, available=False, notes=notes)

    right_labels: list[str] = []
    right_freqs: list[np.ndarray] = []
    for pop in right_pops:
        freq = _load_freq(panel, (pop,), notes, pop)
        if freq is not None:
            right_freqs.append(freq)
            right_labels.append(pop)
    if len(right_freqs) < 3:
        return ComparisonBlock(
            kind=kind,
            available=False,
            notes=notes + ["Need at least three outgroup populations for qpAdm-style f4."],
        )

    all_freqs = source_freqs + right_freqs
    target, aligned = _aligned_columns(query_index, panel, all_freqs)
    n_used = int(target.size)
    if n_used < 50:
        return ComparisonBlock(
            kind=kind,
            available=False,
            notes=notes + [f"Only {n_used} overlapping SNPs; need a denser SNP VCF."],
        )

    src = aligned[: len(source_freqs)]
    rights = aligned[len(source_freqs) :]
    raw, weights, rss = qpadm_weights(target, src, rights)
    notes.append("Outgroups: " + ", ".join(right_labels) + f". f4 residual RMS={rss:.4e}.")
    if np.any(raw < -0.02):
        notes.append(
            "Raw qpAdm-style weights included a negative component "
            f"({', '.join(f'{lab}={val:.3f}' for lab, val in zip(kept_labels, raw))}); "
            "percentages are clipped to non-negative and rescaled to 100%."
        )

    estimates = []
    for label, pct, col in zip(kept_labels, weights, src):
        ibs = 1.0 - float(np.mean(np.abs(target - col)))
        estimates.append(
            PopulationEstimate(
                population=label,
                percent=round(float(pct) * 100.0, 3),
                n_snps=n_used,
                mean_ibs=round(ibs, 4),
            )
        )
    estimates.sort(key=lambda item: item.percent, reverse=True)
    return ComparisonBlock(kind=kind, available=True, estimates=estimates, notes=notes)


def compare_ancestry(
    query_index: dict[tuple[str, int], dict],
    *,
    panel,
    settings: Settings,
) -> ComparisonBlock:
    return _fit_ancestry_model(
        query_index,
        panel=panel,
        groups=settings.ancestry_groups(),
        right_pops=settings.ancestry_right_pops,
        kind="ancestry",
        notes=list(ANCESTRY_NOTES),
    )


def compare_ancestry_5source(
    query_index: dict[tuple[str, int], dict],
    *,
    panel,
    settings: Settings,
) -> ComparisonBlock:
    return _fit_ancestry_model(
        query_index,
        panel=panel,
        groups=settings.ancestry_5_groups(),
        right_pops=settings.ancestry_5_right_pops,
        kind="ancestry_5",
        notes=list(ANCESTRY_5_NOTES),
    )
