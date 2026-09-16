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
class HaplogroupMarkerCall:
    haplogroup: str
    marker: str
    rsid: str
    chrom: str
    pos: int
    ancestral: str
    derived: str
    observed: str | None
    status: str
    genotype: str | None = None
    backbone: bool = True
    qual: float | None = None
    gq: int | None = None
    dp: int | None = None
    igc: float | None = None
    ad: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HaplogroupGroupCount:
    n: int
    n_called: int
    percent: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HaplogroupRow:
    haplogroup: str
    marker: str
    sample_status: str
    groups: dict[str, HaplogroupGroupCount] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "haplogroup": self.haplogroup,
            "marker": self.marker,
            "sample_status": self.sample_status,
            "groups": {name: item.to_dict() for name, item in self.groups.items()},
        }


@dataclass
class HaplogroupResult:
    available: bool
    sample_best: str | None = None
    markers: list[HaplogroupMarkerCall] = field(default_factory=list)
    rows: list[HaplogroupRow] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    mt_available: bool = False
    mt_sample_best: str | None = None
    mt_markers: list[HaplogroupMarkerCall] = field(default_factory=list)
    mt_rows: list[HaplogroupRow] = field(default_factory=list)
    mt_notes: list[str] = field(default_factory=list)
    status_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "available": self.available,
            "sample_best": self.sample_best,
            "markers": [item.to_dict() for item in self.markers],
            "rows": [item.to_dict() for item in self.rows],
            "notes": self.notes,
            "mt_available": self.mt_available,
            "mt_sample_best": self.mt_sample_best,
            "mt_markers": [item.to_dict() for item in self.mt_markers],
            "mt_rows": [item.to_dict() for item in self.mt_rows],
            "mt_notes": self.mt_notes,
            "status_notes": self.status_notes,
        }


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
    haplogroups: HaplogroupResult
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
            "haplogroups": self.haplogroups.to_dict(),
            "errors": self.errors,
        }
