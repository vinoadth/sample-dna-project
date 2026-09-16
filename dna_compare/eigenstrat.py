from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from dna_compare.config import CODE_TO_CHROM, Settings, default_settings

HEADER_SIZE = 48
PACKED_MISSING = 3


@dataclass
class IndRecord:
    index: int
    sample_id: str
    sex: str
    population: str


@dataclass
class SnpRecord:
    index: int
    rsid: str
    chrom: str
    gpos: float
    pos: int
    allele1: str
    allele2: str


class PackedTGeno:
    """Random-access reader for AADR TGENO (individual-major packed ancestrymap)."""

    def __init__(self, geno_path: Path):
        self.path = Path(geno_path)
        with self.path.open("rb") as handle:
            header = handle.read(HEADER_SIZE)
        if not header.startswith(b"TGENO"):
            raise ValueError(f"{self.path} is not a TGENO packed file (got {header[:16]!r})")
        parts = header.split()
        self.nind = int(parts[1])
        self.nsnp = int(parts[2])
        self.bytes_per_ind = (self.nsnp + 3) // 4
        expected = HEADER_SIZE + self.bytes_per_ind * self.nind
        size = self.path.stat().st_size
        if size != expected:
            raise ValueError(
                f"TGENO size mismatch for {self.path}: expected {expected} bytes, got {size}"
            )

    def read_individual(self, ind_index: int) -> np.ndarray:
        if ind_index < 0 or ind_index >= self.nind:
            raise IndexError(ind_index)
        offset = HEADER_SIZE + ind_index * self.bytes_per_ind
        with self.path.open("rb") as handle:
            handle.seek(offset)
            packed = np.frombuffer(handle.read(self.bytes_per_ind), dtype=np.uint8).copy()
        shifts = np.array([6, 4, 2, 0], dtype=np.uint8)
        unpacked = ((packed[:, None] >> shifts) & 3).ravel()
        return unpacked[: self.nsnp].astype(np.uint8)


class AadrPanel:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or default_settings()
        self._inds: list[IndRecord] | None = None
        self._snps: list[SnpRecord] | None = None
        self._id_to_ind: dict[str, IndRecord] | None = None
        self._pop_to_inds: dict[str, list[IndRecord]] | None = None
        self._geno: PackedTGeno | None = None

    @property
    def available(self) -> bool:
        return (
            self.settings.aadr_geno.exists()
            and self.settings.aadr_ind.exists()
            and self.settings.aadr_snp.exists()
        )

    def inds(self) -> list[IndRecord]:
        if self._inds is None:
            records = []
            with self.settings.aadr_ind.open() as handle:
                for i, line in enumerate(handle):
                    parts = line.split()
                    if len(parts) < 3:
                        continue
                    records.append(IndRecord(i, parts[0], parts[1], parts[2]))
            self._inds = records
            self._id_to_ind = {rec.sample_id: rec for rec in records}
            pops: dict[str, list[IndRecord]] = {}
            for rec in records:
                pops.setdefault(rec.population, []).append(rec)
            self._pop_to_inds = pops
        return self._inds

    def snps(self) -> list[SnpRecord]:
        if self._snps is None:
            records = []
            with self.settings.aadr_snp.open() as handle:
                for i, line in enumerate(handle):
                    parts = line.split()
                    if len(parts) < 6:
                        continue
                    chrom_raw = parts[1]
                    chrom = CODE_TO_CHROM.get(int(chrom_raw), chrom_raw) if chrom_raw.isdigit() else chrom_raw
                    records.append(
                        SnpRecord(
                            index=i,
                            rsid=parts[0],
                            chrom=str(chrom),
                            gpos=float(parts[2]),
                            pos=int(parts[3]),
                            allele1=parts[4],
                            allele2=parts[5],
                        )
                    )
            self._snps = records
        return self._snps

    def sample_by_id(self, sample_id: str) -> IndRecord | None:
        self.inds()
        assert self._id_to_ind is not None
        return self._id_to_ind.get(sample_id)

    def samples_for_population(self, population: str, limit: int | None = None) -> list[IndRecord]:
        self.inds()
        assert self._pop_to_inds is not None
        recs = self._pop_to_inds.get(population, [])
        cap = self.settings.max_samples_per_pop if limit is None else limit
        return recs[:cap]

    def geno(self) -> PackedTGeno:
        if self._geno is None:
            self._geno = PackedTGeno(self.settings.aadr_geno)
        return self._geno

    def dosage_allele1(self, sample_id: str) -> np.ndarray:
        rec = self.sample_by_id(sample_id)
        if rec is None:
            raise KeyError(sample_id)
        g = self.geno().read_individual(rec.index).astype(np.float32)
        g[g == PACKED_MISSING] = np.nan
        return g

    def population_allele1_freq(self, populations: tuple[str, ...] | str) -> np.ndarray:
        if isinstance(populations, str):
            populations = (populations,)
        cache_name = "aadr_freq_" + "_".join(sorted(populations)) + ".npy"
        cache_path = self.settings.cache_dir / cache_name
        if cache_path.exists():
            return np.load(cache_path)
        dosages = []
        for pop in populations:
            for rec in self.samples_for_population(pop):
                dosages.append(self.dosage_allele1(rec.sample_id))
        if not dosages:
            raise KeyError(f"No AADR samples for {populations}")
        stacked = np.vstack(dosages)
        with np.errstate(all="ignore"):
            freq = np.nanmean(stacked / 2.0, axis=0).astype(np.float32)
        self.settings.cache_dir.mkdir(parents=True, exist_ok=True)
        np.save(cache_path, freq)
        return freq
