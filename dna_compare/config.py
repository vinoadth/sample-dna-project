from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
REFERENCE_DIR = DATA_DIR / "references"
HOMININ_DIR = REFERENCE_DIR / "hominin"
CASTE_DIR = REFERENCE_DIR / "caste"
TAMIL_COMMUNITY_REF = CASTE_DIR / "tamil_community_reference.tsv"
CACHE_DIR = REFERENCE_DIR / "cache"
SAMPLE_DIR = DATA_DIR / "samples"
UPLOAD_DIR = DATA_DIR / "uploads"

AADR_DIR = REFERENCE_DIR / "aadr"
AADR_STEM = AADR_DIR / "v66.p1_HO.aadr.patch.PUB"
AADR_GENO = Path(str(AADR_STEM) + ".geno")
AADR_IND = Path(str(AADR_STEM) + ".ind")
AADR_SNP = Path(str(AADR_STEM) + ".snp")
AADR_ANNO = AADR_DIR / "v66.p1_HO.aadr.PUB.anno"

LIFTOVER_DIR = REFERENCE_DIR / "liftover"
HG38_TO_HG19_CHAIN = LIFTOVER_DIR / "hg38ToHg19.over.chain.gz"
HG38_TO_HG19_CHAIN_URL = "https://hgdownload.soe.ucsc.edu/goldenPath/hg38/liftOver/hg38ToHg19.over.chain.gz"

# Legacy locations (pre-move). default_settings() prefers these if still in the project root.
_LEGACY_STEM = PROJECT_ROOT / "v66.p1_HO.aadr.patch.PUB"

# High-coverage archaic VCFs (hg19/GRCh37 to match HO coordinates).
# Download later into data/references/hominin/ using these exact names.
HOMININ_DOWNLOADS = {
    "altai_neanderthal": {
        "filename": "AltaiNea.hg19_1000g.vcf.gz",
        "index": "AltaiNea.hg19_1000g.vcf.gz.tbi",
        "source": "http://cdna.eva.mpg.de/neandertal/altai/AltaiNeandertal/VCF/",
        "label": "Altai Neanderthal (high-coverage VCF)",
    },
    "vindija_neanderthal": {
        "filename": "Vindija33.19.hg19_1000g.vcf.gz",
        "index": "Vindija33.19.hg19_1000g.vcf.gz.tbi",
        "source": "http://cdna.eva.mpg.de/neandertal/Vindija/VCF/",
        "label": "Vindija 33.19 Neanderthal (high-coverage VCF)",
    },
    "chagyrskaya_neanderthal": {
        "filename": "Chagyrskaya-Phalanx.hg19.vcf.gz",
        "index": "Chagyrskaya-Phalanx.hg19.vcf.gz.tbi",
        "source": "http://ftp.eva.mpg.de/neandertal/Chagyrskaya/VCF/",
        "label": "Chagyrskaya Neanderthal VCF",
    },
    "denisovan": {
        "filename": "DenisovaPinky.hg19_1000g.vcf.gz",
        "index": "DenisovaPinky.hg19_1000g.vcf.gz.tbi",
        "source": "http://cdna.eva.mpg.de/denisova/",
        "label": "Denisova 3 (Pinky) high-coverage VCF",
    },
    "neanderthal_informative_snps": {
        "filename": "neanderthal_informative_snps.tsv",
        "source": "Sankararaman / Prüfer archaic-informative sites (build yourself or from paper supplements)",
        "label": "Optional SNP list: chrom pos ancestral derived source=Neanderthal",
        "columns": "chrom\tpos\tref\talt\tarchaic_allele\tsource",
    },
    "denisovan_informative_snps": {
        "filename": "denisovan_informative_snps.tsv",
        "source": "Browning Sprime / Sankararaman Denisovan-informative sites",
        "label": "Optional SNP list: chrom pos ancestral derived source=Denisovan",
        "columns": "chrom\tpos\tref\talt\tarchaic_allele\tsource",
    },
}

