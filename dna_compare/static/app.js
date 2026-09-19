(function () {
  const MAX_BARS = 16;

  function $(sel, root) {
    return (root || document).querySelector(sel);
  }

  function fmtPct(value) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
    return Number(value).toFixed(2) + "%";
  }

  function barRows(items, className) {
    const cleaned = items
      .map(function (item) {
        return {
          name: item.population || item.label || "unknown",
          percent: item.percent,
        };
      })
      .filter(function (item) {
        return item.percent !== null && item.percent !== undefined;
      })
      .slice(0, MAX_BARS);
    if (!cleaned.length) return '<p class="text-secondary mb-0">No estimates for this comparison.</p>';
    const max = Math.max.apply(
      null,
      cleaned.map(function (item) {
        return Math.abs(Number(item.percent)) || 0;
      }).concat([1])
    );
    return (
      '<div class="d-grid gap-2">' +
      cleaned
        .map(function (item) {
          const width = Math.max(0, Math.min(100, (Math.abs(Number(item.percent)) / max) * 100));
          return (
            '<div class="row align-items-center g-2">' +
            '<div class="col-4 col-md-3 text-truncate small" title="' +
            escapeHtml(item.name) +
            '">' +
            escapeHtml(item.name) +
            "</div>" +
            '<div class="col">' +
            '<div class="progress" role="progressbar" aria-valuenow="' +
            Math.round(width) +
            '" aria-valuemin="0" aria-valuemax="100" style="height: 10px">' +
            '<div class="progress-bar ' +
            className +
            '" style="width:' +
            width +
            '%"></div></div></div>' +
            '<div class="col-auto font-monospace small">' +
            fmtPct(item.percent) +
            "</div></div>"
          );
        })
        .join("") +
      "</div>"
    );
  }

  function escapeHtml(text) {
    return String(text)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function chromOrder(chrom) {
    var key = String(chrom).replace(/^chr/i, "").toUpperCase();
    if (key === "X") return 23;
    if (key === "Y") return 24;
    if (key === "MT" || key === "M") return 25;
    var n = parseInt(key, 10);
    return Number.isFinite(n) ? n : 100;
  }

  function chromBars(counts) {
    const entries = Object.keys(counts || {})
      .map(function (chrom) {
        return { chrom: chrom, n: counts[chrom] };
      })
      .sort(function (a, b) {
        return chromOrder(a.chrom) - chromOrder(b.chrom);
      });
    if (!entries.length) return '<p class="text-secondary mb-0">No chromosome counts.</p>';
    const max = Math.max.apply(
      null,
      entries.map(function (item) {
        return item.n;
      })
    ) || 1;
    return (
      '<div class="d-grid gap-2">' +
      entries
        .map(function (item) {
          const width = (item.n / max) * 100;
          return (
            '<div class="row align-items-center g-2">' +
            '<div class="col-4 col-md-3 text-truncate small">chr ' +
            escapeHtml(item.chrom) +
            "</div>" +
            '<div class="col">' +
            '<div class="progress" role="progressbar" aria-valuenow="' +
            Math.round(width) +
            '" aria-valuemin="0" aria-valuemax="100" style="height: 10px">' +
            '<div class="progress-bar" style="width:' +
            width +
            '%"></div></div></div>' +
            '<div class="col-auto font-monospace small">' +
            item.n.toLocaleString() +
            "</div></div>"
          );
        })
        .join("") +
      "</div>"
    );
  }

  function fmtHgCell(cell) {
    if (!cell || !cell.n_called) return "—";
    const n = Number(cell.n || 0);
    const denom = Number(cell.n_called);
    if (cell.percent === null || cell.percent === undefined) return n + "/" + denom;
    return n + "/" + denom + " (" + Number(cell.percent).toFixed(0) + "%)";
  }

  const HG_STATUS_LABEL = {
    derived: "derived (yes)",
    ancestral: "ancestral (no)",
    "no-call": "no-call (SNP missing)",
    conflict: "conflict (ignore)",
    het: "het (unclear)",
    mismatch: "mismatch (unexpected allele)",
  };

  function hgStatusBadge(status) {
    const label = HG_STATUS_LABEL[status] || status;
    const cls = {
      derived: "text-bg-success",
      ancestral: "text-bg-secondary",
      "no-call": "text-bg-light",
      conflict: "text-bg-danger",
      het: "text-bg-warning",
      mismatch: "text-bg-danger",
    }[status] || "text-bg-light";
    return '<span class="badge ' + cls + '">' + escapeHtml(label) + "</span>";
  }

  function hgGlossary() {
    return (
      '<dl class="row small mb-3 p-3 bg-body-secondary rounded border">' +
      '<dt class="col-sm-2 font-monospace">derived</dt><dd class="col-sm-10">yes — this file has the mutation that defines that haplogroup</dd>' +
      '<dt class="col-sm-2 font-monospace">ancestral</dt><dd class="col-sm-10">no — this file has the older allele, so that haplogroup is ruled out</dd>' +
      '<dt class="col-sm-2 font-monospace">no-call</dt><dd class="col-sm-10">that defining SNP is missing or unreadable in this VCF</dd>' +
      '<dt class="col-sm-2 font-monospace">conflict</dt><dd class="col-sm-10">markers disagree (child looks yes, parent is no) — do not treat as a call</dd>' +
      '<dt class="col-sm-2 font-monospace">GQ</dt><dd class="col-sm-10">genotype quality from the VCF; higher is more confident (scale differs by file)</dd>' +
      '<dt class="col-sm-2 font-monospace">DP</dt><dd class="col-sm-10">sequencing read depth at that site; usually missing on SNP-array files</dd>' +
      '<dt class="col-sm-2 font-monospace">IGC</dt><dd class="col-sm-10">Illumina GenCall (0–1) on array VCFs; low IGC is weaker support</dd>' +
      "</dl>"
    );
  }

  function fmtQc(value, digits) {
    if (value === null || value === undefined || value === "") return "—";
    if (typeof value === "number" && digits !== undefined) return value.toFixed(digits);
    return String(value);
  }

  function markerQcTable(markers, label) {
    if (!markers || !markers.length) return "";
    const hasDp = markers.some(function (m) { return m.dp != null; });
    const hasIgc = markers.some(function (m) { return m.igc != null; });
    const hasGq = markers.some(function (m) { return m.gq != null; });
    const hasQual = markers.some(function (m) { return m.qual != null; });
    const head =
      "<th>Haplogroup</th><th>Marker</th><th>This sample</th>" +
      (hasGq ? "<th>GQ</th>" : "") +
      (hasDp ? "<th>DP</th>" : "") +
      (hasIgc ? "<th>IGC</th>" : "") +
      (hasQual ? "<th>QUAL</th>" : "") +
      (hasGq || hasDp || hasIgc || hasQual ? "" : "<th>quality</th>");
    const body = markers
      .map(function (row) {
        const status = row.status || "no-call";
        return (
          "<tr><td>" +
          escapeHtml(row.haplogroup) +
          "</td><td>" +
          escapeHtml(row.marker || "—") +
          "</td><td>" +
          hgStatusBadge(status) +
          "</td>" +
          (hasGq ? '<td class="num">' + fmtQc(row.gq) + "</td>" : "") +
          (hasDp ? '<td class="num">' + fmtQc(row.dp) + "</td>" : "") +
          (hasIgc ? '<td class="num">' + fmtQc(row.igc, 2) + "</td>" : "") +
          (hasQual ? '<td class="num">' + fmtQc(row.qual) + "</td>" : "") +
          (hasGq || hasDp || hasIgc || hasQual ? "" : '<td class="num">—</td>') +
          "</tr>"
        );
      })
      .join("");
    return (
      '<h3 class="h6 text-secondary mt-4">' +
      escapeHtml(label) +
      " marker quality</h3>" +
      '<div class="table-responsive"><table class="table table-sm table-striped table-hover align-middle hg-table hg-qc-table"><thead><tr>' +
      head +
      "</tr></thead><tbody>" +
      body +
      "</tbody></table></div>"
    );
  }

  function communityRefCard(block) {
    if (!block || block.hidden) {
      return "";
    }
    if (!block.available) {
      return card(
        "Tamil community reference ranges",
        '<p class="text-secondary mb-0">Need ancestry results and data/references/caste/tamil_community_reference.tsv.</p>' +
          notesList(block && block.notes)
      );
    }
    const rows = block.estimates || [];
    const body = rows
      .map(function (row) {
        const cls = row.steppe_in_range && row.aasi_in_range
          ? "table-success"
          : row.steppe_in_range
            ? "table-info"
            : row.percent >= 50
              ? "table-warning"
              : "";
        return (
          "<tr class=\"" +
          cls +
          "\"><td>" +
          escapeHtml(row.population) +
          '</td><td class="num">' +
          escapeHtml(row.ref_aasi || "—") +
          '</td><td class="num">' +
          escapeHtml(row.ref_steppe || "—") +
          '</td><td class="num">' +
          (row.sample_aasi == null ? "—" : Number(row.sample_aasi).toFixed(1) + "%") +
          '</td><td class="num">' +
          (row.sample_steppe == null ? "—" : Number(row.sample_steppe).toFixed(1) + "%") +
          "</td><td>" +
          escapeHtml(row.ref_y || "—") +
          '</td><td class="num">' +
          Number(row.percent).toFixed(0) +
          "%</td></tr>"
        );
      })
      .join("");
    return card(
      "Tamil community reference ranges",
      '<p class="small text-secondary mb-2">Fit = how close this file\'s AASI_Onge and Steppe_MLBA are to the stored published ranges. Not a caste call. Row color: both ranges match / Steppe matches / fit ≥ 50%.</p>' +
        '<div class="table-responsive"><table class="table table-sm table-striped table-hover align-middle hg-table"><thead><tr>' +
        "<th>Community</th><th>Ref AASI/ASI</th><th>Ref Steppe</th><th>This AASI</th><th>This Steppe</th><th>Ref Y (community %)</th><th>Fit</th>" +
        "</tr></thead><tbody>" +
        body +
        "</tbody></table></div>" +
        notesList(block.notes)
    );
  }

  function relatednessCard(block) {
    if (!block || !block.available) {
      if (!block || !block.other_filename) {
        return "";
      }
      return card(
        "Relatedness vs second VCF",
        '<p class="text-secondary mb-0">The second VCF was attached, but relatedness could not be estimated.</p>' +
          notesList(block.notes)
      );
    }
    const kinship = block.kinship == null ? "—" : Number(block.kinship).toFixed(3);
    const ibs = block.mean_ibs == null ? "—" : Number(block.mean_ibs).toFixed(3);
    const n = Number(block.n_snps || 0).toLocaleString();
    const rel = block.reliability || "—";
    const het =
      (block.het_rate_query == null ? "—" : Number(block.het_rate_query).toFixed(2)) +
      " / " +
      (block.het_rate_other == null ? "—" : Number(block.het_rate_other).toFixed(2));
    const matchBits = [];
    if (block.n_matched_pos) matchBits.push(Number(block.n_matched_pos).toLocaleString() + " by position");
    if (block.n_matched_rsid) matchBits.push(Number(block.n_matched_rsid).toLocaleString() + " by rsID");
    const body =
      '<p class="mb-3">Compared to <strong>' +
      escapeHtml(block.other_sample_id || block.other_filename || "second file") +
      "</strong></p>" +
      '<p class="fs-5 mb-2">' +
      escapeHtml(block.relationship || "unknown") +
      "</p>" +
      '<div class="row g-3 mb-2">' +
      kpi(kinship, "KING kinship") +
      kpi(ibs, "mean IBS") +
      kpi(n, "overlapping autosomal SNPs") +
      kpi(
        Number(block.ibs0 || 0).toLocaleString() +
          " / " +
          Number(block.ibs1 || 0).toLocaleString() +
          " / " +
          Number(block.ibs2 || 0).toLocaleString(),
        "IBS0 / IBS1 / IBS2"
      ) +
      "</div>" +
      '<div class="row g-3 mb-2">' +
      kpi(escapeHtml(rel), "call reliability") +
      kpi(het, "het rate (query / other)") +
      kpi(
        matchBits.length ? matchBits.join(" · ") : "—",
        "how SNPs were matched"
      ) +
      kpi(
        Number(block.n_qc_dropped || 0).toLocaleString(),
        "low-quality sites dropped"
      ) +
      "</div>" +
      relatednessTables(block) +
      notesList(block.notes);
    return card("Relatedness vs second VCF", body);
  }

  function relatednessBand(kinship) {
    if (kinship == null) return "";
    const k = Number(kinship);
    if (k >= 0.354) return "twin";
    if (k >= 0.177) return "first";
    if (k >= 0.088) return "second";
    if (k >= 0.044) return "cousin";
    if (k >= 0.022) return "distant";
    return "unrelated";
  }

  function relatednessTables(block) {
    const n = Number(block.n_snps || 0);
    const fmt = function (value) {
      if (value == null || Number.isNaN(Number(value))) return "—";
      return Number(value).toFixed(1) + "%";
    };
    const rows = [
      ["IBS0 (opposite homozygotes)", block.ibs0, block.ibs0_pct],
      ["IBS1 (one allele shared)", block.ibs1, block.ibs1_pct],
      ["IBS2 (both alleles shared)", block.ibs2, block.ibs2_pct],
      ["Mean IBS (allele sharing)", "—", block.mean_ibs == null ? null : 100 * Number(block.mean_ibs)],
      ["Estimated DNA shared (2 × kinship)", "—", block.shared_pct],
    ];
    const share = rows
      .map(function (row) {
        return (
          "<tr><td>" +
          escapeHtml(row[0]) +
          '</td><td class="num">' +
          (row[1] === "—" ? "—" : Number(row[1] || 0).toLocaleString()) +
          '</td><td class="num">' +
          fmt(row[2]) +
          "</td></tr>"
        );
      })
      .join("");
    const band = relatednessBand(block.kinship);
    const refs = [
      ["twin", "Same person / identical twin", "≥ 0.35", "~100%", "~0%"],
      ["first", "Parent–child or full sibling", "~0.25", "~50%", "≈0% parent–child"],
      ["second", "Second-degree (half-sib, uncle, grandparent)", "~0.13", "~25%", "low"],
      ["cousin", "Third-degree (first cousin)", "~0.06", "~12.5%", "moderate"],
      ["distant", "Fourth-degree / distant", "~0.03", "~6%", "higher"],
      ["unrelated", "Unrelated or very distant", "~0", "~0%", "highest"],
    ];
    const refBody = refs
      .map(function (row) {
        const active = row[0] === band;
        return (
          "<tr" +
          (active ? ' class="table-info"' : "") +
          "><td>" +
          escapeHtml(row[1]) +
          (active ? ' <span class="badge text-bg-info">this pair</span>' : "") +
          "</td><td>" +
          escapeHtml(row[2]) +
          "</td><td>" +
          escapeHtml(row[3]) +
          "</td><td>" +
          escapeHtml(row[4]) +
          "</td></tr>"
        );
      })
      .join("");
    return (
      '<h3 class="h6 text-secondary mt-3">Sharing on ' +
      n.toLocaleString() +
      " overlapping SNPs</h3>" +
      '<div class="table-responsive mb-3"><table class="table table-sm table-striped align-middle hg-table"><thead><tr>' +
      "<th>Metric</th><th>Count</th><th>Percentage</th></tr></thead><tbody>" +
      share +
      "</tbody></table></div>" +
      '<h3 class="h6 text-secondary">Typical ranges (KING)</h3>' +
      '<div class="table-responsive"><table class="table table-sm table-striped align-middle hg-table"><thead><tr>' +
      "<th>Relationship</th><th>Kinship</th><th>DNA shared</th><th>IBS0</th></tr></thead><tbody>" +
      refBody +
      "</tbody></table></div>"
    );
  }

  function haploCard(hg) {
    const showY = !!hg.available;
    const showMt = !!hg.mt_available;
    if (!showY && !showMt) {
      return card("Haplogroups", notesList(hg.notes) + notesList(hg.mt_notes));
    }
    const title = showY
      ? "Y haplogroups (R1a1 / M17 and others)"
      : "mtDNA haplogroups (M, R, U, and others)";
    let body = "";
    if (showY) {
      body += haploTable(hg, "y");
      body += markerQcTable(hg.markers || [], "Y");
    }
    if (showMt) {
      if (showY) body += '<h2 class="h5 mt-4">mtDNA haplogroups (M, R, U, and others)</h2>';
      body += haploTable(
        { sample_best: hg.mt_sample_best, rows: hg.mt_rows || [] },
        "mt"
      );
      body += markerQcTable(hg.mt_markers || [], "mtDNA");
    }
    if (showY || showMt) body += hgGlossary();
    body += notesList(hg.notes);
    body += notesList(hg.mt_notes);
    return card(title, body);
  }

  function hgPctClass(cell) {
    if (!cell || cell.percent === null || cell.percent === undefined) return "";
    const pct = Number(cell.percent);
    if (!(pct > 0)) return "";
    if (pct <= 25) return "table-warning";
    if (pct <= 50) return "table-info";
    if (pct <= 75) return "table-primary";
    return "table-success";
  }

  function hgPctLegend() {
    return (
      '<p class="small text-secondary mb-2">' +
      "Highlight is the AADR share in that community: " +
      '<span class="badge text-bg-warning">≤25%</span> ' +
      '<span class="badge text-bg-info">≤50%</span> ' +
      '<span class="badge text-bg-primary">≤75%</span> ' +
      '<span class="badge text-bg-success">&gt;75%</span>' +
      "</p>"
    );
  }

  function haploTable(block, kind) {
    const label = kind === "mt" ? "mtDNA" : "Y";
    const rows = (block && block.rows) || [];
    const best = block && block.sample_best
      ? '<p class="mb-3">Deepest derived ' +
        label +
        " marker in this VCF: <strong>" +
        escapeHtml(block.sample_best) +
        "</strong></p>"
      : '<p class="mb-3">No derived backbone ' +
        label +
        " marker in this VCF (or calls conflict).</p>";
    if (!rows.length) {
      return best + '<p class="text-secondary mb-0">No AADR haplogroup counts (need the .anno file).</p>';
    }
    const groups = Object.keys(rows[0].groups || {});
    const head =
      "<th>Haplogroup</th><th>Marker</th><th>This sample</th>" +
      groups
        .map(function (name) {
          return "<th>" + escapeHtml(name) + "</th>";
        })
        .join("");
    const body = rows
      .map(function (row) {
        const status = row.sample_status || "no-call";
        return (
          "<tr><td>" +
          escapeHtml(row.haplogroup) +
          "</td><td>" +
          escapeHtml(row.marker || "—") +
          "</td><td>" +
          hgStatusBadge(status) +
          "</td>" +
          groups
            .map(function (name) {
              const cell = (row.groups || {})[name];
              const extra = hgPctClass(cell);
              return (
                '<td class="num' +
                (extra ? " " + extra : "") +
                '">' +
                fmtHgCell(cell) +
                "</td>"
              );
            })
            .join("") +
          "</tr>"
        );
      })
      .join("");
    return (
      best +
      hgPctLegend() +
      '<div class="table-responsive"><table class="table table-sm table-striped table-hover align-middle hg-table"><thead><tr>' +
      head +
      "</tr></thead><tbody>" +
      body +
      "</tbody></table></div>"
    );
  }

  function notesList(notes) {
    if (!notes || !notes.length) return "";
    return (
      '<ul class="list-unstyled small text-secondary mb-0 mt-3">' +
      notes
        .map(function (note) {
          return "<li>" + escapeHtml(note) + "</li>";
        })
        .join("") +
      "</ul>"
    );
  }

  function previewTable(rows) {
    if (!rows || !rows.length) return '<p class="text-secondary mb-0">No SNP preview rows.</p>';
    const body = rows
      .slice(0, 100)
      .map(function (row) {
        return (
          "<tr><td>" +
          escapeHtml(row.chrom) +
          "</td><td>" +
          escapeHtml(row.pos) +
          "</td><td>" +
          escapeHtml(row.rsid) +
          "</td><td>" +
          escapeHtml(row.ref) +
          "</td><td>" +
          escapeHtml(row.alt) +
          "</td><td>" +
          escapeHtml(row.genotype) +
          "</td></tr>"
        );
      })
      .join("");
    return (
      '<div class="table-responsive"><table class="table table-sm table-striped table-hover align-middle"><thead><tr>' +
      "<th>chrom</th><th>pos</th><th>rsid</th><th>ref</th><th>alt</th><th>GT</th>" +
      "</tr></thead><tbody>" +
      body +
      "</tbody></table></div>"
    );
  }

  function card(title, body) {
    return (
      '<section class="card shadow-sm mb-3">' +
      '<div class="card-header fw-semibold">' +
      escapeHtml(title) +
      "</div>" +
      '<div class="card-body">' +
      body +
      "</div></section>"
    );
  }

  function kpi(value, label, valueClass) {
    return (
      '<div class="col-6 col-md-3">' +
      '<div class="card shadow-sm h-100"><div class="card-body py-3">' +
      '<div class="fs-4 fw-semibold ' +
      (valueClass || "") +
      '">' +
      value +
      '</div><div class="text-secondary small">' +
      label +
      "</div></div></div></div>"
    );
  }

  function renderDashboard(root, payload) {
    const vcf = payload.vcf || {};
    const errors = payload.errors || [];
    root.innerHTML =
      '<div class="row g-3 mb-3">' +
      kpi(
        payload.ok ? "ok" : "failed",
        escapeHtml(payload.source_filename || ""),
        payload.ok ? "text-success" : "text-danger"
      ) +
      kpi(escapeHtml(vcf.sample_id || "—"), "sample") +
      kpi(Number(vcf.n_snps || 0).toLocaleString(), "SNPs parsed") +
      kpi(Number(vcf.n_non_snp_skipped || 0).toLocaleString(), "non-SNPs skipped") +
      "</div>" +
      '<div class="row g-3 mb-3">' +
      kpi(
        escapeHtml(vcf.lifted_to ? (vcf.assembly || "?") + " → " + vcf.lifted_to : vcf.assembly || "unknown"),
        vcf.lifted_to
          ? "assembly (lifted for AADR/hg19)"
          : "assembly",
        vcf.lifted_to ? "text-success" : vcf.assembly === "GRCh38" ? "text-warning" : ""
      ) +
      kpi(Number(vcf.n_lifted || 0).toLocaleString(), "sites lifted") +
      kpi(Number(vcf.n_unmapped || 0).toLocaleString(), "unmapped in liftover") +
      "</div>" +
      (vcf.assembly === "GRCh38" && !vcf.lifted_to
        ? '<div class="alert alert-warning">This VCF looks like GRCh38 (often GSA-24v3 / gtc2vcf). Haplogroups still match by rsID and hg38 positions. Place hg38ToHg19.over.chain.gz under data/references/liftover/ so autosomal AADR sites line up.</div>'
        : "") +
      (errors.length
        ? '<div class="alert alert-danger">' + errors.map(escapeHtml).join(" · ") + "</div>"
        : "") +
      card(
        "Deep ancestry (qpAdm-style 3-source)",
        barRows((payload.ancestry && payload.ancestry.estimates) || [], "ancestry") +
          notesList(payload.ancestry && payload.ancestry.notes)
      ) +
      communityRefCard(payload.community_ref || {}) +
      relatednessCard(payload.relatedness || {}) +
      haploCard(payload.haplogroups || {}) +
      '<div class="row g-3">' +
      '<div class="col-lg-6">' +
      card(
        "Population mixture weights",
        barRows((payload.populations && payload.populations.estimates) || [], "") +
          notesList(payload.populations && payload.populations.notes)
      ) +
      "</div><div class=\"col-lg-6\">" +
      card(
        "Caste / community weights",
        barRows((payload.caste && payload.caste.estimates) || [], "") +
          notesList(payload.caste && payload.caste.notes)
      ) +
      "</div></div>" +
      '<div class="row g-3">' +
      '<div class="col-lg-6">' +
      card(
        "Hominin comparison",
        barRows((payload.hominin && payload.hominin.estimates) || [], "hominin") +
          notesList(payload.hominin && payload.hominin.notes)
      ) +
      "</div><div class=\"col-lg-6\">" +
      card("SNPs by chromosome", chromBars(vcf.chrom_counts || {})) +
      "</div></div>" +
      card("SNP preview", previewTable(vcf.preview || []));
  }

  async function loadSamples(select, emptyLabel) {
    const res = await fetch("/api/samples");
    const data = await res.json();
    select.innerHTML = "<option value=\"\">" + (emptyLabel || "Choose a bundled sample…") + "</option>";
    (data.samples || []).forEach(function (name) {
      const opt = document.createElement("option");
      opt.value = name;
      opt.textContent = name;
      select.appendChild(opt);
    });
  }

  function flagsFromForm(form) {
    return {
      hominin: form.querySelector('[name="hominin"]').checked,
      caste: form.querySelector('[name="caste"]').checked,
      populations: form.querySelector('[name="populations"]').checked,
      ancestry: form.querySelector('[name="ancestry"]').checked,
      haplogroups: !form.querySelector('[name="haplogroups"]') || form.querySelector('[name="haplogroups"]').checked,
    };
  }

  function setupLive() {
    const form = $("#analyze-form");
    if (!form) return;
    const status = $("#status");
    const results = $("#results");
    const sampleSelect = $("#sample-select");
    const otherSelect = $("#other-select");
    const runBtn = $("#run-btn");
    Promise.all([
      loadSamples(sampleSelect, "Choose a bundled sample…"),
      otherSelect ? loadSamples(otherSelect, "None — skip relatedness") : Promise.resolve(),
    ]).catch(function () {
      status.textContent = "Could not list bundled samples.";
    });

    form.addEventListener("submit", async function (event) {
      event.preventDefault();
      const fileInput = $("#vcf-file");
      const otherInput = $("#other-file");
      const sample = sampleSelect.value;
      const otherSample = otherSelect ? otherSelect.value : "";
      const flags = flagsFromForm(form);
      const primaryFile = fileInput.files && fileInput.files[0];
      const otherFile = otherInput && otherInput.files && otherInput.files[0];
      runBtn.disabled = true;
      status.className = "form-text text-secondary mb-0 mt-2";
      status.textContent =
        "Analyzing… the first comparison against AADR can take several minutes while frequency caches are built.";
      try {
        let res;
        if (primaryFile || otherFile) {
          if (!primaryFile && !sample) {
            status.className = "alert alert-danger py-2 px-3 mt-2 mb-0";
            status.textContent = "Choose a bundled sample or upload a SNP VCF.";
            return;
          }
          const fd = new FormData();
          if (primaryFile) fd.append("vcf", primaryFile);
          if (sample) fd.append("sample", sample);
          if (otherFile) fd.append("other", otherFile);
          if (otherSample) fd.append("other_sample", otherSample);
          fd.append("hominin", String(flags.hominin));
          fd.append("caste", String(flags.caste));
          fd.append("populations", String(flags.populations));
          fd.append("ancestry", String(flags.ancestry));
          fd.append("haplogroups", String(flags.haplogroups));
          res = await fetch("/api/analyze", { method: "POST", body: fd });
        } else if (sample) {
          res = await fetch("/api/analyze-sample", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(Object.assign({
              filename: sample,
              other_filename: otherSample || "",
            }, flags)),
          });
        } else {
          status.className = "alert alert-danger py-2 px-3 mt-2 mb-0";
          status.textContent = "Choose a bundled sample or upload a SNP VCF.";
          return;
        }
        const payload = await res.json();
        if (!res.ok && !payload.source_filename) {
          throw new Error(payload.error || "Analyze failed");
        }
        renderDashboard(results, payload);
        results.classList.remove("d-none");
        status.textContent = payload.ok ? "Done." : "Finished with errors.";
        if (!payload.ok) status.className = "alert alert-danger py-2 px-3 mt-2 mb-0";
      } catch (err) {
        status.className = "alert alert-danger py-2 px-3 mt-2 mb-0";
        status.textContent = err.message || String(err);
      } finally {
        runBtn.disabled = false;
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    const results = $("#results");
    if (window.ANALYSIS_PAYLOAD && results) {
      $("#live-controls") && $("#live-controls").classList.add("d-none");
      renderDashboard(results, window.ANALYSIS_PAYLOAD);
      results.classList.remove("d-none");
      return;
    }
    setupLive();
  });

  window.renderDnaDashboard = renderDashboard;
})();
