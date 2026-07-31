/* ============================================================
   ForensicAI — Frontend Logic
   Handles upload, analysis, and results rendering
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  // ---- Element References ----
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('file-input');
  const previewArea = document.getElementById('preview-area');
  const previewImg = document.getElementById('preview-img');
  const analyzeBtn = document.getElementById('analyze-btn');

  const uploadSection = document.getElementById('upload-section');
  const loadingSection = document.getElementById('loading-section');
  const resultsSection = document.getElementById('results-section');

  const verdictCard = document.getElementById('verdict-card');
  const verdictIcon = document.getElementById('verdict-icon');
  const verdictText = document.getElementById('verdict-text');
  const confidenceFill = document.getElementById('confidence-fill');
  const confidencePct = document.getElementById('confidence-pct');

  const voteRealScore = document.getElementById('vote-real-score');
  const voteEditedScore = document.getElementById('vote-edited-score');
  const voteAiScore = document.getElementById('vote-ai-score');

  const originalImg = document.getElementById('original-img');
  const elaImg = document.getElementById('ela-img');

  const resetBtn = document.getElementById('reset-btn');

  let selectedFile = null;

  // ---- Drag & Drop ----
  ['dragenter', 'dragover'].forEach(evt => {
    dropZone.addEventListener(evt, e => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(evt => {
    dropZone.addEventListener(evt, e => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.remove('dragover');
    });
  });

  dropZone.addEventListener('drop', e => {
    const files = e.dataTransfer.files;
    if (files.length) handleFile(files[0]);
  });

  // ---- Click to browse ----
  dropZone.addEventListener('click', () => fileInput.click());
  dropZone.addEventListener('keydown', e => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      fileInput.click();
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length) handleFile(fileInput.files[0]);
  });

  // ---- Handle File ----
  function handleFile(file) {
    if (!file.type.startsWith('image/')) {
      alert('Please select a valid image file.');
      return;
    }

    if (file.size > 16 * 1024 * 1024) {
      alert('File is too large. Maximum size is 16 MB.');
      return;
    }

    selectedFile = file;

    const reader = new FileReader();
    reader.onload = e => {
      previewImg.src = e.target.result;
      previewArea.classList.remove('hidden');
      // Scroll to preview
      previewArea.scrollIntoView({ behavior: 'smooth', block: 'center' });
    };
    reader.readAsDataURL(file);
  }

  // ---- Analyze ----
  analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    analyzeBtn.disabled = true;
    uploadSection.classList.add('hidden');
    loadingSection.classList.remove('hidden');

    // Animate loading steps
    animateLoadingSteps();

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
      const response = await fetch('/analyze', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Analysis failed');
      }

      loadingSection.classList.add('hidden');
      showResults(data);
    } catch (err) {
      loadingSection.classList.add('hidden');
      uploadSection.classList.remove('hidden');
      analyzeBtn.disabled = false;
      alert('Error: ' + err.message);
    }
  });

  // ---- Animate Loading Steps ----
  function animateLoadingSteps() {
    const steps = document.querySelectorAll('.loading-step');
    steps.forEach(s => {
      s.classList.remove('active', 'done');
    });

    const delays = [0, 500, 1000, 1500, 2000];
    steps.forEach((step, i) => {
      setTimeout(() => {
        // Mark previous steps as done
        for (let j = 0; j < i; j++) {
          steps[j].classList.remove('active');
          steps[j].classList.add('done');
        }
        step.classList.add('active');
      }, delays[i]);
    });
  }

  // ---- Show Results ----
  function showResults(data) {
    resultsSection.classList.remove('hidden');

    // Scroll to results
    setTimeout(() => {
      resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);

    // Verdict
    verdictCard.classList.remove('verdict-real', 'verdict-edited', 'verdict-ai');

    const verdictMap = {
      REAL: { icon: '✅', text: 'Authentic Image', cls: 'verdict-real' },
      EDITED: { icon: '✏️', text: 'Edited / Forged Image', cls: 'verdict-edited' },
      AI_GENERATED: { icon: '🤖', text: 'AI-Generated Image', cls: 'verdict-ai' },
    };

    const v = verdictMap[data.verdict] || verdictMap.REAL;
    verdictIcon.textContent = v.icon;
    verdictText.textContent = v.text;
    verdictCard.classList.add(v.cls);

    // Confidence bar animation
    confidenceFill.style.width = '0%';
    confidencePct.textContent = '0%';
    setTimeout(() => {
      confidenceFill.style.width = data.confidence + '%';
      animateCounter(confidencePct, 0, data.confidence, 1200);
    }, 200);

    // Vote distribution
    const votes = data.votes || {};
    voteRealScore.textContent = (votes.REAL || 0).toFixed(1) + '%';
    voteEditedScore.textContent = (votes.EDITED || 0).toFixed(1) + '%';
    voteAiScore.textContent = (votes.AI_GENERATED || 0).toFixed(1) + '%';

    // Images
    const ts = Date.now();
    if (data.original_image_url) {
      originalImg.src = data.original_image_url + '?t=' + ts;
    }
    if (data.ela_image_url) {
      elaImg.src = data.ela_image_url + '?t=' + ts;
    }

    // Detail cards
    const details = data.details || {};
    populateDetails('ela', details.ela);
    populateDetails('metadata', details.metadata);
    populateDetails('noise', details.noise);
    populateDetails('frequency', details.frequency);
    populateDetails('texture', details.texture);
  }

  // ---- Populate Detail Cards ----
  function populateDetails(moduleId, moduleData) {
    const container = document.getElementById(moduleId + '-details');
    if (!container || !moduleData) return;

    container.innerHTML = '';

    // Module verdict badge
    if (moduleData.verdict) {
      const row = createMetricRow('Module Verdict', '');
      const badge = document.createElement('span');
      badge.className = 'metric-verdict ' + getVerdictClass(moduleData.verdict);
      badge.textContent = formatVerdict(moduleData.verdict);
      row.querySelector('.metric-value').replaceWith(badge);
      container.appendChild(row);
    }

    // Confidence
    if (moduleData.confidence !== undefined) {
      container.appendChild(createMetricRow('Confidence', moduleData.confidence + '%'));
    }

    // Metrics
    const metrics = moduleData.metrics || {};
    for (const [key, value] of Object.entries(metrics)) {
      const label = formatMetricName(key);
      const val = typeof value === 'boolean' ? (value ? '✅ Yes' : '❌ No') : String(value);
      container.appendChild(createMetricRow(label, val));
    }
  }

  function createMetricRow(label, value) {
    const row = document.createElement('div');
    row.className = 'metric-row';
    row.innerHTML = `
      <span class="metric-label">${label}</span>
      <span class="metric-value">${value}</span>
    `;
    return row;
  }

  // ---- Detail Card Toggle ----
  document.querySelectorAll('.detail-header').forEach(header => {
    header.addEventListener('click', () => {
      const card = header.closest('.detail-card');
      const isOpen = card.classList.contains('open');

      // Close all
      document.querySelectorAll('.detail-card').forEach(c => c.classList.remove('open'));

      // Toggle current
      if (!isOpen) {
        card.classList.add('open');
        header.setAttribute('aria-expanded', 'true');
      } else {
        header.setAttribute('aria-expanded', 'false');
      }
    });
  });

  // ---- Reset ----
  resetBtn.addEventListener('click', () => {
    resultsSection.classList.add('hidden');
    uploadSection.classList.remove('hidden');
    previewArea.classList.add('hidden');
    previewImg.src = '';
    fileInput.value = '';
    selectedFile = null;
    analyzeBtn.disabled = false;
    confidenceFill.style.width = '0%';

    // Close all detail cards
    document.querySelectorAll('.detail-card').forEach(c => c.classList.remove('open'));

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  // ---- Helpers ----
  function formatMetricName(str) {
    return str
      .replace(/_/g, ' ')
      .replace(/\b\w/g, c => c.toUpperCase())
      .replace(/Pct\b/, '%')
      .replace(/Std\b/, 'Std Dev');
  }

  function formatVerdict(verdict) {
    const map = {
      REAL: 'Real',
      EDITED: 'Edited',
      AI_GENERATED: 'AI Generated',
    };
    return map[verdict] || verdict;
  }

  function getVerdictClass(verdict) {
    const map = {
      REAL: 'real',
      EDITED: 'edited',
      AI_GENERATED: 'ai',
    };
    return map[verdict] || '';
  }

  function animateCounter(element, start, end, duration) {
    const startTime = performance.now();
    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease out
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = start + (end - start) * eased;
      element.textContent = current.toFixed(1) + '%';
      if (progress < 1) {
        requestAnimationFrame(update);
      }
    }
    requestAnimationFrame(update);
  }
});
