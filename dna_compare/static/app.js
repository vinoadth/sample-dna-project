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
    if (!cleaned.length) return '<p class="empty">No estimates for this comparison.</p>';
    const max = Math.max.apply(
      null,
      cleaned.map(function (item) {
        return Math.abs(Number(item.percent)) || 0;
      }).concat([1])
    );
    return (
      '<div class="bars">' +
      cleaned
        .map(function (item) {
          const width = Math.max(0, Math.min(100, (Math.abs(Number(item.percent)) / max) * 100));
          return (
            '<div class="bar-row">' +
            '<span class="name" title="' +
            escapeHtml(item.name) +
            '">' +
            escapeHtml(item.name) +
            "</span>" +
            '<div class="track"><div class="fill ' +
            className +
            '" style="width:' +
            width +
            '%"></div></div>' +
            '<span class="pct">' +
            fmtPct(item.percent) +
            "</span>" +
            "</div>"
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
    if (!entries.length) return '<p class="empty">No chromosome counts.</p>';
    const max = Math.max.apply(
      null,
      entries.map(function (item) {
        return item.n;
      })
    ) || 1;
    return (
      '<div class="bars">' +
      entries
        .map(function (item) {
          const width = (item.n / max) * 100;
          return (
            '<div class="bar-row">' +
            '<span class="name">chr ' +
            escapeHtml(item.chrom) +
            "</span>" +
            '<div class="track"><div class="fill" style="width:' +
            width +
            '%"></div></div>' +
            '<span class="pct">' +
            item.n.toLocaleString() +
            "</span>" +
            "</div>"
          );
        })
        .join("") +
      "</div>"
    );
  }

  function notesList(notes) {
    if (!notes || !notes.length) return "";
    return (
      '<ul class="notes">' +
      notes
        .map(function (note) {
          return "<li>" + escapeHtml(note) + "</li>";
        })
        .join("") +
      "</ul>"
    );
  }

  function previewTable(rows) {
    if (!rows || !rows.length) return '<p class="empty">No SNP preview rows.</p>';
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
      '<div class="table-wrap"><table><thead><tr>' +
      "<th>chrom</th><th>pos</th><th>rsid</th><th>ref</th><th>alt</th><th>GT</th>" +
      "</tr></thead><tbody>" +
      body +
      "</tbody></table></div>"
    );
  }

  function renderDashboard(root, payload) {
    const vcf = payload.vcf || {};
    const errors = payload.errors || [];
    root.innerHTML =
      '<div class="kpis">' +
      '<div class="kpi"><div class="n ' +
      (payload.ok ? "ok" : "") +
      '">' +
      (payload.ok ? "ok" : "failed") +
      '</div><div class="l">' +
      escapeHtml(payload.source_filename || "") +
      "</div></div>" +
      '<div class="kpi"><div class="n">' +
      escapeHtml(vcf.sample_id || "—") +
      '</div><div class="l">sample</div></div>' +
      '<div class="kpi"><div class="n">' +
      Number(vcf.n_snps || 0).toLocaleString() +
      '</div><div class="l">SNPs parsed</div></div>' +
      '<div class="kpi"><div class="n">' +
      Number(vcf.n_non_snp_skipped || 0).toLocaleString() +
      '</div><div class="l">non-SNPs skipped</div></div>' +
      "</div>" +
      (errors.length
        ? '<p class="status error">' + errors.map(escapeHtml).join(" · ") + "</p>"
        : "") +
      '<section class="panel"><h2>Deep ancestry / Steppe</h2>' +
      barRows((payload.ancestry && payload.ancestry.estimates) || [], "ancestry") +
      notesList(payload.ancestry && payload.ancestry.notes) +
      "</section>" +
      '<div class="grid-2">' +
      '<section class="panel"><h2>Population mixture weights</h2>' +
      barRows((payload.populations && payload.populations.estimates) || [], "") +
      notesList(payload.populations && payload.populations.notes) +
      "</section>" +
      '<section class="panel"><h2>Caste / community weights</h2>' +
      barRows((payload.caste && payload.caste.estimates) || [], "") +
      notesList(payload.caste && payload.caste.notes) +
      "</section>" +
      "</div>" +
      '<div class="grid-2">' +
      '<section class="panel"><h2>Hominin comparison</h2>' +
      barRows((payload.hominin && payload.hominin.estimates) || [], "hominin") +
      notesList(payload.hominin && payload.hominin.notes) +
      "</section>" +
      '<section class="panel"><h2>SNPs by chromosome</h2>' +
      chromBars(vcf.chrom_counts || {}) +
      "</section>" +
      "</div>" +
      '<section class="panel"><h2>SNP preview</h2>' +
      previewTable(vcf.preview || []) +
      "</section>";
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
      status.className = "status";
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
          status.className = "status error";
          status.textContent = "Choose a bundled sample or upload a SNP VCF.";
          return;
        }
        const payload = await res.json();
        if (!res.ok && !payload.source_filename) {
          throw new Error(payload.error || "Analyze failed");
        }
        renderDashboard(results, payload);
        results.classList.remove("hidden");
        status.textContent = payload.ok ? "Done." : "Finished with errors.";
        if (!payload.ok) status.className = "status error";
      } catch (err) {
        status.className = "status error";
        status.textContent = err.message || String(err);
      } finally {
        runBtn.disabled = false;
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    const results = $("#results");
    if (window.ANALYSIS_PAYLOAD && results) {
      $("#live-controls") && $("#live-controls").classList.add("hidden");
      renderDashboard(results, window.ANALYSIS_PAYLOAD);
      results.classList.remove("hidden");
      return;
    }
    setupLive();
  });

  window.renderDnaDashboard = renderDashboard;
})();
