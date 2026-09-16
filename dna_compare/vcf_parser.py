from __future__ import annotations

import gzip
from collections import Counter
from pathlib import Path
from typing import BinaryIO, Iterator, TextIO

from dna_compare.config import VARIANT_PREVIEW_LIMIT
from dna_compare.models import VariantRow, VcfSummary


def _open_text(path: Path) -> TextIO:
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt")
    return path.open("rt")


def normalize_chrom(chrom: str) -> str:
    chrom = chrom.strip()
    if chrom.startswith("chr"):
        chrom = chrom[3:]
    if chrom == "23":
        return "X"
    if chrom == "24":
        return "Y"
    if chrom in {"25", "26", "M", "MT", "chrM"}:
        return "MT"
    return chrom


def _is_snp(ref: str, alt: str) -> bool:
    if ref in {".", ""} or alt in {".", ""}:
        return False
    if "," in alt:
        alt = alt.split(",", 1)[0]
    return len(ref) == 1 and len(alt) == 1 and ref != "*" and alt != "*"


def _parse_gt(gt: str) -> tuple[str, float | None]:
    if not gt or gt == "." or gt.startswith("."):
        return (".", None)
    token = gt.split(":", 1)[0]
    seps = "/" if "/" in token else "|" if "|" in token else None
    if seps is None:
        if token in {"0", "1"}:
            dosage = float(token)
            return (token, dosage)
        return (token, None)
    alleles = token.split(seps)
    if any(a == "." for a in alleles):
        return (token, None)
    try:
        dosage = sum(int(a) for a in alleles)
    except ValueError:
        return (token, None)
    return (token.replace("|", "/"), float(dosage))


def iter_vcf_snps(handle: TextIO) -> tuple[list[str], Iterator[dict]]:
    samples: list[str] = []

    def _rows() -> Iterator[dict]:
        for raw in handle:
            if raw.startswith("##"):
                continue
            if raw.startswith("#CHROM"):
                header = raw.rstrip("\n").split("\t")
                samples.clear()
                samples.extend(header[9:])
                continue
            if not raw.strip() or raw.startswith("#"):
                continue
            cols = raw.rstrip("\n").split("\t")
            if len(cols) < 8:
                continue
            ref = cols[3]
            alt = cols[4]
            snp = _is_snp(ref, alt)
            alt_primary = alt.split(",", 1)[0]
            gt_raw = cols[9] if len(cols) > 9 else "."
            gt, dosage = _parse_gt(gt_raw)
            yield {
                "chrom": normalize_chrom(cols[0]),
                "pos": int(cols[1]),
                "rsid": cols[2],
                "ref": ref,
                "alt": alt_primary,
                "alt_all": alt,
                "is_snp": snp,
                "genotype": gt,
                "dosage_alt": dosage,
                "n_samples": max(0, len(cols) - 9),
            }

    return samples, _rows()


def parse_vcf(
    source: Path | str | TextIO | BinaryIO,
    *,
    preview_limit: int = VARIANT_PREVIEW_LIMIT,
) -> tuple[VcfSummary, dict[tuple[str, int], dict]]:
    """Parse a SNP VCF into a UI summary plus (chrom, pos) lookup.

    `source` may be a path, an open text handle, or a binary buffer (API upload).
    """
    import io

    close = False
    handle: TextIO
    filename = "upload.vcf"
    if isinstance(source, (str, Path)):
        path = Path(source)
        filename = path.name
        handle = _open_text(path)
        close = True
    else:
        name = getattr(source, "name", filename)
        if isinstance(name, str):
            filename = Path(name).name
        raw = source.read()
        if isinstance(raw, bytes):
            if raw[:2] == b"\x1f\x8b":
                handle = gzip.open(io.BytesIO(raw), "rt")
            else:
                handle = io.StringIO(raw.decode("utf-8", errors="replace"))
            close = True
        else:
            handle = io.StringIO(raw)

    try:
        return _parse_open(handle, filename=filename, preview_limit=preview_limit)
    finally:
        if close:
            handle.close()


def _parse_open(handle: TextIO, *, filename: str, preview_limit: int) -> tuple[VcfSummary, dict[tuple[str, int], dict]]:
    samples, rows = iter_vcf_snps(handle)
    preview: list[VariantRow] = []
    index: dict[tuple[str, int], dict] = {}
    chrom_counts: Counter[str] = Counter()
    n_records = 0
    n_snps = 0
    n_skip = 0
    sample_id = Path(filename).stem
    n_file_samples = 0

    for row in rows:
        n_records += 1
        n_file_samples = max(n_file_samples, row["n_samples"])
        if not row["is_snp"]:
            n_skip += 1
            continue
        n_snps += 1
        chrom_counts[row["chrom"]] += 1
        key = (row["chrom"], row["pos"])
        index[key] = row
        if len(preview) < preview_limit:
            preview.append(
                VariantRow(
                    chrom=row["chrom"],
                    pos=row["pos"],
                    rsid=row["rsid"],
                    ref=row["ref"],
                    alt=row["alt"],
                    genotype=row["genotype"],
                    dosage_alt=row["dosage_alt"],
                )
            )

    if samples:
        sample_id = samples[0]
    summary = VcfSummary(
        sample_id=sample_id,
        n_records=n_records,
        n_snps=n_snps,
        n_non_snp_skipped=n_skip,
        n_samples_in_file=n_file_samples or len(samples),
        chrom_counts=dict(sorted(chrom_counts.items(), key=lambda kv: kv[0])),
        preview=preview,
    )
    return summary, index
