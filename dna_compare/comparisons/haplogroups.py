from __future__ import annotations

from collections import Counter
from pathlib import Path

from dna_compare.config import Settings
from dna_compare.models import (
    HaplogroupGroupCount,
    HaplogroupMarkerCall,
    HaplogroupResult,
    HaplogroupRow,
)

# Published backbone Y markers (hg19 / GRCh37). Alleles from ISOGG / FTDNA / Karafet.
# M17 is an indel on arrays and is ignored for the final call if it contradicts M173.
Y_MARKERS: tuple[dict, ...] = (
    {"haplogroup": "R (M207)", "marker": "M207", "rsids": ("rs2032658",), "positions": (15581983,), "ancestral": "A", "derived": "G", "backbone": True},
    {"haplogroup": "R1 (M173)", "marker": "M173", "rsids": ("rs2032624",), "positions": (15026424,), "ancestral": "A", "derived": "C", "backbone": True},
    {"haplogroup": "R1a1 (M17)", "marker": "M17", "rsids": ("rs3908",), "positions": (21733165, 21733168), "ancestral": "D", "derived": "I", "backbone": True},
    {"haplogroup": "R1a1a (M198)", "marker": "M198", "rsids": ("rs2020857",), "positions": (15030752,), "ancestral": "C", "derived": "T", "backbone": True},
    {"haplogroup": "R1b (M343)", "marker": "M343", "rsids": ("rs9786184",), "positions": (2887824,), "ancestral": "C", "derived": "A", "backbone": True},
    {"haplogroup": "H (M69)", "marker": "M69", "rsids": ("rs2032673",), "positions": (21894058,), "ancestral": "T", "derived": "C", "backbone": True},
    {"haplogroup": "L (M20)", "marker": "M20", "rsids": ("rs3911",), "positions": (21733454,), "ancestral": "A", "derived": "G", "backbone": True},
    {"haplogroup": "J2 (M172)", "marker": "M172", "rsids": ("rs2032604",), "positions": (14969634,), "ancestral": "T", "derived": "G", "backbone": True},
    {"haplogroup": "J1 (M267)", "marker": "M267", "rsids": ("rs9341313",), "positions": (22741818,), "ancestral": "T", "derived": "G", "backbone": True},
    {"haplogroup": "I (M170)", "marker": "M170", "rsids": ("rs2032597",), "positions": (14847792,), "ancestral": "A", "derived": "C", "backbone": True},
    {"haplogroup": "G (M201)", "marker": "G-M201", "rsids": ("rs2032636",), "positions": (15027529,), "ancestral": "G", "derived": "T", "backbone": True},
    {"haplogroup": "C (M130)", "marker": "M130", "rsids": ("rs35284970",), "positions": (2734854,), "ancestral": "C", "derived": "T", "backbone": True},
    {"haplogroup": "Q (M242)", "marker": "M242", "rsids": ("rs8179021",), "positions": (15018582,), "ancestral": "C", "derived": "T", "backbone": True},
)

# Deepest-first labels used for the sample call.
_SPECIFICITY = (
    "R1a1a (M198)",
    "R1a1 (M17)",
    "R1b (M343)",
    "R1 (M173)",
    "R (M207)",
    "J2 (M172)",
    "J1 (M267)",
    "H (M69)",
    "L (M20)",
    "G (M201)",
    "C (M130)",
    "Q (M242)",
    "I (M170)",
)

# Rows in the AADR frequency table (ISOGG prefix → display).
# Third field is the sample-marker haplogroup key when it differs from the row label.
_FREQ_ROWS: tuple[tuple[str, str, str], ...] = (
    ("R1a1 (M17)", "M17", "R1a1 (M17)"),
    ("R1b (M343)", "M343", "R1b (M343)"),
    ("R2 (M124)", "M124", ""),
    ("H (M69)", "M69", "H (M69)"),
    ("L (M20)", "M20", "L (M20)"),
    ("J2 (M172)", "M172", "J2 (M172)"),
    ("J1 (M267)", "M267", "J1 (M267)"),
    ("C", "M130", "C (M130)"),
    ("O", "M175", ""),
    ("G", "M201", "G (M201)"),
    ("Q", "M242", "Q (M242)"),
    ("other", "", ""),
)

