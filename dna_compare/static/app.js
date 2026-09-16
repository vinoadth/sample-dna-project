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
              return '<td class="num">' + fmtHgCell((row.groups || {})[name]) + "</td>";
            })
            .join("") +
          "</tr>"
        );
      })
      .join("");
    return (
      best +
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
      (errors.length
        ? '<div class="alert alert-danger">' + errors.map(escapeHtml).join(" · ") + "</div>"
        : "") +
      card(
        "Deep ancestry (qpAdm-style 3-source)",
        barRows((payload.ancestry && payload.ancestry.estimates) || [], "ancestry") +
          notesList(payload.ancestry && payload.ancestry.notes)
      ) +
      card(
        "Y haplogroups (R1a1 / M17 and others)",
        haploTable(payload.haplogroups || {}, "y") +
          markerQcTable((payload.haplogroups && payload.haplogroups.markers) || [], "Y") +
          '<h2 class="h5 mt-4">mtDNA haplogroups (M, R, U, and others)</h2>' +
          haploTable(
            {
              sample_best: payload.haplogroups && payload.haplogroups.mt_sample_best,
              rows: (payload.haplogroups && payload.haplogroups.mt_rows) || [],
            },
            "mt"
          ) +
          markerQcTable((payload.haplogroups && payload.haplogroups.mt_markers) || [], "mtDNA") +
          hgGlossary() +
          notesList(payload.haplogroups && payload.haplogroups.notes) +
          notesList(payload.haplogroups && payload.haplogroups.mt_notes)
      ) +
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

  async function loadSamples(select) {
    const res = await fetch("/api/samples");
    const data = await res.json();
    select.innerHTML = '<option value="">Choose a bundled sample…</option>';
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
    const runBtn = $("#run-btn");
    loadSamples(sampleSelect).catch(function () {
      status.textContent = "Could not list bundled samples.";
    });

    form.addEventListener("submit", async function (event) {
      event.preventDefault();
      const fileInput = $("#vcf-file");
      const sample = sampleSelect.value;
      const flags = flagsFromForm(form);
      runBtn.disabled = true;
      status.className = "form-text text-secondary mb-0 mt-2";
      status.textContent =
        "Analyzing… the first comparison against AADR can take several minutes while frequency caches are built.";
      try {
        let res;
        if (fileInput.files && fileInput.files[0]) {
          const file = fileInput.files[0];
          res = await fetch("/api/analyze?" + new URLSearchParams({
            hominin: String(flags.hominin),
            caste: String(flags.caste),
            populations: String(flags.populations),
            ancestry: String(flags.ancestry),
            haplogroups: String(flags.haplogroups),
          }).toString(), {
            method: "POST",
            headers: { "X-Filename": file.name, "Content-Type": "application/octet-stream" },
            body: file,
          });
        } else if (sample) {
          res = await fetch("/api/analyze-sample", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(Object.assign({ filename: sample }, flags)),
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
