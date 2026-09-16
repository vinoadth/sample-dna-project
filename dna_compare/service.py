from __future__ import annotations

from pathlib import Path
from typing import BinaryIO, TextIO

from dna_compare.comparisons import compare_ancestry, compare_caste, compare_hominin, compare_populations
from dna_compare.config import Settings, default_settings
from dna_compare.eigenstrat import AadrPanel
from dna_compare.models import AnalysisResult, ComparisonBlock
from dna_compare.vcf_parser import parse_vcf


class AnalysisService:
    """Stable entry point for CLI today and FastAPI/Flask later."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or default_settings()
        self._panel: AadrPanel | None = None

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
    ) -> AnalysisResult:
        do_hominin = self.settings.compare_hominin if compare_hominin_flag is None else compare_hominin_flag
        do_caste = self.settings.compare_caste if compare_caste_flag is None else compare_caste_flag
        do_pops = (
            self.settings.compare_populations if compare_populations_flag is None else compare_populations_flag
        )
        do_ancestry = self.settings.compare_ancestry if compare_ancestry_flag is None else compare_ancestry_flag
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
                errors=[f"Failed to parse VCF: {exc}"],
            )

        if filename:
            source_name = filename
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
        return AnalysisResult(
            ok=True,
            source_filename=source_name,
            vcf=summary,
            hominin=hominin,
            caste=caste,
            populations=populations,
            ancestry=ancestry,
        )
