from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from dna_compare.config import Settings, TAMIL_COMMUNITY_REF
from dna_compare.models import CommunityRefMatch, ComparisonBlock, HaplogroupResult

TAMIL_HO_LABELS = {"Tamil", "Vellalar", "Irula"}
FILENAME_HINTS = (
    "tamil",
    "vellalar",
    "iyer",
    "iyengar",
    "nadar",
    "thevar",
    "mukkulathor",
    "vanniyar",
    "gounder",
    "paraiyar",
    "parayar",
    "irula",
    "pillai",
    "chennai",
    "madurai",
    "coimbatore",
    "stu",
)

NOTES = [
    "Fit uses this file's qpAdm-style AASI_Onge and Steppe_MLBA against published Tamil-community ranges.",
    "The table's AASI/ASI column is not the same quantity as AASI_Onge (Onge is a hunter-gatherer proxy; ASI often includes Iran/IVC).",
    "ANI/Steppe is compared to Steppe_MLBA (Sintashta). Inside the published range scores higher.",
    "Y percentages in the table are community frequencies. One person has one Y haplogroup; an uncalled or conflicting Y is left out of the fit.",
    "This is a reference-table overlay, not a caste assignment and not an AADR HO bar.",
]

_Y_ALIASES = (
    ("R1a", "R1a"),
    ("H-M69", "H-M69"),
    ("H (M69)", "H-M69"),
    ("H1", "H-M69"),
    ("H3", "H-M69"),
    ("L-M20", "L-M20"),
    ("L (M20)", "L-M20"),
    ("L1", "L-M20"),
    ("L3", "L-M20"),
    ("J2", "J2"),
    ("R2", "R2"),
    ("C-M130", "C-M130"),
    ("C (M130)", "C-M130"),
    ("O-M175", "O-M175"),
    ("O", "O-M175"),
)


@dataclass(frozen=True)
class CommunityRefRow:
    community_id: str
    display_name: str
    aasi_min: float
    aasi_max: float
    steppe_min: float
    steppe_max: float
    y_haplogroups: dict[str, float]
    note: str


def collapse_ref_y(label: str | None) -> str | None:
    text = (label or "").strip()
    if not text or text.lower() == "other":
        return None
    for prefix, key in _Y_ALIASES:
        if text == prefix or text.startswith(prefix):
            return key
    if text.startswith("H"):
        return "H-M69"
    if text.startswith("L"):
        return "L-M20"
    return None


def interval_score(value: float | None, lo: float, hi: float) -> float | None:
    if value is None:
        return None
    if lo <= value <= hi:
        return 1.0
    dist = lo - value if value < lo else value - hi
    return max(0.0, 1.0 - dist / 15.0)


def parse_y_haplogroups(raw: str) -> dict[str, float]:
    out: dict[str, float] = {}
    for part in (raw or "").split(";"):
        token = part.strip()
        if not token or ":" not in token:
            continue
        name, pct = token.split(":", 1)
        key = collapse_ref_y(name.strip()) or name.strip()
        out[key] = float(pct)
    return out


def load_tamil_community_reference(path: Path | None = None) -> list[CommunityRefRow]:
    src = path or TAMIL_COMMUNITY_REF
    if not src.exists():
        return []
    rows: list[CommunityRefRow] = []
    with src.open(encoding="utf-8") as handle:
        header = handle.readline()
        if not header:
            return []
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            cols = line.rstrip("\n").split("\t")
            if len(cols) < 7:
                continue
            rows.append(
                CommunityRefRow(
                    community_id=cols[0].strip(),
                    display_name=cols[1].strip(),
                    aasi_min=float(cols[2]),
                    aasi_max=float(cols[3]),
                    steppe_min=float(cols[4]),
                    steppe_max=float(cols[5]),
                    y_haplogroups=parse_y_haplogroups(cols[6]),
                    note=cols[7].strip() if len(cols) > 7 else "",
                )
            )
    return rows


def _ancestry_pct(ancestry: ComparisonBlock | None, name: str) -> float | None:
    if ancestry is None:
        return None
    for est in ancestry.estimates:
        label = getattr(est, "population", None) or (est.get("population") if isinstance(est, dict) else None)
        if label == name:
            return float(getattr(est, "percent", est.get("percent") if isinstance(est, dict) else 0))
    return None


def _estimate_label(est) -> str:
    if isinstance(est, dict):
        return str(est.get("population") or est.get("label") or "")
    return str(getattr(est, "population", None) or getattr(est, "label", "") or "")


def _estimate_percent(est) -> float:
    if isinstance(est, dict):
        return float(est.get("percent") or 0)
    return float(getattr(est, "percent", 0) or 0)