# rCRS / PhyloTree positions (rCRS is H2a2a1, so REF=rCRS is often already derived).
MT_MARKERS: tuple[dict, ...] = (
    {"haplogroup": "M (10400T)", "marker": "10400T", "chrom": "MT", "rsids": ("rs28358278",), "positions": (10400,), "ancestral": "C", "derived": "T", "backbone": True},
    {"haplogroup": "M2 (1780C)", "marker": "1780C", "chrom": "MT", "rsids": ("rs2854127",), "positions": (1780,), "ancestral": "T", "derived": "C", "backbone": True},
    {"haplogroup": "M3 (4580C)", "marker": "4580C", "chrom": "MT", "rsids": (), "positions": (4580,), "ancestral": "T", "derived": "C", "backbone": True},
    {"haplogroup": "R (12705C)", "marker": "12705C", "chrom": "MT", "rsids": (), "positions": (12705,), "ancestral": "T", "derived": "C", "backbone": True},
    {"haplogroup": "R5 (8594C)", "marker": "8594C", "chrom": "MT", "rsids": ("rs372365688",), "positions": (8594,), "ancestral": "T", "derived": "C", "backbone": True},
    {"haplogroup": "R7 (13105G)", "marker": "13105G", "chrom": "MT", "rsids": (), "positions": (13105,), "ancestral": "A", "derived": "G", "backbone": True},
    {"haplogroup": "R8 (13215C)", "marker": "13215C", "chrom": "MT", "rsids": (), "positions": (13215,), "ancestral": "T", "derived": "C", "backbone": True},
    {"haplogroup": "R30 (8584A)", "marker": "8584A", "chrom": "MT", "rsids": ("rs3135028",), "positions": (8584,), "ancestral": "G", "derived": "A", "backbone": True},
    {"haplogroup": "U (12308G)", "marker": "12308G", "chrom": "MT", "rsids": (), "positions": (12308,), "ancestral": "A", "derived": "G", "backbone": True},
    {"haplogroup": "U2 (16051G)", "marker": "16051G", "chrom": "MT", "rsids": ("rs117565943",), "positions": (16051,), "ancestral": "A", "derived": "G", "backbone": True},
    {"haplogroup": "HV (14766C)", "marker": "14766C", "chrom": "MT", "rsids": ("rs3135031",), "positions": (14766,), "ancestral": "T", "derived": "C", "backbone": True},
    {"haplogroup": "H (7028C)", "marker": "7028C", "chrom": "MT", "rsids": (), "positions": (7028,), "ancestral": "T", "derived": "C", "backbone": True},
    {"haplogroup": "JT (16126C)", "marker": "16126C", "chrom": "MT", "rsids": ("rs147029798",), "positions": (16126,), "ancestral": "T", "derived": "C", "backbone": True},
)

_MT_SPECIFICITY = (
    "R8 (13215C)",
    "R7 (13105G)",
    "R5 (8594C)",
    "R30 (8584A)",
    "M3 (4580C)",
    "M2 (1780C)",
    "U2 (16051G)",
    "JT (16126C)",
    "H (7028C)",
    "HV (14766C)",
    "U (12308G)",
    "M (10400T)",
    "R (12705C)",
)

