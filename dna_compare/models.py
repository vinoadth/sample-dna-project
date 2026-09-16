from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class VariantRow:
    chrom: str
    pos: int
    rsid: str
    ref: str
    alt: str
    genotype: str
    dosage_alt: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class VcfSummary:
    sample_id: str
    n_records: int
    n_snps: int
    n_non_snp_skipped: int
    n_samples_in_file: int
    chrom_counts: dict[str, int] = field(default_factory=dict)
    preview: list[VariantRow] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sample_id": self.sample_id,
            "n_records": self.n_records,
            "n_snps": self.n_snps,
            "n_non_snp_skipped": self.n_non_snp_skipped,
            "n_samples_in_file": self.n_samples_in_file,
            "chrom_counts": self.chrom_counts,
            "preview": [row.to_dict() for row in self.preview],
        }


@dataclass
class ReferenceStatus:
    key: str
    filename: str
    present: bool
    path: str | None = None
    note: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HomininEstimate:
    label: str
    method: str
    percent: float | None
    n_snps: int
    detail: dict[str, Any] = field(default_factory=dict)
    available: bool = True
    message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        return payload


@dataclass
class PopulationEstimate:
    population: str
    percent: float
    n_snps: int
    mean_ibs: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


CasteEstimate = PopulationEstimate


@dataclass
class ComparisonBlock:
    kind: str
    available: bool
    estimates: list[Any] = field(default_factory=list)
    missing_files: list[ReferenceStatus] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "available": self.available,
            "estimates": [item.to_dict() for item in self.estimates],
            "missing_files": [item.to_dict() for item in self.missing_files],
            "notes": self.notes,
        }


@dataclass
class AnalysisResult:
    """JSON-serializable payload for a future POST /analyze API and HTML UI."""

    ok: bool
    source_filename: str
    vcf: VcfSummary | None
    hominin: ComparisonBlock
    caste: ComparisonBlock
    populations: ComparisonBlock
    ancestry: ComparisonBlock
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "source_filename": self.source_filename,
            "vcf": None if self.vcf is None else self.vcf.to_dict(),
            "hominin": self.hominin.to_dict(),
            "caste": self.caste.to_dict(),
            "populations": self.populations.to_dict(),
            "ancestry": self.ancestry.to_dict(),
            "errors": self.errors,
        }