# Extra Indian-caste frequency / genotype files (not in AADR HO, or denser).
# Place into data/references/caste/ using these names.
CASTE_DOWNLOADS = {
    "caste_allele_frequencies": {
        "filename": "indian_caste_allele_frequencies.tsv",
        "label": "Preferred compact table you can build from any genotype dataset",
        "columns": "chrom\tpos\trsid\tref\talt\tpopulation\talt_freq\tn_haplotypes",
        "source": "Derived from 1000G / GenomeAsia / published Indian caste arrays",
    },
    "1000g_gih": {
        "filename": "1000G_GIH.snps.vcf.gz",
        "index": "1000G_GIH.snps.vcf.gz.tbi",
        "label": "1000 Genomes Gujarati Indian in Houston (GIH)",
        "source": "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/",
    },
    "1000g_pjl": {
        "filename": "1000G_PJL.snps.vcf.gz",
        "index": "1000G_PJL.snps.vcf.gz.tbi",
        "label": "1000 Genomes Punjabi in Lahore (PJL)",
        "source": "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/",
    },
    "1000g_beb": {
        "filename": "1000G_BEB.snps.vcf.gz",
        "index": "1000G_BEB.snps.vcf.gz.tbi",
        "label": "1000 Genomes Bengali in Bangladesh (BEB)",
        "source": "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/",
    },
    "1000g_stu": {
        "filename": "1000G_STU.snps.vcf.gz",
        "index": "1000G_STU.snps.vcf.gz.tbi",
        "label": "1000 Genomes Sri Lankan Tamil in the UK (STU)",
        "source": "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/",
    },
    "1000g_itu": {
        "filename": "1000G_ITU.snps.vcf.gz",
        "index": "1000G_ITU.snps.vcf.gz.tbi",
        "label": "1000 Genomes Indian Telugu in the UK (ITU)",
        "source": "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/",
    },
    "genomeasia_india": {
        "filename": "GenomeAsia100K_India.snps.vcf.gz",
        "index": "GenomeAsia100K_India.snps.vcf.gz.tbi",
        "label": "GenomeAsia 100K Indian-caste subset (request access)",
        "source": "https://browser.genomeasia100k.org/",
    },
    "estonian_biocentre_india": {
        "filename": "EstonianBiocentre_IndianCastes.eigenstrat.geno",
        "companion": [
            "EstonianBiocentre_IndianCastes.eigenstrat.snp",
            "EstonianBiocentre_IndianCastes.eigenstrat.ind",
        ],
        "label": "Estonian Biocentre / published Indian caste Human Origins-style genotypes",
        "source": "Metspalu / Reich / Moorjani Indian-caste supplements",
    },
    "nakatsuka2017_india": {
        "filename": "nakatsuka2017_india.snp",
        "companion": ["nakatsuka2017_india.ind", "nakatsuka2017_india.geno"],
        "label": "Nakatsuka et al. 2017 Cell India genotype pack (many jati/caste labels)",
        "source": "https://doi.org/10.1016/j.cell.2017.09.019",
    },
}

# AADR group IDs already on disk in v66.p1_HO (used immediately).
ARCHAIC_AADR_SAMPLES = {
    "Altai_Neanderthal": "AltaiNeanderthal.DG",
    "Vindija_Neanderthal": "Vindija.DG",
    "Chagyrskaya_Neanderthal": "Chagyrskaya8.DG",
    "Denisova": "Denisova3.DG",
    "Chimp": "Chimp.REF",
}

OUTGROUP_AADR_POPS = ("Mbuti", "Yoruba")

# Right / outgroup pops for qpAdm-style ancestry (must not overlap sources).
ANCESTRY_RIGHT_POPS: tuple[str, ...] = (
    "Mbuti",
    "Yoruba",
    "Ju_hoan_North",
    "Mandenka",
    "French",
    "Han",
    "Papuan",
    "Karitiana",
    "Ulchi",
)

# Map display caste/community → AADR .ind population labels.
CASTE_AADR_POPS: dict[str, tuple[str, ...]] = {
    "Brahmin": ("Brahmin",),
    "Yadava": ("Yadava",),
    "Kapu": ("Kapu",),
    "Mala": ("Mala",),
    "Madiga": ("Madiga",),
    "Irula": ("Irula",),
    "Relli": ("Relli_1", "Relli_2"),
    "Gujarati": ("GujaratiA", "GujaratiB", "GujaratiC", "GujaratiD", "GIH"),
    "Punjabi": ("Punjabi", "PJL"),
    "Bengali": ("BEB",),
    "Telugu": ("ITU",),
    "Tamil": ("STU", "STU-1", "STU-2"),
    "Vellalar": ("VLR",),
    "Cochin_Jew": ("Jew_Cochin",),
}