# display, marker, sample key, AADR prefix, prefixes to exclude
_MT_FREQ_ROWS: tuple[tuple[str, str, str, str, tuple[str, ...]], ...] = (
    ("M (10400T)", "10400T", "M (10400T)", "M", ()),
    ("M2 (1780C)", "1780C", "M2 (1780C)", "M2", ()),
    ("M3", "4580C", "M3 (4580C)", "M3", ("M30", "M33", "M36")),
    ("M4", "", "", "M4", ()),
    ("M36", "", "", "M36", ()),
    ("R (12705C)", "12705C", "R (12705C)", "R", ()),
    ("R5 (8594C)", "8594C", "R5 (8594C)", "R5", ()),
    ("R7 (13105G)", "13105G", "R7 (13105G)", "R7", ()),
    ("R8 (13215C)", "13215C", "R8 (13215C)", "R8", ()),
    ("R30 (8584A)", "8584A", "R30 (8584A)", "R30", ()),
    ("U (12308G)", "12308G", "U (12308G)", "U", ()),
    ("U2 (16051G)", "16051G", "U2 (16051G)", "U2", ()),
    ("HV (14766C)", "14766C", "HV (14766C)", "HV", ()),
    ("H (7028C)", "7028C", "H (7028C)", "H", ("HV",)),
    ("JT (16126C)", "16126C", "JT (16126C)", "JT", ()),
)

_COMP = str.maketrans("ACGT", "TGCA")
_ANNO_GROUP = 14
_ANNO_SEX = 30
_ANNO_Y_ISOGG = 35
_ANNO_Y_MANUAL = 36
_ANNO_MT = 38


def _norm_rsid(rsid: str) -> str:
    rsid = (rsid or "").split(",")[0].strip()
    if rsid.startswith("exm-"):
        rsid = rsid[4:]
    return rsid


def _observed_allele(row: dict) -> str | None:
    gt = row.get("genotype") or ""
    ref = str(row.get("ref") or "").upper()
    alt = str(row.get("alt") or "").upper()
    if not gt or gt == "." or gt.startswith("."):
        return None
    token = gt.split(":", 1)[0].replace("|", "/")
    parts = token.split("/") if "/" in token else [token]
    alleles: list[str] = []
    for part in parts:
        if part == "0":
            alleles.append(ref)
        elif part == "1":
            alleles.append(alt)
        elif part.upper() in {ref, alt, "D", "I", "A", "C", "G", "T"}:
            alleles.append(part.upper())
        elif part == ".":
            return None
    uniq = {a for a in alleles if a}
    if len(uniq) == 1:
        return next(iter(uniq))
    if len(uniq) > 1:
        return "het"
    return None


def _lookup_marker(index: dict[tuple[str, int], dict], spec: dict) -> dict | None:
    chrom = spec.get("chrom") or "Y"
    for pos in spec["positions"]:
        row = index.get((chrom, int(pos)))
        if row:
            return row
    want = {_norm_rsid(r) for r in spec.get("rsids") or ()}
    if not want:
        return None
    for row in index.values():
        if row.get("chrom") != chrom:
            continue
        if _norm_rsid(str(row.get("rsid") or "")) in want:
            return row
    return None


def _status(observed: str | None, ancestral: str, derived: str) -> str:
    if observed is None:
        return "no-call"
    if observed == "het":
        return "het"
    obs = observed.upper()
    anc, der = ancestral.upper(), derived.upper()
    if obs == der:
        return "derived"
    if obs == anc:
        return "ancestral"
    if anc not in {"D", "I"} and der not in {"D", "I"}:
        if obs == der.translate(_COMP) and anc == anc:
            return "derived"
        if obs == anc.translate(_COMP):
            return "ancestral"
    return "mismatch"


def score_markers(query_index: dict[tuple[str, int], dict], specs: tuple[dict, ...]) -> list[HaplogroupMarkerCall]:
    calls: list[HaplogroupMarkerCall] = []
    for spec in specs:
        row = _lookup_marker(query_index, spec)
        observed = _observed_allele(row) if row else None
        status = _status(observed, spec["ancestral"], spec["derived"])
        rsids = spec.get("rsids") or ()
        calls.append(
            HaplogroupMarkerCall(
                haplogroup=spec["haplogroup"],
                marker=spec["marker"],
                rsid=rsids[0] if rsids else spec["marker"],
                chrom=spec.get("chrom") or "Y",
                pos=int(row["pos"]) if row else int(spec["positions"][0]),
                ancestral=spec["ancestral"],
                derived=spec["derived"],
                observed=observed,
                status=status,
                genotype=None if row is None else str(row.get("genotype") or ""),
                backbone=bool(spec.get("backbone", True)),
            )
        )
    return calls


