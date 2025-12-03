// static/app.js

document.addEventListener("DOMContentLoaded", () => {
  const autoForm = document.getElementById("auto-form");
  const manualForm = document.getElementById("manual-form");
  const modeButtons = document.querySelectorAll(".mode-btn");

  const blendOutput = document.getElementById("blend-output");
  const noResults = document.getElementById("no-results");
  const tableBody = document.getElementById("fruits-table-body");
  const correctionNotification = document.getElementById("correction-notification");

  // Temperature detection elements
  const autoDetectTempBtn = document.getElementById("auto-detect-temp");
  const manualDetectTempBtn = document.getElementById("manual-detect-temp");
  const autoTempInput = document.getElementById("auto-temp_C");
  const manualTempInput = document.getElementById("temp_C");
  const autoTempStatus = document.getElementById("auto-temp-status");
  const manualTempStatus = document.getElementById("manual-temp-status");

  // Juice calculation elements
  const autoCalcJuiceBtn = document.getElementById("auto-calc-juice");
  const manualCalcJuiceBtn = document.getElementById("manual-calc-juice");
  const autoJuiceInput = document.getElementById("auto-juice_ml_per_L");
  const manualJuiceInput = document.getElementById("manual-juice_ml_per_L");
  const autoJuiceStatus = document.getElementById("auto-juice-status");
  const manualJuiceStatus = document.getElementById("manual-juice-status");
  const autoIntensitySelect = document.getElementById("auto-intensity");

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

  // Slider value display elements
  const sweetnessSlider = document.getElementById("sweetness");
  const tartnessSlider = document.getElementById("tartness");
  const sweetnessValue = document.getElementById("sweetness-value");
  const tartnessValue = document.getElementById("tartness-value");

  // Percentage inputs for manual mode
  const pct1 = document.getElementById("pct1");
  const pct2 = document.getElementById("pct2");
  const pct3 = document.getElementById("pct3");
  const pct4 = document.getElementById("pct4");
  const totalPctDisplay = document.getElementById("total-pct");

  // --- Slider value updates ---
  sweetnessSlider.addEventListener("input", () => {
    sweetnessValue.textContent = sweetnessSlider.value;
  });

  tartnessSlider.addEventListener("input", () => {
    tartnessValue.textContent = tartnessSlider.value;
  });

  // --- Percentage total calculation ---
  function updateTotalPercentage() {
    const total =
      parseFloat(pct1.value || 0) +
      parseFloat(pct2.value || 0) +
      parseFloat(pct3.value || 0) +
      parseFloat(pct4.value || 0);

    totalPctDisplay.textContent = total;

    // Change color based on total
    if (total === 100) {
      totalPctDisplay.style.color = "var(--green-primary)";
    } else {
      totalPctDisplay.style.color = "var(--amber-primary)";
    }
  }

  pct1.addEventListener("input", updateTotalPercentage);
  pct2.addEventListener("input", updateTotalPercentage);
  pct3.addEventListener("input", updateTotalPercentage);
  pct4.addEventListener("input", updateTotalPercentage);

  // Initialize total percentage display
  updateTotalPercentage();

  // --- Weather detection functions ---
  async function detectTemperature(tempInput, statusEl) {
    statusEl.textContent = "Detecting location...";
    statusEl.className = "temp-status detecting";

    try {
      // Get user's location
      const position = await new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
          reject(new Error("Geolocation not supported"));
        }
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          timeout: 30000,
          enableHighAccuracy: false
        });
      });

      const lat = position.coords.latitude;
      const lon = position.coords.longitude;

      statusEl.textContent = "Fetching weather...";

      // Get weather data
      const response = await fetch("/api/weather", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lat, lon })
      });

      const data = await response.json();

      if (data.success) {
        tempInput.value = data.temp_c;
        statusEl.textContent = `✓ ${data.location}: ${data.temp_c}°C, ${data.weather}`;
        statusEl.className = "temp-status success";
      } else {
        statusEl.textContent = `⚠ ${data.message}`;
        statusEl.className = "temp-status warning";
      }
    } catch (error) {
      console.error("Temperature detection error:", error);
      statusEl.textContent = `✗ ${error.message || "Could not detect temperature"}`;
      statusEl.className = "temp-status error";
    }
  }

  // Attach weather detection handlers
  autoDetectTempBtn.addEventListener("click", () => {
    detectTemperature(autoTempInput, autoTempStatus);
  });

  manualDetectTempBtn.addEventListener("click", () => {
    detectTemperature(manualTempInput, manualTempStatus);
  });

  // --- Juice calculation functions ---
  async function calculateJuiceAmount(fruits, intensityOrTarget, juiceInput, statusEl) {
    statusEl.textContent = "Calculating optimal juice amount...";
    statusEl.className = "juice-status calculating";

    try {
      // Determine target sugar based on intensity or use specific value
      let target_sugar_g_L = 7.0; // Default medium

      if (typeof intensityOrTarget === "string") {
        // Intensity mode (auto)
        if (intensityOrTarget === "light") target_sugar_g_L = 5.0;
        else if (intensityOrTarget === "medium") target_sugar_g_L = 7.0;
        else if (intensityOrTarget === "strong") target_sugar_g_L = 9.0;
      } else if (typeof intensityOrTarget === "number") {
        // Specific target (manual)
        target_sugar_g_L = intensityOrTarget;
      }

      const response = await fetch("/api/juice/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          fruits: fruits,
          target_sugar_g_L: target_sugar_g_L
        })
      });

      const data = await response.json();

      if (data.success) {
        juiceInput.value = data.recommended_ml_per_L;
        statusEl.textContent = `✓ ${data.reasoning}`;
        statusEl.className = "juice-status success";
      } else {
        statusEl.textContent = `⚠ ${data.reasoning}`;
        statusEl.className = "juice-status warning";
      }
    } catch (error) {
      console.error("Juice calculation error:", error);
      statusEl.textContent = `✗ Could not calculate. Using default.`;
      statusEl.className = "juice-status error";
    }
  }

  // Manual mode juice calculation - based on selected fruits
  manualCalcJuiceBtn.addEventListener("click", () => {
    const selectedFruits = [
      fruitSelects[0].value,
      fruitSelects[1].value,
      fruitSelects[2].value,
      fruitSelects[3].value
    ];
    calculateJuiceAmount(selectedFruits, 7.0, manualJuiceInput, manualJuiceStatus);
  });

  // Auto mode juice calculation - based on intensity
  autoCalcJuiceBtn.addEventListener("click", () => {
    const intensity = autoIntensitySelect.value;
    // For auto mode, we don't know fruits yet, so pass empty array
    // The backend will use default/safe calculation
    calculateJuiceAmount([], intensity, autoJuiceInput, autoJuiceStatus);
  });

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
      temp_C: autoForm["auto-temp_C"].value,
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

    // Show correction notification if percentages were auto-corrected
    if (data.pct_corrected && data.correction_message) {
      correctionNotification.classList.remove("hidden");
      correctionNotification.className = "notification notification-warning";
      correctionNotification.innerHTML = `
        <strong>⚠️ Auto-Correction Applied:</strong> ${data.correction_message}
      `;
    } else {
      correctionNotification.classList.add("hidden");
    }

    (data.fruits || []).forEach((f) => {
      const tr = document.createElement("tr");
      const pct = f.pct != null ? (f.pct * 100).toFixed(0) : "";
      const mlL = f.juice_ml_per_L != null ? f.juice_ml_per_L.toFixed(1) : "";
      const mlBatch = f.juice_ml_batch != null ? f.juice_ml_batch.toFixed(1) : "";

      // Show original percentage if it was corrected
      let pctDisplay = `${pct}%`;
      if (f.original_pct != null && data.pct_corrected) {
        const origPct = (f.original_pct * 100).toFixed(0);
        pctDisplay = `<span class="corrected-pct">${pct}%</span> <span class="original-pct">(was ${origPct}%)</span>`;
      }

      tr.innerHTML = `
        <td>${f.name}</td>
        <td>${pctDisplay}</td>
        <td>${mlL}</td>
        <td>${mlBatch}</td>
      `;
      tableBody.appendChild(tr);
    });

    // Render formulation breakdown
    if (data.formulation) {
      const form = data.formulation;
      document.getElementById("form-water").textContent = `${form.water_ml} ml`;
      document.getElementById("form-fruit-juice").textContent = `${form.total_fruit_juice_ml} ml`;
      document.getElementById("form-lemon").textContent = `${form.lemon_juice_ml} ml`;
      document.getElementById("form-ginger-bug").textContent = `${form.ginger_bug_ml} ml (${form.ginger_bug_pct}% of batch)`;
      document.getElementById("form-total").textContent = `${form.total_batch_ml} ml (${data.batch_l} L)`;

      // Show individual fruit juice breakdown
      const fruitDetailsEl = document.getElementById("fruit-juice-details");
      fruitDetailsEl.innerHTML = "";
      (data.fruits || []).forEach((f) => {
        const div = document.createElement("div");
        div.className = "fruit-juice-detail";
        div.innerHTML = `
          <span class="fruit-juice-name">• ${f.name}</span>
          <span class="fruit-juice-amount">${f.juice_ml_batch.toFixed(1)} ml</span>
        `;
        fruitDetailsEl.appendChild(div);
      });
    }

    // Render fermentation time
    if (data.ferment_time) {
      const ft = data.ferment_time;
      document.getElementById("ferment-optimal").textContent = ft.optimal_hours;
      document.getElementById("ferment-range-text").textContent =
        `Range: ${ft.min_hours} to ${ft.max_hours} hours`;

      const recEl = document.getElementById("ferment-recommendation");
      recEl.textContent = ft.recommendation;
      recEl.className = `fermentation-quality quality-${ft.quality}`;

      document.getElementById("phase-1-time").textContent = `${ft.phase_1_hours}h`;
      document.getElementById("phase-2-time").textContent = `${ft.phase_2_hours}h`;
    }

    sugarEl.textContent = (data.sugar_g_per_L ?? 0).toFixed(1);
    co2El.textContent = (data.co2_vols ?? 0).toFixed(1);
    abvEl.textContent = (data.abv_percent ?? 0).toFixed(2);
    safetyEl.textContent = data.safety_flag || "Safe";

    if (data.cost_estimate != null) {
      costEl.textContent = `$${data.cost_estimate}`;
    } else {
      costEl.textContent = "--";
    }

    if (data.safety_detail) {
      const sd = data.safety_detail;
      safetyDetailEl.textContent = `${sd.temp_C}°C • Max ${sd.max_hours}h • ${sd.risk} risk`;
    } else {
      safetyDetailEl.textContent = "--";
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
