// static/app.js

document.addEventListener("DOMContentLoaded", () => {
  const autoForm = document.getElementById("auto-form");
  const manualForm = document.getElementById("manual-form");
  const modeButtons = document.querySelectorAll(".mode-btn");

  const blendOutput = document.getElementById("blend-output");
  const noResults = document.getElementById("no-results");
  const tableBody = document.getElementById("fruits-table-body");

  const sugarEl = document.getElementById("metric-sugar");
  const co2El = document.getElementById("metric-co2");
  const abvEl = document.getElementById("metric-abv");
  const safetyEl = document.getElementById("metric-safety");
  const costEl = document.getElementById("metric-cost");
  const safetyDetailEl = document.getElementById("metric-safety-detail");
  const recipeSummaryEl = document.getElementById("recipe-summary");

  const fruitSelects = [
    document.getElementById("fruit1"),
    document.getElementById("fruit2"),
    document.getElementById("fruit3"),
    document.getElementById("fruit4"),
  ];

  // --- Mode toggle ---
  modeButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const mode = btn.dataset.mode;
      modeButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      if (mode === "auto") {
        autoForm.classList.remove("hidden");
        manualForm.classList.add("hidden");
      } else {
        manualForm.classList.remove("hidden");
        autoForm.classList.add("hidden");
      }
    });
  });

  // --- Fetch metadata (fruits) ---
  fetch("/api/metadata")
    .then(res => res.json())
    .then(data => {
      const fruits = data.fruits || [];
      fruitSelects.forEach(sel => {
        sel.innerHTML = '<option value="">(none)</option>';
        fruits.forEach(name => {
          const opt = document.createElement("option");
          opt.value = name;
          opt.textContent = name;
          sel.appendChild(opt);
        });
      });
    })
    .catch(err => {
      console.error("Failed to load fruit metadata", err);
    });

  // --- Auto form submit ---
  autoForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      sweetness: autoForm.sweetness.value,
      tartness: autoForm.tartness.value,
      style: autoForm.style.value,
      batch_l: autoForm["auto-batch_l"].value,
      juice_ml_per_L: autoForm["auto-juice_ml_per_L"].value,
    };

    try {
      const res = await fetch("/api/suggest/auto", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error("Server error");
      const data = await res.json();
      renderResults(data, "auto");
    } catch (err) {
      console.error(err);
      alert("Something went wrong while generating the auto blend.");
    }
  });

  // --- Manual form submit ---
  manualForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      fruit1: manualForm.fruit1.value,
      fruit2: manualForm.fruit2.value,
      fruit3: manualForm.fruit3.value,
      fruit4: manualForm.fruit4.value,
      pct1: manualForm.pct1.value,
      pct2: manualForm.pct2.value,
      pct3: manualForm.pct3.value,
      pct4: manualForm.pct4.value,
      batch_l: manualForm["manual-batch_l"].value,
      juice_ml_per_L: manualForm["manual-juice_ml_per_L"].value,
      temp_C: manualForm.temp_C.value,
    };

    try {
      const res = await fetch("/api/suggest/manual", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error("Server error");
      const data = await res.json();
      renderResults(data, "manual");
    } catch (err) {
      console.error(err);
      alert("Something went wrong while calculating the manual blend.");
    }
  });

  function renderResults(data, mode) {
    noResults.style.display = "none";
    blendOutput.classList.remove("hidden");
    tableBody.innerHTML = "";

    (data.fruits || []).forEach((f) => {
      const tr = document.createElement("tr");
      const pct = f.pct != null ? (f.pct * 100).toFixed(0) : "";
      const mlL = f.juice_ml_per_L != null ? f.juice_ml_per_L.toFixed(1) : "";
      const mlBatch = f.juice_ml_batch != null ? f.juice_ml_batch.toFixed(1) : "";

      tr.innerHTML = `
        <td>${f.name}</td>
        <td>${pct}%</td>
        <td>${mlL}</td>
        <td>${mlBatch}</td>
      `;
      tableBody.appendChild(tr);
    });

    sugarEl.textContent = (data.sugar_g_per_L ?? 0).toFixed(2);
    co2El.textContent = (data.co2_vols ?? 0).toFixed(2);
    abvEl.textContent = (data.abv_percent ?? 0).toFixed(3);
    safetyEl.textContent = data.safety_flag || "";

    if (data.cost_estimate != null) {
      costEl.textContent = `Estimated ingredient cost for this batch: ~₹${data.cost_estimate}`;
    } else {
      costEl.textContent = "";
    }

    if (data.safety_detail) {
      const sd = data.safety_detail;
      safetyDetailEl.textContent =
        `At ~${(data.sugar_g_per_L || 0).toFixed(1)} g/L sugar and ${sd.temp_C}°C, ` +
        `keep warm for max ~${sd.max_hours} hours (${sd.risk}) before chilling.`;
    } else {
      safetyDetailEl.textContent = "";
    }

    const fruitsList = (data.fruits || [])
      .map((f) => `${(f.pct * 100).toFixed(0)}% ${f.name}`)
      .join(", ");

    recipeSummaryEl.textContent =
      `For a ${data.batch_l} L batch with ${data.juice_ml_per_L} ml juice per L: ` +
      `use ${fruitsList}. Follow your ginger bug + lemon SOP for water and culture. ` +
      `Blend gives about ${data.sugar_g_per_L.toFixed(1)} g/L sugar, ` +
      `${data.co2_vols.toFixed(1)} vols CO₂ and ~${data.abv_percent.toFixed(2)}% ABV (max).`;
  }
});
