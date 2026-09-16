# Reference files

**AADR v66.1 Human Origins** belongs in `data/references/aadr/` (`*.geno`, `*.ind`, `*.snp`, `*.anno`). That panel already includes ancient/modern Greek, Chinese, Iranian/Persian, Indian-caste, and archaic hominin samples. No extra download is required for those comparisons.

Optional hominin extracts live in `data/references/hominin/`. Full MPI-EVA per-chromosome VCFs are 50–70 GB each and are not needed.

## Hominin (`data/references/hominin/`)

Use **hg19 / GRCh37** coordinates so sites line up with the HO SNP list and with typical consumer SNP VCFs.

| Save as | What it is |
| --- | --- |
| `AltaiNea.hg19_1000g.vcf.gz` | Altai Neanderthal high-coverage VCF |
| `AltaiNea.hg19_1000g.vcf.gz.tbi` | tabix index |
| `Vindija33.19.hg19_1000g.vcf.gz` | Vindija 33.19 Neanderthal VCF |
| `Vindija33.19.hg19_1000g.vcf.gz.tbi` | tabix index |
| `Chagyrskaya-Phalanx.hg19.vcf.gz` | Chagyrskaya Neanderthal VCF |
| `Chagyrskaya-Phalanx.hg19.vcf.gz.tbi` | tabix index |
| `DenisovaPinky.hg19_1000g.vcf.gz` | Denisova 3 (“Pinky”) VCF |
| `DenisovaPinky.hg19_1000g.vcf.gz.tbi` | tabix index |
| `neanderthal_informative_snps.tsv` | optional informative-site table |
| `denisovan_informative_snps.tsv` | optional informative-site table |

Typical sources: MPI-EVA (`http://cdna.eva.mpg.de/neandertal/` and `http://cdna.eva.mpg.de/denisova/`).

Informative TSV columns:

```
chrom	pos	ref	alt	archaic_allele	source
```

## Indian caste (`data/references/caste/`)

AADR HO already has Brahmin, Yadava, Kapu, Mala, Madiga, Irula, Relli, Gujarati, Punjabi, Telugu (ITU), Tamil (STU / STU-1 / STU-2), **Vellalar (VLR)**, Bengali (BEB), Cochin Jew.

**Spelling / format check (Sep 2026):** public *genotype* files labeled Pillai, Chettiyar/Chettiar, or Vanniyar were not found. Those names show up in older STR/mtDNA papers, not in downloadable HO/VCF panels. Closest public SNP label is Mondal **Vellalar (`VLR`)** already inside AADR HO (Pillai is often a Vellalar title). Nakatsuka 2017 *did* genotype many other Tamil groups (Kallar, Nadar, Arunthathiyar, Gounder, Mudaliar, …) but those arrays are **author-request only**. GenomeAsia has Iyer / Iyangar / Irula / Kota / Toda / Paniya / Urban Chennai — **DAC login**, not a public VCF.

Downloaded metadata (not genotypes) lives in `data/references/caste/`:

| File | What it is |
| --- | --- |
| `nakatsuka2017_groups.xlsx` | Group names + IBD scores (bioRxiv 047035) |
| `41586_2019_1793_MOESM3_ESM.xlsx` | GenomeAsia sample summary (IYE, IYA, IRU, …) |
| `tamil_nadu_group_aliases.tsv` | Spelling crosswalk and what is usable now |

Do not download Mondal ENA BAMs (`PRJEB16019`): they are whole genomes, and the Vellalar subset is already in AADR as `VLR`.

**Pallar / Parayar / Komati–Setti (name variants):** none of these strings are AADR HO population labels. Nakatsuka *did* genotype close matches, still restricted:

| Asked-for name | How papers usually label it | Nakatsuka (not public AADR) |
| --- | --- | --- |
| Pallar | Pallan, Devendrakulathan | `Pallan_PL1` Omni n=20; `Devendrakulathan` HO n=4 |
| Parayar | Paraiyar, Adi Dravidar | `Adi_Dravida` HO n=10 (do not confuse with `Paravar`, a different coastal group) |
| Chettiyar / Setti / Komati | Arya Vysya, Vysya (Andhra) | `Vysya` HO n=39 |

Public AADR already scores **Mala** and **Madiga** (Andhra), which are not Pallar/Parayar, and **Kapu**, which is not Komati/Chettiyar. Do not alias those names onto each other.

Add these files for more jati/caste labels and denser SNPs:

| Save as | What it is |
| --- | --- |
| `indian_caste_allele_frequencies.tsv` | **best next file to make** — compact frequencies |
| `1000G_GIH.snps.vcf.gz` | 1000 Genomes Gujarati (GIH) |
| `1000G_PJL.snps.vcf.gz` | 1000 Genomes Punjabi (PJL) |
| `1000G_BEB.snps.vcf.gz` | 1000 Genomes Bengali (BEB) |
| `1000G_STU.snps.vcf.gz` | 1000 Genomes Sri Lankan Tamil (STU) |
| `1000G_ITU.snps.vcf.gz` | 1000 Genomes Indian Telugu (ITU) |
| `GenomeAsia100K_India.snps.vcf.gz` | GenomeAsia Indian-caste subset (access required) |
| `EstonianBiocentre_IndianCastes.eigenstrat.geno` | plus matching `.snp` and `.ind` |
| `nakatsuka2017_india.snp` | plus `nakatsuka2017_india.ind` and `.geno` (many jati labels) |

Frequency TSV columns:

```
chrom	pos	rsid	ref	alt	population	alt_freq	n_haplotypes
```

Suggested `population` values: `Brahmin_TN`, `Brahmin_UP`, `Iyer`, `Iyengar`, `Nambudiri`, `Rajput`, `Jat`, `Ror`, `Patel`, `Maratha`, `Reddy`, `Kamma`, `Nair`, `Ezhava`, `Vellalar`, `Pillai`, `Chettiyar`, `Vanniyar`, `Mudaliar`, `Thevar`, `Nadar`, `Kayastha`, `Baniya`, `Khatri`, `Chamar`, `Yadav`, `Kurmi`, `Mala`, `Madiga`, `Irula`, `Paniya`.

After those files are in `data/references/caste/`, they still need to be wired into `compare_caste` (the app currently scores AADR HO labels only). The preferred drop-in is `indian_caste_allele_frequencies.tsv`.

## Query VCF

Your input should be SNP-only (no indels required). Chromosomes may be `1` or `chr1`. The JSON from `python main.py analyze file.vcf --json` is the payload a later `POST /analyze` API and HTML table can consume unchanged.