def score_y_markers(query_index: dict[tuple[str, int], dict]) -> list[HaplogroupMarkerCall]:
    calls = score_markers(query_index, Y_MARKERS)
    by_label = {call.haplogroup: call for call in calls}

    # M17 indel on chips often contradicts M173; do not let it win.
    m17 = by_label.get("R1a1 (M17)")
    m173 = by_label.get("R1 (M173)")
    if m17 and m173 and m17.status == "derived" and m173.status == "ancestral":
        m17.status = "conflict"

    r1a1 = by_label.get("R1a1 (M17)")
    m198 = by_label.get("R1a1a (M198)")
    if m198 and r1a1 and m198.status == "derived" and r1a1.status in {"ancestral", "conflict"}:
        m198.status = "conflict"
    r1b = by_label.get("R1b (M343)")
    if r1b and m173 and r1b.status == "derived" and m173.status == "ancestral":
        r1b.status = "conflict"
    r1 = by_label.get("R1 (M173)")
    r = by_label.get("R (M207)")
    if r1 and r and r1.status == "derived" and r.status == "ancestral":
        r1.status = "conflict"
    return calls


def best_sample_haplogroup(
    calls: list[HaplogroupMarkerCall],
    specificity: tuple[str, ...] = _SPECIFICITY,
) -> str | None:
    derived = {c.haplogroup for c in calls if c.backbone and c.status == "derived"}
    if not derived:
        return None
    for label in specificity:
        if label in derived:
            return label
    return sorted(derived)[0]


def collapse_y_haplogroup(raw: str) -> str | None:
    text = (raw or "").strip().rstrip("~").replace(" ", "")
    if not text or text in {".", ".."} or text.lower().startswith("n/a"):
        return None
    if text.startswith("R1a"):
        return "R1a1 (M17)"
    if text.startswith("R1b"):
        return "R1b (M343)"
    if text.startswith("R2"):
        return "R2 (M124)"
    if text.startswith("H"):
        return "H (M69)"
    if text.startswith("L"):
        return "L (M20)"
    if text.startswith("J2"):
        return "J2 (M172)"
    if text.startswith("J"):
        return "J1 (M267)" if text.startswith("J1") else "J"
    if text.startswith("C"):
        return "C"
    if text.startswith("O"):
        return "O"
    if text.startswith("G"):
        return "G"
    if text.startswith("Q"):
        return "Q"
    if text.startswith("LT"):
        return "other"
    if text.startswith("T"):
        return "other"
    if text.startswith("E"):
        return "other"
    if text.startswith("I"):
        return "I (M170)"
    return "other"


def _y_call_from_anno(cols: list[str]) -> str | None:
    if len(cols) <= _ANNO_Y_MANUAL:
        return None
    manual = cols[_ANNO_Y_MANUAL].strip()
    auto = cols[_ANNO_Y_ISOGG].strip() if len(cols) > _ANNO_Y_ISOGG else ""
    for raw in (manual, auto):
        collapsed = collapse_y_haplogroup(raw)
        if collapsed is not None:
            return collapsed
    return None


def collapse_mt_haplogroup(raw: str) -> str | None:
    """Keep the first AADR token (M36d;M → M36d) for prefix counts."""
    text = (raw or "").split(";")[0].strip().replace(" ", "")
    if not text or text in {".", ".."} or text.lower().startswith("n/a"):
        return None
    return text


