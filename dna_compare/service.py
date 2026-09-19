from __future__ import annotations

from pathlib import Path
from typing import BinaryIO, TextIO

from dna_compare.comparisons import (
    compare_ancestry,
    compare_caste,
    compare_haplogroups,
    compare_hominin,
    compare_populations,
    compare_relatedness,
    score_community_reference,
)
from dna_compare.assembly import assembly_note, detect_assembly
from dna_compare.config import Settings, default_settings
from dna_compare.eigenstrat import AadrPanel
from dna_compare.liftover import ensure_hg38_to_hg19_chain, lift_query_index, load_chain
from dna_compare.models import AnalysisResult, ComparisonBlock, HaplogroupResult, RelatednessResult
from dna_compare.vcf_parser import parse_vcf, preview_rows


class AnalysisService:
    """Stable entry point for CLI today and FastAPI/Flask later."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or default_settings()
        self._panel: AadrPanel | None = None
        self._chain = None

    @property
    def panel(self) -> AadrPanel | None:
        panel = AadrPanel(self.settings)
        if not panel.available:
            return None
        if self._panel is None:
            self._panel = panel
        return self._panel

    def analyze(
        self,
        source: Path | str | TextIO | BinaryIO,
        *,
        filename: str | None = None,
        compare_hominin_flag: bool | None = None,
        compare_caste_flag: bool | None = None,
        compare_populations_flag: bool | None = None,
        compare_ancestry_flag: bool | None = None,
        compare_haplogroups_flag: bool | None = None,
        other_source: Path | str | TextIO | BinaryIO | None = None,
        other_filename: str | None = None,
    ) -> AnalysisResult:
        do_hominin = self.settings.compare_hominin if compare_hominin_flag is None else compare_hominin_flag
        do_caste = self.settings.compare_caste if compare_caste_flag is None else compare_caste_flag
        do_pops = (
            self.settings.compare_populations if compare_populations_flag is None else compare_populations_flag
        )
        do_ancestry = self.settings.compare_ancestry if compare_ancestry_flag is None else compare_ancestry_flag
        do_haplo = (
            self.settings.compare_haplogroups if compare_haplogroups_flag is None else compare_haplogroups_flag
        )
        source_name = filename or (Path(source).name if isinstance(source, (str, Path)) else "upload.vcf")
        empty_pops = ComparisonBlock(kind="populations", available=False)
        empty_ancestry = ComparisonBlock(kind="ancestry", available=False)
        try:
            summary, index = parse_vcf(source, preview_limit=self.settings.variant_preview_limit)
        except Exception as exc:  # noqa: BLE001
            return AnalysisResult(
                ok=False,
                source_filename=source_name,
                vcf=None,
                hominin=ComparisonBlock(kind="hominin", available=False, notes=[str(exc)]),
                caste=ComparisonBlock(kind="caste", available=False),
                populations=empty_pops,
                ancestry=empty_ancestry,
                haplogroups=HaplogroupResult(available=False, notes=[str(exc)]),
                community_ref=ComparisonBlock(kind="community_ref", available=False, notes=[str(exc)]),
                relatedness=RelatednessResult(available=False, notes=[str(exc)]),
                errors=[f"Failed to parse VCF: {exc}"],
            )

        if filename:
            source_name = filename
        detect_assembly(summary, assume=self.settings.assume_assembly)
        index = self._maybe_lift(summary, index)
        panel = self.panel
        hominin = (
            compare_hominin(index, panel=panel, settings=self.settings)
            if do_hominin
            else ComparisonBlock(kind="hominin", available=False, notes=["Hominin comparison disabled."])
        )
        caste = (
            compare_caste(index, panel=panel, settings=self.settings)
            if do_caste
            else ComparisonBlock(kind="caste", available=False, notes=["Caste comparison disabled."])
        )
        populations = (
            compare_populations(index, panel=panel, settings=self.settings)
            if do_pops
            else ComparisonBlock(kind="populations", available=False, notes=["Population comparison disabled."])
        )
        ancestry = (
            compare_ancestry(index, panel=panel, settings=self.settings)
            if do_ancestry
            else ComparisonBlock(kind="ancestry", available=False, notes=["Ancestry comparison disabled."])
        )
        haplogroups = (
            compare_haplogroups(index, settings=self.settings)
            if do_haplo
            else HaplogroupResult(available=False, notes=["Haplogroup comparison disabled."])
        )
        relatedness = self._compare_other(
            summary,
            index,
            other_source,
            other_filename,
            source_name,
        )
        community_ref = score_community_reference(
            ancestry if do_ancestry else None,
            haplogroups if do_haplo else None,
            caste=caste if do_caste else None,
            filename=source_name,
            settings=self.settings,
        )
        note = assembly_note(summary)
        if note:
            hominin.notes = [note] + list(hominin.notes)
            caste.notes = [note] + list(caste.notes)
            populations.notes = [note] + list(populations.notes)
            ancestry.notes = [note] + list(ancestry.notes)
            haplogroups.notes = [note] + list(haplogroups.notes)
            relatedness.notes = [note] + list(relatedness.notes)
            community_ref.notes = [note] + list(community_ref.notes)
        return AnalysisResult(
            ok=True,
            source_filename=source_name,
            vcf=summary,
            hominin=hominin,
            caste=caste,
            populations=populations,
            ancestry=ancestry,
            haplogroups=haplogroups,
            community_ref=community_ref,
            relatedness=relatedness,
        )

    def _maybe_lift(self, summary, index: dict[tuple[str, int], dict]) -> dict[tuple[str, int], dict]:
        if summary.assembly != "GRCh38":
            return index
        chain_path = ensure_hg38_to_hg19_chain(
            self.settings.liftover_chain,
            download=self.settings.auto_download_chain,
        )
        if chain_path is None:
            return index
        try:
            if self._chain is None:
                self._chain = load_chain(chain_path)
            lifted, stats = lift_query_index(index, self._chain)
        except (OSError, ValueError):
            return index
        summary.lifted_to = "GRCh37"
        summary.n_lifted = int(stats["n_lifted"])
        summary.n_unmapped = int(stats["n_unmapped"])
        summary.preview = preview_rows(lifted, self.settings.variant_preview_limit)
        return lifted

    def _compare_other(
        self,
        summary,
        index: dict[tuple[str, int], dict],
        other_source: Path | str | TextIO | BinaryIO | None,
        other_filename: str | None,
        query_filename: str,
    ) -> RelatednessResult:
        if other_source is None:
            return RelatednessResult(
                available=False,
                query_sample_id=summary.sample_id,
                notes=["No second VCF uploaded. Add a parent, relative, or any other SNP VCF to estimate closeness."],
            )
        other_name = other_filename or (
            Path(other_source).name if isinstance(other_source, (str, Path)) else "other.vcf"
        )
        try:
            other_summary, other_index = parse_vcf(
                other_source, preview_limit=self.settings.variant_preview_limit
            )
        except Exception as exc:  # noqa: BLE001
            return RelatednessResult(
                available=False,
                other_filename=other_name,
                query_sample_id=summary.sample_id,
                notes=[f"Failed to parse second VCF: {exc}"],
            )
        detect_assembly(other_summary, assume=self.settings.assume_assembly)
        other_index = self._maybe_lift(other_summary, other_index)
        return compare_relatedness(
            index,
            other_index,
            other_filename=other_name,
            other_sample_id=other_summary.sample_id,
            query_sample_id=summary.sample_id,
            query_filename=query_filename,
            query_assembly=summary.assembly,
            other_assembly=other_summary.assembly,
            query_lifted_to=summary.lifted_to,
            other_lifted_to=other_summary.lifted_to,
        )