# Generic first; per-label notes are coverage caveats, not a preferred caste list.
CASTE_GENERAL_NOTES: tuple[str, ...] = (
    "Bars are the AADR HO community labels that exist in this file — not a ranked or complete caste list.",
    "A title or subcaste may sit under a scored label. Example: Pillai is often a Vellalar title; "
    "the HO VLR set is 9 samples, not every Vellalar subdivision.",
)

# Short UI notes: titles/subcastes often associated with a scored label.
CASTE_LABEL_NOTES: dict[str, str] = {
    "Tamil": (
        "Tamil (STU): Sri Lankan Tamil in 1000 Genomes — a language/region label, not a Tamil Nadu jati."
    ),
    "Brahmin": (
        "Brahmin: two HO samples only. Iyer / Iyengar are not this file."
    ),
    "Telugu": (
        "Telugu (ITU): Indian Telugu in the UK (1000 Genomes), not a single caste."
    ),
    "Vellalar": (
        "Vellalar (VLR): 9 Mondal samples. Not Gounder, Mudaliar, or every Pillai-using family."
    ),
    "Kapu": (
        "Kapu: Andhra community in AADR. Not Chettiyar / Nagarathar."
    ),
    "Mala": (
        "Mala: Andhra group in AADR. Not Pallar or Parayar."
    ),
    "Madiga": (
        "Madiga: Andhra group in AADR. Not Pallar or Parayar."
    ),
    "Irula": (
        "Irula: AADR tribal/community samples from South India (also GenomeAsia IRU, restricted)."
    ),
    "Gujarati": "Gujarati: 1000 Genomes GIH plus HO Gujarati A–D, not a single jati.",
    "Punjabi": "Punjabi: 1000 Genomes PJL plus HO Punjabi.",
    "Bengali": "Bengali: 1000 Genomes BEB.",
}

# Mentioned often, but no public HO bar.
CASTE_MISSING_PANEL_NOTES: tuple[str, ...] = (
    "No public HO panel for Chettiyar / Nattukottai Chettiar, Vanniyar, or Parayar. "
    "Do not read a missing name from a nearby bar (Kapu is not Chettiyar; Mala/Madiga are not Parayar).",
)

# Named packs of AADR HO groups already in v66.p1 (no extra download).
POPULATION_PACKS: dict[str, dict[str, tuple[str, ...]]] = {
    "greek": {
        "Greek_modern": ("Greek", "Greek_WGA"),
        "Greece_Crete_EMBA": ("Greece_Crete_HgCharalambos_EMBA",),
        "Greece_Crete_LBA": ("Greece_Crete_LBA",),
        "Greece_Peloponnese_LBA": ("Greece_Peloponnese_LBA",),
        "Greece_PalaceofNestor_BA": ("Greece_PalaceofNestor_BA",),
        "Greece_Kastrouli_BA": ("Greece_Kastrouli_BA",),
        "Greece_LBA": ("Greece_LBA",),
        "Greece_Crete_N": ("Greece_Crete_Aposelemis_N",),
        "Cycladic_EBA": ("Greece_EpanoKoufonisi_EBA_Cycladic",),
    },
    "chinese": {
        "Han": ("Han",),
        "Dai": ("Dai",),
        "Naxi": ("Naxi",),
        "China_Yangshao_LN": ("China_Baligang_LN_Yangshao",),
        "China_Xiaoheyan_LN": ("China_LN_Xiaoheyan",),
        "China_Shang": ("China_Jinan_LiuJiaZhuang_Shang", "China_Henan_Xisima_LShang"),
        "China_Zhou": ("China_Weifang_XinZhi_Zhou", "China_Baligang_BA_EasternZhou"),
        "China_Tibet_IA": ("China_Tibet_Gebusailu_IA",),
    },
    "persian": {
        "Iranian": ("Iranian",),
        "Iranian_Zoroastrian": ("Iranian_Zoroastrian",),
        "Iran_Hasanlu_IA": ("Iran_Hasanlu_IA",),
        "Iran_GanjDareh_N": ("Iran_GanjDareh_N",),
        "Iran_TepeHissar_C": ("Iran_TepeHissar_C",),
        "Iran_Parthian": ("Iran_LiarsangBon_Parthian",),
        "Turkey_Ancient_Persian": ("Turkey_Ancient_Persian",),
    },
    "caste": CASTE_AADR_POPS,
}