def score_mt_markers(query_index: dict[tuple[str, int], dict]) -> list[HaplogroupMarkerCall]:
    calls = score_markers(query_index, MT_MARKERS)
    by_label = {call.haplogroup: call for call in calls}
    m_call = by_label.get("M (10400T)")
    r_call = by_label.get("R (12705C)")
    if m_call and r_call and m_call.status == "derived" and r_call.status == "derived":
        m_call.status = "conflict"
        r_call.status = "conflict"
    for child, parent in (
        ("M2 (1780C)", "M (10400T)"),
        ("M3 (4580C)", "M (10400T)"),
        ("R5 (8594C)", "R (12705C)"),
        ("R7 (13105G)", "R (12705C)"),
        ("R8 (13215C)", "R (12705C)"),
        ("R30 (8584A)", "R (12705C)"),
        ("U (12308G)", "R (12705C)"),
        ("U2 (16051G)", "U (12308G)"),
        ("HV (14766C)", "R (12705C)"),
        ("H (7028C)", "HV (14766C)"),
        ("JT (16126C)", "R (12705C)"),
    ):
        child_call = by_label.get(child)
        parent_call = by_label.get(parent)
        if (
            child_call
            and parent_call
            and child_call.status == "derived"
            and parent_call.status in {"ancestral", "conflict"}
        ):
            child_call.status = "conflict"
    return calls


def load_anno_mt_by_group(anno_path: Path) -> dict[str, list[str | None]]:
    """AADR group ID → mt haplogroup tokens (all sexes; None = uncalled)."""
    out: dict[str, list[str | None]] = {}
    if not anno_path.exists():
        return out
    with anno_path.open(encoding="utf-8", errors="replace") as handle:
        header = handle.readline()
        if not header:
            return out
        for line in handle:
            cols = line.rstrip("\n").split("\t")
            if len(cols) <= _ANNO_MT:
                continue
            group = cols[_ANNO_GROUP].strip()
            out.setdefault(group, []).append(collapse_mt_haplogroup(cols[_ANNO_MT]))
    return out


def _prefix_count(tokens: list[str], prefix: str, exclude: tuple[str, ...]) -> int:
    n = 0
    for token in tokens:
        if not token.startswith(prefix):
            continue
        if any(token.startswith(ex) for ex in exclude):
            continue
        n += 1
    return n


def aadr_mt_frequency_rows(
    anno_by_pop: dict[str, list[str | None]],
    groups: dict[str, tuple[str, ...]],
    sample_status: dict[str, str],
) -> list[HaplogroupRow]:
    rows: list[HaplogroupRow] = []
    for label, marker, sample_key, prefix, exclude in _MT_FREQ_ROWS:
        group_counts: dict[str, HaplogroupGroupCount] = {}
        for display, pops in groups.items():
            tokens = [tok for pop in pops for tok in anno_by_pop.get(pop, [])]
            called = [tok for tok in tokens if tok is not None]
            n_called = len(called)
            n = _prefix_count(called, prefix, exclude) if prefix else 0
            percent = (100.0 * n / n_called) if n_called else None
            group_counts[display] = HaplogroupGroupCount(n=n, n_called=n_called, percent=percent)
        if not prefix and not any(item.n for item in group_counts.values()):
            continue
        rows.append(
            HaplogroupRow(
                haplogroup=label,
                marker=marker,
                sample_status=sample_status.get(sample_key or label, "no-call"),
                groups=group_counts,
            )
        )
    other_groups: dict[str, HaplogroupGroupCount] = {}
    named_prefixes = tuple(prefix for _l, _m, _s, prefix, _e in _MT_FREQ_ROWS if prefix)
    for display, pops in groups.items():
        called = [tok for pop in pops for tok in anno_by_pop.get(pop, []) if tok is not None]
        n_called = len(called)
        n = sum(1 for tok in called if not any(tok.startswith(p) for p in named_prefixes))
        other_groups[display] = HaplogroupGroupCount(
            n=n,
            n_called=n_called,
            percent=(100.0 * n / n_called) if n_called else None,
        )
    if any(item.n for item in other_groups.values()):
        rows.append(
            HaplogroupRow(
                haplogroup="other",
                marker="",
                sample_status="no-call",
                groups=other_groups,
            )
        )
    return rows


