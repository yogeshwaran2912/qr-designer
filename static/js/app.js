/**
 * QR ART STUDIO - Frontend Application Controller
 * Handles image selection/upload, URL validation, style selection,
 * before/after split slider, and scannability verification display.
 */

document.addEventListener("DOMContentLoaded", () => {
  // State
  const state = {
    selectedFilename: null,
    selectedImageUrl: null,
    url: "https://www.google.com",
    style: "fantasy",
    opacity: 0.85,
    contrast: 1.15,
    brightness: 1.05,
    moduleColor: "#0f172a",
    errorCorrection: "H",
    isGenerating: false,
    sliderPos: 50, // 0 to 100
    isDraggingSlider: false,
    viewMode: "compare" // "compare", "result", "original"
  };

  // DOM Elements
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");
  const inputChipsList = document.getElementById("inputChipsList");
  const refreshInputsBtn = document.getElementById("refreshInputsBtn");
  const selectedImageCard = document.getElementById("selectedImageCard");
  const selectedImageThumb = document.getElementById("selectedImageThumb");
  const selectedImageName = document.getElementById("selectedImageName");
  const selectedImageMeta = document.getElementById("selectedImageMeta");

  const urlInput = document.getElementById("urlInput");
  const urlValidationIcon = document.getElementById("urlValidationIcon");
  const urlChips = document.querySelectorAll(".url-chip");

  const styleCards = document.querySelectorAll(".style-card");
  const fineTuningToggle = document.getElementById("fineTuningToggle");
  const fineTuningBody = document.getElementById("fineTuningBody");

  const opacitySlider = document.getElementById("opacitySlider");
  const opacityVal = document.getElementById("opacityVal");
  const contrastSlider = document.getElementById("contrastSlider");
  const contrastVal = document.getElementById("contrastVal");
  const brightnessSlider = document.getElementById("brightnessSlider");
  const brightnessVal = document.getElementById("brightnessVal");
  const moduleColorPicker = document.getElementById("moduleColorPicker");
  const swatchBtns = document.querySelectorAll(".swatch-btn");
  const eccSelect = document.getElementById("eccSelect");

  const generateBtn = document.getElementById("generateBtn");
  const btnSpinner = document.getElementById("btnSpinner");

  // Output / Preview Elements
  const validationBanner = document.getElementById("validationBanner");
  const statusBadge = document.getElementById("statusBadge");
  const statusText = document.getElementById("statusText");
  const engineBadge = document.getElementById("engineBadge");
  const engineText = document.getElementById("engineText");
  const decodedUrlLink = document.getElementById("decodedUrlLink");
  const copyUrlBtn = document.getElementById("copyUrlBtn");

  const comparisonContainer = document.getElementById("comparisonContainer");
  const resultImage = document.getElementById("resultImage");
  const originalImage = document.getElementById("originalImage");
  const compareOverlay = document.getElementById("compareOverlay");
  const compareHandle = document.getElementById("compareHandle");
  const stageMeta = document.getElementById("stageMeta");

  const viewCompareBtn = document.getElementById("viewCompareBtn");
  const viewResultBtn = document.getElementById("viewResultBtn");
  const viewOriginalBtn = document.getElementById("viewOriginalBtn");

  const downloadPngBtn = document.getElementById("downloadPngBtn");
  const downloadJpgBtn = document.getElementById("downloadJpgBtn");

  // CV Analysis Elements
  const cvTabBtns = document.querySelectorAll(".cv-tab-btn");
  const cvTabContents = document.querySelectorAll(".cv-tab-content");
  const metricDimensions = document.getElementById("metricDimensions");
  const metricLuminance = document.getElementById("metricLuminance");
  const metricContrast = document.getElementById("metricContrast");
  const metricEdges = document.getElementById("metricEdges");
  const paletteChips = document.getElementById("paletteChips");
  const recommendationText = document.getElementById("recommendationText");
  const heatmapImg = document.getElementById("heatmapImg");
  const edgeImg = document.getElementById("edgeImg");

  // --- INITIALIZATION ---
  async function init() {
    setupEventListeners();
    setupSplitSlider();
    await loadInputFiles();
  }

  // --- EVENT LISTENERS ---
  function setupEventListeners() {
    // Dropzone upload
    dropzone.addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", handleFileSelect);

    dropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropzone.classList.add("dragover");
    });
    dropzone.addEventListener("dragleave", () => {
      dropzone.classList.remove("dragover");
    });
    dropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropzone.classList.remove("dragover");
      if (e.dataTransfer.files.length > 0) {
        uploadFile(e.dataTransfer.files[0]);
      }
    });

    refreshInputsBtn.addEventListener("click", loadInputFiles);

    // URL input validation & typing
    urlInput.addEventListener("input", handleUrlInput);

    urlChips.forEach((chip) => {
      chip.addEventListener("click", () => {
        urlInput.value = chip.dataset.url;
        handleUrlInput();
      });
    });

    // Style Card selection
    styleCards.forEach((card) => {
      card.addEventListener("click", () => {
        styleCards.forEach((c) => c.classList.remove("active"));
        card.classList.add("active");
        const radio = card.querySelector('input[type="radio"]');
        if (radio) {
          radio.checked = true;
          state.style = radio.value;
        }
      });
    });

    // Collapsible fine tuning
    fineTuningToggle.addEventListener("click", () => {
      const isVisible = fineTuningBody.style.display !== "none";
      fineTuningBody.style.display = isVisible ? "none" : "flex";
      const icon = fineTuningToggle.querySelector(".toggle-icon");
      if (icon) {
        icon.style.transform = isVisible ? "rotate(-90deg)" : "rotate(0deg)";
      }
    });

    // Sliders
    opacitySlider.addEventListener("input", (e) => {
      state.opacity = parseFloat(e.target.value);
      opacityVal.textContent = Math.round(state.opacity * 100) + "%";
    });

    contrastSlider.addEventListener("input", (e) => {
      state.contrast = parseFloat(e.target.value);
      contrastVal.textContent = state.contrast.toFixed(2) + "x";
    });

    brightnessSlider.addEventListener("input", (e) => {
      state.brightness = parseFloat(e.target.value);
      brightnessVal.textContent = state.brightness.toFixed(2) + "x";
    });

    moduleColorPicker.addEventListener("input", (e) => {
      state.moduleColor = e.target.value;
    });

    swatchBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        const color = btn.dataset.color;
        moduleColorPicker.value = color;
        state.moduleColor = color;
        showToast(`Module tint set to ${color}`);
      });
    });

    eccSelect.addEventListener("change", (e) => {
      state.errorCorrection = e.target.value;
    });

    // Generate CTA
    generateBtn.addEventListener("click", handleGenerate);

    // Copy URL
    copyUrlBtn.addEventListener("click", () => {
      const textToCopy = decodedUrlLink.textContent;
      navigator.clipboard.writeText(textToCopy).then(() => {
        showToast("Decoded URL copied to clipboard!");
      });
    });

    // View Toggles
    viewCompareBtn.addEventListener("click", () => setViewMode("compare"));
    viewResultBtn.addEventListener("click", () => setViewMode("result"));
    viewOriginalBtn.addEventListener("click", () => setViewMode("original"));

    // CV Analysis Tabs
    cvTabBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        cvTabBtns.forEach((b) => b.classList.remove("active"));
        cvTabContents.forEach((c) => c.classList.remove("active"));

        btn.classList.add("active");
        const tabId = btn.dataset.tab;
        if (tabId === "metrics") document.getElementById("tabMetrics").classList.add("active");
        if (tabId === "heatmap") document.getElementById("tabHeatmap").classList.add("active");
        if (tabId === "edges") document.getElementById("tabEdges").classList.add("active");
      });
    });
  }

  // --- INPUT FILES MANAGEMENT ---
  async function loadInputFiles() {
    try {
      inputChipsList.innerHTML = '<span class="loading-chips">Scanning input folder...</span>';
      const res = await fetch("/api/inputs");
      const data = await res.json();

      if (data.success && data.files.length > 0) {
        inputChipsList.innerHTML = "";
        data.files.forEach((file) => {
          const chip = document.createElement("div");
          chip.className = `input-chip ${file.filename === state.selectedFilename ? "active" : ""}`;
          chip.dataset.filename = file.filename;
          chip.dataset.url = file.url;

          chip.innerHTML = `
            <img class="chip-thumb" src="${file.url}" alt="${file.filename}">
            <span>${file.filename}</span>
            ${file.is_sample ? '<span class="sample-tag">Castle Preset</span>' : ""}
          `;

          chip.addEventListener("click", () => selectInputFile(file));
          inputChipsList.appendChild(chip);
        });

        // Auto select first file or house1.png if nothing selected
        if (!state.selectedFilename) {
          const defaultFile = data.files.find((f) => f.filename.includes("house")) || data.files[0];
          selectInputFile(defaultFile);
        }
      } else {
        inputChipsList.innerHTML = '<span class="sublabel">No images found in input/. Upload one above!</span>';
      }
    } catch (err) {
      inputChipsList.innerHTML = '<span class="sublabel">Failed to load input files.</span>';
    }
  }

  function selectInputFile(file) {
    state.selectedFilename = file.filename;
    state.selectedImageUrl = file.url;

    // Update active chip
    document.querySelectorAll(".input-chip").forEach((c) => {
      c.classList.toggle("active", c.dataset.filename === file.filename);
    });

    // Update Selected Image Card
    selectedImageThumb.src = file.url;
    selectedImageName.textContent = file.filename;
    selectedImageMeta.textContent = `${file.size_kb ? file.size_kb + " KB • " : ""}Ready for artistic QR`;
    selectedImageCard.style.display = "flex";

    // Update Original preview image
    originalImage.src = file.url;

    // Trigger analysis
    runImageAnalysis(file.filename);
  }

  function handleFileSelect(e) {
    if (e.target.files && e.target.files[0]) {
      uploadFile(e.target.files[0]);
    }
  }

  async function uploadFile(file) {
    const formData = new FormData();
    formData.append("file", file);

    showToast(`Uploading ${file.name}...`);
    try {
      const res = await fetch("/api/upload", {
        method: "POST",
        body: formData
      });
      const data = await res.json();

      if (data.success) {
        showToast("Image uploaded successfully!");
        await loadInputFiles();
        selectInputFile({
          filename: data.filename,
          url: data.file_url
        });
        if (data.analysis) {
          renderAnalysis(data.analysis);
        }
      } else {
        showToast(`Upload failed: ${data.error || "Unknown error"}`, true);
      }
    } catch (err) {
      showToast("Network error uploading file.", true);
    }
  }

  // --- COMPUTER VISION IMAGE ANALYSIS ---
  async function runImageAnalysis(filename) {
    try {
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename })
      });
      const data = await res.json();

      if (data.success && data.analysis) {
        renderAnalysis(data.analysis);
      }
    } catch (err) {
      console.error("Analysis failed:", err);
    }
  }

  function renderAnalysis(analysis) {
    metricDimensions.textContent = `${analysis.width} × ${analysis.height}`;
    metricLuminance.textContent = `${analysis.mean_brightness} / 255`;
    metricContrast.textContent = `${analysis.contrast_rms} RMS`;
    metricEdges.textContent = `${analysis.edge_density}%`;

    recommendationText.textContent = `Recommended Style: ${formatStyleName(analysis.recommended_style)} (${analysis.recommendation_reason})`;

    // Palette Chips
    paletteChips.innerHTML = "";
    if (analysis.palette && analysis.palette.length > 0) {
      analysis.palette.forEach((c) => {
        const chip = document.createElement("div");
        chip.className = "palette-chip";
        chip.title = `Click to use ${c.hex} as module color`;
        chip.innerHTML = `
          <span class="palette-color-dot" style="background: ${c.hex};"></span>
          <span class="palette-hex">${c.hex}</span>
          <span class="palette-pct">${c.percent}%</span>
        `;
        chip.addEventListener("click", () => {
          moduleColorPicker.value = c.hex;
          state.moduleColor = c.hex;
          showToast(`Module tint set to palette color: ${c.hex}`);
        });
        paletteChips.appendChild(chip);
      });
    }

    // Diagnostic Maps
    const t = new Date().getTime();
    heatmapImg.src = `${analysis.heatmap_url}?t=${t}`;
    edgeImg.src = `${analysis.edge_url}?t=${t}`;
  }

  function formatStyleName(styleKey) {
    const names = {
      classic: "Classic Artistic QR",
      image_blended: "Image-Blended QR",
      dark_overlay: "Dark Module Overlay",
      transparent: "Transparent QR Artwork",
      high_contrast: "High-Contrast QR",
      fantasy: "Creative Fantasy QR"
    };
    return names[styleKey] || styleKey;
  }

  // --- URL VALIDATION ---
  function handleUrlInput() {
    const rawUrl = urlInput.value.trim();
    state.url = rawUrl;

    if (!rawUrl) {
      urlValidationIcon.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2.5">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
      `;
      urlValidationIcon.title = "URL cannot be empty";
      return;
    }

    const isValid = /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?(\?[^\s]*)?(#[^\s]*)?$/i.test(rawUrl);

    if (isValid) {
      urlValidationIcon.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
      `;
      urlValidationIcon.title = "Valid URL format";
    } else {
      urlValidationIcon.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2.5">
          <polygon points="12 2 2 22 22 22"></polygon>
          <line x1="12" y1="9" x2="12" y2="13"></line>
          <line x1="12" y1="17" x2="12.01" y2="17"></line>
        </svg>
      `;
      urlValidationIcon.title = "Enter a valid website URL (e.g. https://www.google.com)";
    }
  }

  // --- QR ART GENERATION ---
  async function handleGenerate() {
    if (state.isGenerating) return;

    if (!state.selectedFilename) {
      showToast("Please select or upload an image first.", true);
      return;
    }

    let url = urlInput.value.trim();
    if (!url) {
      showToast("Please enter a valid website URL.", true);
      urlInput.focus();
      return;
    }

    if (!url.startsWith("http://") && !url.startsWith("https://")) {
      url = "https://" + url;
      urlInput.value = url;
    }

    // Set UI Loading State
    state.isGenerating = true;
    generateBtn.disabled = true;
    btnSpinner.style.display = "block";
    stageMeta.textContent = "Synthesizing Artistic QR Artwork & Verifying...";

    const payload = {
      filename: state.selectedFilename,
      url: url,
      style: state.style,
      opacity: state.opacity,
      contrast: state.contrast,
      brightness: state.brightness,
      module_color: state.moduleColor,
      error_correction: state.errorCorrection
    };

    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (data.success && data.data) {
        const item = data.data;

        // 1. Update Scannability Status Banner
        const isSuccess = item.status === "SUCCESS";
        statusBadge.className = `status-indicator-badge ${isSuccess ? "success" : "failed"}`;
        statusBadge.querySelector(".status-icon-check").textContent = isSuccess ? "✓" : "✗";
        statusText.textContent = `QR Validation: ${item.status}`;

        engineText.textContent = item.engine_used || "Independent QR Scanner";
        decodedUrlLink.textContent = item.decoded_url || "Failed to decode";
        decodedUrlLink.href = item.decoded_url || "#";

        // 2. Update Result Image Preview
        resultImage.src = item.qr_image_url;
        originalImage.src = item.original_image_url;

        // 3. Update Download Links
        downloadPngBtn.href = item.download_png_url;
        downloadJpgBtn.href = item.download_jpg_url;

        // 4. Update Meta
        stageMeta.textContent = `Generated in ${item.elapsed_seconds}s • ${item.style_name} • ECC ${item.level} • Ver ${item.version}`;

        // Toast feedback
        if (isSuccess) {
          showToast(`QR Art Generated & 100% Scannable!`);
        } else {
          showToast(`Warning: Validation check failed (${item.validation_details})`, true);
        }

        // Reset view to comparison
        setViewMode("compare");
      } else {
        showToast(`Generation Error: ${data.error || "Unknown error"}`, true);
        stageMeta.textContent = "Generation failed.";
      }
    } catch (err) {
      showToast("Server communication error.", true);
      stageMeta.textContent = "Error during generation.";
    } finally {
      state.isGenerating = false;
      generateBtn.disabled = false;
      btnSpinner.style.display = "none";
    }
  }

  // --- INTERACTIVE BEFORE / AFTER SPLIT SLIDER ---
  function setupSplitSlider() {
    let isDragging = false;

    function updateSlider(clientX) {
      const rect = comparisonContainer.getBoundingClientRect();
      let offsetX = clientX - rect.left;
      let percent = (offsetX / rect.width) * 100;
      percent = Math.max(0, Math.min(100, percent));

      state.sliderPos = percent;
      compareOverlay.style.clipPath = `polygon(0 0, ${percent}% 0, ${percent}% 100%, 0 100%)`;
      compareHandle.style.left = `${percent}%`;
    }

    compareHandle.addEventListener("mousedown", (e) => {
      isDragging = true;
      e.preventDefault();
    });

    comparisonContainer.addEventListener("mousedown", (e) => {
      isDragging = true;
      updateSlider(e.clientX);
    });

    window.addEventListener("mousemove", (e) => {
      if (!isDragging || state.viewMode !== "compare") return;
      updateSlider(e.clientX);
    });

    window.addEventListener("mouseup", () => {
      isDragging = false;
    });

    // Touch support for mobile/tablet
    comparisonContainer.addEventListener("touchstart", (e) => {
      isDragging = true;
      if (e.touches[0]) updateSlider(e.touches[0].clientX);
    });

    window.addEventListener("touchmove", (e) => {
      if (!isDragging || state.viewMode !== "compare") return;
      if (e.touches[0]) updateSlider(e.touches[0].clientX);
    });

    window.addEventListener("touchend", () => {
      isDragging = false;
    });
  }

  function setViewMode(mode) {
    state.viewMode = mode;
    viewCompareBtn.classList.toggle("active", mode === "compare");
    viewResultBtn.classList.toggle("active", mode === "result");
    viewOriginalBtn.classList.toggle("active", mode === "original");

    if (mode === "compare") {
      compareHandle.style.display = "block";
      compareOverlay.style.clipPath = `polygon(0 0, ${state.sliderPos}% 0, ${state.sliderPos}% 100%, 0 100%)`;
      compareHandle.style.left = `${state.sliderPos}%`;
    } else if (mode === "result") {
      // Show full QR code
      compareHandle.style.display = "none";
      compareOverlay.style.clipPath = "polygon(0 0, 0 0, 0 100%, 0 100%)";
    } else if (mode === "original") {
      // Show full Original image
      compareHandle.style.display = "none";
      compareOverlay.style.clipPath = "polygon(0 0, 100% 0, 100% 100%, 0 100%)";
    }
  }

  // --- TOAST NOTIFICATIONS ---
  function showToast(msg, isError = false) {
    const container = document.getElementById("toastContainer");
    const toast = document.createElement("div");
    toast.className = `toast ${isError ? "error" : ""}`;
    if (isError) {
      toast.style.borderColor = "var(--status-failed)";
      toast.style.color = "#fca5a5";
    }
    toast.textContent = msg;

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transition = "opacity 0.4s ease";
      setTimeout(() => toast.remove(), 400);
    }, 3200);
  }

  // Start app
  init();
});