# 3-source South Asia model (Narasimhan-style left pops). One Steppe number.
ANCESTRY_AADR_POPS: dict[str, tuple[str, ...]] = {
    "Steppe_MLBA": ("Russia_Chelyabinsk_MLBA_Sintashta",),
    "Indus_Periphery": ("Iran_ShahriSokhta_BA1-1", "Iran_ShahriSokhta_BA2-2"),
    "AASI_Onge": ("ONG",),
}

DEFAULT_POPULATION_PACKS = ("greek", "chinese", "persian", "caste")

MAX_SAMPLES_PER_POP = 24
VARIANT_PREVIEW_LIMIT = 100

# Chromosome codes used in EIGENSTRAT/HO .snp files.
CHROM_TO_CODE = {str(i): i for i in range(1, 23)}
CHROM_TO_CODE.update(
    {
        "X": 23,
        "Y": 24,
        "XY": 25,
        "MT": 26,
        "M": 26,
    }
)
CODE_TO_CHROM = {v: k for k, v in CHROM_TO_CODE.items() if k not in {"M", "XY"}}
CODE_TO_CHROM[25] = "XY"
CODE_TO_CHROM[26] = "MT"


@dataclass
class Settings:
    aadr_geno: Path = AADR_GENO
    aadr_ind: Path = AADR_IND
    aadr_snp: Path = AADR_SNP
    aadr_anno: Path = AADR_ANNO
    hominin_dir: Path = HOMININ_DIR
    caste_dir: Path = CASTE_DIR
    tamil_community_ref: Path = TAMIL_COMMUNITY_REF
    cache_dir: Path = CACHE_DIR
    variant_preview_limit: int = VARIANT_PREVIEW_LIMIT
    max_samples_per_pop: int = MAX_SAMPLES_PER_POP
    compare_hominin: bool = True
    compare_caste: bool = True
    compare_populations: bool = True
    compare_ancestry: bool = True
    compare_haplogroups: bool = True
    assume_assembly: str | None = None
    auto_download_chain: bool = True
    liftover_chain: Path = HG38_TO_HG19_CHAIN
    population_packs: tuple[str, ...] = DEFAULT_POPULATION_PACKS
    extra_pops: dict[str, tuple[str, ...]] = field(default_factory=dict)
    extra_caste_groups: dict[str, tuple[str, ...]] = field(default_factory=dict)
    ancestry_right_pops: tuple[str, ...] = ANCESTRY_RIGHT_POPS

    def caste_groups(self) -> dict[str, tuple[str, ...]]:
        merged = dict(CASTE_AADR_POPS)
        merged.update(self.extra_caste_groups)
        return merged

    def ancestry_groups(self) -> dict[str, tuple[str, ...]]:
        return dict(ANCESTRY_AADR_POPS)

    def selected_population_groups(self) -> dict[str, tuple[str, ...]]:
        groups: dict[str, tuple[str, ...]] = {}
        for pack in self.population_packs:
            groups.update(POPULATION_PACKS.get(pack, {}))
        groups.update(self.extra_pops)
        groups.update(self.extra_caste_groups)
        return groups


def _existing_aadr_stem() -> Path:
    for stem in (AADR_STEM, _LEGACY_STEM):
        if Path(str(stem) + ".geno").exists() and Path(str(stem) + ".ind").exists():
            return stem
    return AADR_STEM


def default_settings() -> Settings:
    stem = _existing_aadr_stem()
    return Settings(
        aadr_geno=Path(str(stem) + ".geno"),
        aadr_ind=Path(str(stem) + ".ind"),
        aadr_snp=Path(str(stem) + ".snp"),
        aadr_anno=AADR_ANNO,
    )
