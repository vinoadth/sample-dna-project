from __future__ import annotations

import numpy as np

from dna_compare.config import Settings
from dna_compare.models import ComparisonBlock, PopulationEstimate


def _query_allele1_freq(row: dict, allele1: str, allele2: str) -> float | None:
    dosage = row.get("dosage_alt")
    if dosage is None:
        return None
    q_ref, q_alt = row["ref"].upper(), row["alt"].upper()
    allele1, allele2 = allele1.upper(), allele2.upper()
    copies = 2.0
    gt = row.get("genotype") or ""
    if gt and "/" not in gt and "|" not in gt:
        copies = 1.0
    q_alt_freq = dosage / copies
    if q_ref == allele2 and q_alt == allele1:
        return q_alt_freq
    if q_ref == allele1 and q_alt == allele2:
        return 1.0 - q_alt_freq
    return None


def _nnls_percentages(F: np.ndarray, q: np.ndarray) -> np.ndarray:
    weights, *_ = np.linalg.lstsq(F, q, rcond=None)
    weights = np.clip(weights, 0.0, None)
    total = float(weights.sum())
    if total <= 0:
        return np.zeros(F.shape[1])
    return 100.0 * weights / total


def compare_populations(
    query_index: dict[tuple[str, int], dict],
    *,
    panel,
    settings: Settings,
    groups: dict[str, tuple[str, ...]] | None = None,
    kind: str = "populations",
) -> ComparisonBlock:
    notes = [
        "Percentages are mixture weights on overlapping Human Origins SNPs from AADR v66.1, "
        "not ethnic, national, or caste identity."
    ]
    if panel is None or not panel.available:
        return ComparisonBlock(
            kind=kind,
            available=False,
            notes=["AADR HO panel not found under data/references/aadr/."],
        )
    groups = groups if groups is not None else settings.selected_population_groups()
    if not groups:
        return ComparisonBlock(kind=kind, available=False, notes=["No population packs selected."])

    snps = panel.snps()
    labels: list[str] = []
    pop_freqs: list[np.ndarray] = []
    for label, aadr_pops in groups.items():
        try:
            pop_freqs.append(panel.population_allele1_freq(aadr_pops))
            labels.append(label)
        except KeyError:
            notes.append(f"No AADR samples for {label} ({', '.join(aadr_pops)})")

    if not labels:
        return ComparisonBlock(kind=kind, available=False, notes=notes)

    q_vals: list[float] = []
    columns: list[list[float]] = [[] for _ in labels]
    for snp in snps:
        row = query_index.get((snp.chrom, snp.pos))
        if row is None:
            continue
        qv = _query_allele1_freq(row, snp.allele1, snp.allele2)
        if qv is None:
            continue
        freqs = [float(freq[snp.index]) for freq in pop_freqs]
        if any(not np.isfinite(val) for val in freqs):
            continue
        q_vals.append(qv)
        for i, val in enumerate(freqs):
            columns[i].append(val)

    n_used = len(q_vals)
    if n_used < 50:
        return ComparisonBlock(
            kind=kind,
            available=False,
            notes=notes + [f"Only {n_used} overlapping SNPs; need a denser SNP VCF."],
        )

    F = np.column_stack([np.asarray(col, dtype=float) for col in columns])
    q = np.asarray(q_vals, dtype=float)
    percents = _nnls_percentages(F, q)
    estimates = []
    for label, pct, col in zip(labels, percents, columns):
        ibs = 1.0 - float(np.mean(np.abs(q - np.asarray(col))))
        estimates.append(
            PopulationEstimate(
                population=label,
                percent=round(float(pct), 3),
                n_snps=n_used,
                mean_ibs=round(ibs, 4),
            )
        )
    estimates.sort(key=lambda item: item.percent, reverse=True)
    return ComparisonBlock(kind=kind, available=True, estimates=estimates, notes=notes)