def load_anno_y_by_group(anno_path: Path) -> dict[str, list[str | None]]:
    """AADR group ID → Y haplogroup labels for males (None = uncalled)."""
    out: dict[str, list[str | None]] = {}
    if not anno_path.exists():
        return out
    with anno_path.open(encoding="utf-8", errors="replace") as handle:
        header = handle.readline()
        if not header:
            return out
        for line in handle:
            cols = line.rstrip("\n").split("\t")
            if len(cols) <= _ANNO_Y_ISOGG:
                continue
            group = cols[_ANNO_GROUP].strip()
            sex = cols[_ANNO_SEX].strip().upper() if len(cols) > _ANNO_SEX else ""
            if sex.startswith("F"):
                continue
            out.setdefault(group, []).append(_y_call_from_anno(cols))
    return out


def _group_counts(calls: list[str | None]) -> dict[str, HaplogroupGroupCount]:
    called = [c for c in calls if c is not None]
    n_called = len(called)
    counts = Counter(called)
    rows: dict[str, HaplogroupGroupCount] = {}
    for label, _marker, _prefix in _FREQ_ROWS:
        n = counts.get(label, 0)
        if label == "other":
            named = {name for name, _, _ in _FREQ_ROWS if name != "other"}
            n = sum(v for k, v in counts.items() if k not in named)
        percent = (100.0 * n / n_called) if n_called else None
        rows[label] = HaplogroupGroupCount(n=n, n_called=n_called, percent=percent)
    return rows


def aadr_frequency_rows(
    anno_by_pop: dict[str, list[str | None]],
    groups: dict[str, tuple[str, ...]],
    sample_status: dict[str, str],
) -> list[HaplogroupRow]:
    per_group = {
        display: _group_counts([call for pop in pops for call in anno_by_pop.get(pop, [])])
        for display, pops in groups.items()
    }
    rows: list[HaplogroupRow] = []
    for label, marker, sample_key in _FREQ_ROWS:
        if label == "other":
            continue
        rows.append(
            HaplogroupRow(
                haplogroup=label,
                marker=marker,
                sample_status=sample_status.get(sample_key or label, "no-call"),
                groups={name: per_group[name][label] for name in groups},
            )
        )
    other_groups = {name: per_group[name]["other"] for name in groups}
    if any(item.n for item in other_groups.values()):
        rows.append(
            HaplogroupRow(
                haplogroup="other",
                marker="",
                sample_status="no-call",
                groups=other_groups,
            )
        )
    return rows


SAMPLE_STATUS_NOTES: tuple[str, ...] = (
    "This sample column: derived = yes, this file has the mutation that defines that haplogroup.",
    "Ancestral = no, this file has the older allele, so that haplogroup is ruled out.",
    "No-call = that defining SNP is missing or unreadable in this VCF, so we cannot say yes or no.",
    "Conflict = markers disagree (a downstream SNP looks like yes while a parent lineage is no). Do not treat the downstream yes as a call.",
)