def tamil_reference_applicable(
    caste: ComparisonBlock | None,
    filename: str | None = None,
) -> bool:
    """Show the Tamil range table only for Tamil-looking files."""
    name = (filename or "").lower()
    if any(hint in name for hint in FILENAME_HINTS):
        return True
    if caste is None or not caste.available or not caste.estimates:
        return False
    ranked = sorted(caste.estimates, key=_estimate_percent, reverse=True)
    top = {_estimate_label(est) for est in ranked[:2]}
    if top & TAMIL_HO_LABELS:
        return True
    tamil_share = sum(_estimate_percent(est) for est in ranked if _estimate_label(est) in TAMIL_HO_LABELS)
    return tamil_share >= 25.0


def score_community_reference(
    ancestry: ComparisonBlock | None,
    haplogroups: HaplogroupResult | None,
    *,
    caste: ComparisonBlock | None = None,
    filename: str | None = None,
    settings: Settings | None = None,
) -> ComparisonBlock:
    if not tamil_reference_applicable(caste, filename):
        return ComparisonBlock(
            kind="community_ref",
            available=False,
            hidden=True,
            notes=["Tamil community ranges hidden: this file does not look Tamil-related (filename or top HO labels)."],
        )
    path = settings.tamil_community_ref if settings is not None else TAMIL_COMMUNITY_REF
    refs = load_tamil_community_reference(path)
    notes = list(NOTES)
    if not refs:
        return ComparisonBlock(
            kind="community_ref",
            available=False,
            notes=notes + [f"Reference table not found: {path}"],
        )
    sample_aasi = _ancestry_pct(ancestry, "AASI_Onge")
    sample_steppe = _ancestry_pct(ancestry, "Steppe_MLBA")
    if sample_aasi is None and sample_steppe is None:
        return ComparisonBlock(
            kind="community_ref",
            available=False,
            notes=notes + ["Need the ancestry comparison to score this table."],
        )
    sample_y = haplogroups.sample_best if haplogroups is not None else None
    sample_y_key = collapse_ref_y(sample_y)
    matches: list[CommunityRefMatch] = []
    n_snps = 0
    if ancestry is not None:
        for est in ancestry.estimates:
            n_snps = int(getattr(est, "n_snps", 0) or 0)
            if n_snps:
                break
    for row in refs:
        aasi_score = interval_score(sample_aasi, row.aasi_min, row.aasi_max)
        steppe_score = interval_score(sample_steppe, row.steppe_min, row.steppe_max)
        y_score = None
        y_note = "Y not used (no derived backbone call in this VCF)."
        if sample_y_key:
            typical = row.y_haplogroups.get(sample_y_key)
            if typical is not None:
                y_score = min(1.0, typical / 25.0)
                y_note = f"Sample {sample_y} maps to {sample_y_key} (table ~{typical:.0f}%)."
            else:
                y_score = 0.0
                y_note = f"Sample {sample_y} is not among this row's listed Y haplogroups."
        parts: list[tuple[float, float]] = []
        if steppe_score is not None:
            parts.append((steppe_score, 0.6 if y_score is None else 0.5))
        if aasi_score is not None:
            parts.append((aasi_score, 0.4 if y_score is None else 0.35))
        if y_score is not None:
            parts.append((y_score, 0.15))
        weight = sum(w for _s, w in parts) or 1.0
        fit = 100.0 * sum(score * w for score, w in parts) / weight
        matches.append(
            CommunityRefMatch(
                population=row.display_name,
                percent=round(fit, 1),
                n_snps=n_snps,
                aasi_in_range=bool(sample_aasi is not None and row.aasi_min <= sample_aasi <= row.aasi_max),
                steppe_in_range=bool(
                    sample_steppe is not None and row.steppe_min <= sample_steppe <= row.steppe_max
                ),
                aasi_score=None if aasi_score is None else round(aasi_score, 3),
                steppe_score=None if steppe_score is None else round(steppe_score, 3),
                y_score=None if y_score is None else round(y_score, 3),
                sample_aasi=sample_aasi,
                sample_steppe=sample_steppe,
                ref_aasi=f"{row.aasi_min:.0f}–{row.aasi_max:.0f}%",
                ref_steppe=f"{row.steppe_min:.0f}–{row.steppe_max:.0f}%",
                ref_y="; ".join(f"{name} ~{pct:.0f}%" for name, pct in row.y_haplogroups.items()),
                sample_y=sample_y,
                y_note=y_note,
                note=row.note,
            )
        )
    matches.sort(key=lambda item: item.percent, reverse=True)
    if matches:
        notes.append(
            f"Closest published range: {matches[0].population} (fit {matches[0].percent:.0f}%). "
            "Fit is distance to the table, not a probability you belong to that community."
        )
    return ComparisonBlock(kind="community_ref", available=True, estimates=matches, notes=notes)