def compare_haplogroups(
    query_index: dict[tuple[str, int], dict],
    *,
    settings: Settings,
) -> HaplogroupResult:
    notes = [
        "One person has one Y haplogroup. Percentages are AADR male counts in each scored group, not mixture weights.",
        "R1a1 here is the M17 / M198 lineage (also written R1a1a). M17 on SNP arrays is an indel and is marked conflict if M173 is ancestral.",
        "AADR Y labels are the ISOGG column in v66.1 HO .anno (YFull-based automatic calls). "
        "Several HO community labels have only a few samples (often 2–9).",
    ]
    mt_notes = [
        "One person has one mtDNA haplogroup. Percentages are AADR published mt calls, not mixture weights.",
        "Markers use rCRS / PhyloTree positions. rCRS is haplogroup H2a2a1, so REF=rCRS can already be the derived allele (for example 12705C = R).",
        "A dash means that label has no mt haplogroup in the AADR .anno (common for 1000 Genomes HO groups such as STU, ITU, GIH, PJL, BEB).",
        "M3 / R7 / R8 sit inside M / R; those rows can add up to more than 100%.",
    ]
    calls = score_y_markers(query_index)
    best = best_sample_haplogroup(calls)
    sample_status = {c.haplogroup: c.status for c in calls}
    mt_calls = score_mt_markers(query_index)
    mt_best = best_sample_haplogroup(mt_calls, _MT_SPECIFICITY)
    mt_status = {c.haplogroup: c.status for c in mt_calls}

    n_y = sum(1 for (chrom, _pos) in query_index if chrom == "Y")
    n_mt = sum(1 for (chrom, _pos) in query_index if chrom == "MT")
    if n_y == 0:
        notes.append("No chrY SNPs in this VCF, so every marker is no-call.")
    elif best:
        notes.append(f"Deepest consistent derived marker in this file: {best}.")
    else:
        notes.append("No backbone Y marker is derived in this file (or derived calls conflict).")
    if n_mt == 0:
        mt_notes.append("No chrMT SNPs in this VCF, so every mt marker is no-call.")
    elif mt_best:
        mt_notes.append(f"Deepest consistent derived mt marker in this file: {mt_best}.")
    else:
        mt_notes.append("No backbone mt marker is derived in this file (or calls conflict).")

    anno_path = settings.aadr_anno
    groups = settings.caste_groups()
    if not anno_path.exists():
        notes.append("AADR .anno not found; group percentages need data/references/aadr/*.anno.")
        mt_notes.append("AADR .anno not found; group percentages need data/references/aadr/*.anno.")
        return HaplogroupResult(
            available=any(c.status != "no-call" for c in calls),
            sample_best=best,
            markers=calls,
            rows=[],
            notes=notes,
            mt_available=any(c.status != "no-call" for c in mt_calls),
            mt_sample_best=mt_best,
            mt_markers=mt_calls,
            mt_rows=[],
            mt_notes=mt_notes,
            status_notes=list(SAMPLE_STATUS_NOTES),
        )
    anno_by_pop = load_anno_y_by_group(anno_path)
    rows = aadr_frequency_rows(anno_by_pop, groups, sample_status)
    n_males = sum(len(anno_by_pop.get(pop, [])) for pops in groups.values() for pop in pops)
    notes.append(f"AADR males in scored caste/community groups: {n_males}.")
    mt_by_pop = load_anno_mt_by_group(anno_path)
    mt_rows = aadr_mt_frequency_rows(mt_by_pop, groups, mt_status)
    n_mt_called = sum(
        1
        for pops in groups.values()
        for pop in pops
        for tok in mt_by_pop.get(pop, [])
        if tok is not None
    )
    mt_with_calls = [
        name
        for name, pops in groups.items()
        if any(tok is not None for pop in pops for tok in mt_by_pop.get(pop, []))
    ]
    if mt_with_calls:
        mt_notes.append(
            "Labels with at least one AADR mt call: "
            + ", ".join(mt_with_calls)
            + f" ({n_mt_called} calls). Example: Vellalar/VLR is a small HO set that happens to have mt filled in."
        )
    else:
        mt_notes.append("No scored label has an AADR mt haplogroup in this .anno.")
    return HaplogroupResult(
        available=True,
        sample_best=best,
        markers=calls,
        rows=rows,
        notes=notes,
        mt_available=True,
        mt_sample_best=mt_best,
        mt_markers=mt_calls,
        mt_rows=mt_rows,
        mt_notes=mt_notes,
        status_notes=list(SAMPLE_STATUS_NOTES),
    )
