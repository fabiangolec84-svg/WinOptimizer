/**
 * WinOptimizer v2.0 Pro - Frontend Client Engine
 * Fully connected to pywebview backend API bridge
 */

// State
const state = {
  activeTab: 'dashboard',
  lang: 'pl',
  cpuHistory: [15, 20, 18, 25, 22, 19, 15],
  ramHistory: [58, 59, 61, 60, 62, 60, 60],
  diskHistory: [65, 65, 65, 65, 65, 65, 65],
  cleanerTargets: [],
  selectedCleanerKeys: new Set(),
  storageFiles: [],
  selectedFilePaths: new Set(),
  installedApps: [],
  selectedProcPid: null
};

// ==========================================================================
// INTERNATIONALIZATION (PL / EN)
// ==========================================================================
const TRANSLATIONS = {
  pl: {
    nav: {
      dashboard: "Panel główny",
      cleaner: "Czyszczenie dysku",
      storage: "Duże i rzadkie pliki",
      gaming: "Gaming & FPS",
      profiles: "Profile Gier",
      privacy: "Debloat & Prywatność",
      startup: "Autostart",
      bloatware: "Aplikacje Systemowe",
      settings: "Ustawienia & Prawo"
    },
    topbar: {
      subtitle: "Monitoruj podzespoły w czasie rzeczywistym, zwalniaj pamięć RAM i redukuj opóźnienia w grach.",
      btn_restore: "Punkt przywracania",
      btn_explorer: "Zresetuj Explorer",
      btn_refresh: "Odśwież"
    },
    dashboard: {
      cpu_title: "PROCESOR (CPU)",
      ram_title: "PAMIĘĆ (RAM)",
      disk_title: "DYSK SYSTEMOWY (C:)",
      metric_load: "Obciążenie",
      metric_usage: "Zajętość",
      hero_title: "1-Click Game Boost",
      hero_desc: "Szybkie czyszczenie bufora RAM (Standby List), aktywacja planu Ultimate Performance i wyłączenie dławienia sieci.",
      btn_boost: "🚀 1-CLICK GAME BOOST",
      btn_ram: "Zwolnij RAM",
      chk1: "Wyższy i stabilny FPS",
      chk2: "Mniejszy input lag",
      chk3: "Brak micro-stutteringu",
      chk4: "Szybsza reakcja systemu",
      ab_title: "Auto-Boost w tle (Wykrywanie gier)",
      ab_desc: "Wykrywa uruchomienie gry (CS2, Valorant, GTA, Fortnite itp.), automatycznie czyści RAM i ustawia priorytet CPU na Wysoki.",
      ab_active: "Działa w tle",
      ab_disabled: "Wyłączony",
      proc_heading: "Procesy w tle & Użycie RAM"
    },
    settings: {
      lang_heading: "Język interfejsu / Language",
      lang_sub: "Wybierz preferowany język wyświetlania w aplikacji WinOptimizer. Zmiana jest natychmiastowa.",
      updates_heading: "Aktualizacje programu",
      updates_sub: "Automatyczne sprawdzanie nowych wydań, ulepszeń wydajności i bazy procesów gier.",
      btn_check: "Sprawdź dostępność aktualizacji"
    }
  },
  en: {
    nav: {
      dashboard: "Dashboard",
      cleaner: "Disk Cleaner",
      storage: "Large & Rare Files",
      gaming: "Gaming & FPS",
      profiles: "Game Profiles",
      privacy: "Debloat & Privacy",
      startup: "Startup Apps",
      bloatware: "System Apps",
      settings: "Settings & Legal"
    },
    topbar: {
      subtitle: "Real-time hardware monitoring, RAM standby purge, and ultra-low gaming latency.",
      btn_restore: "Restore Point",
      btn_explorer: "Restart Explorer",
      btn_refresh: "Refresh"
    },
    dashboard: {
      cpu_title: "PROCESSOR (CPU)",
      ram_title: "MEMORY (RAM)",
      disk_title: "SYSTEM DISK (C:)",
      metric_load: "Load",
      metric_usage: "Usage",
      hero_title: "1-Click Game Boost",
      hero_desc: "Standby List memory purge, Ultimate Performance power plan, and network throttling bypass.",
      btn_boost: "🚀 1-CLICK GAME BOOST",
      btn_ram: "Free RAM",
      chk1: "Higher & stable FPS",
      chk2: "Lower input latency",
      chk3: "Zero micro-stuttering",
      chk4: "Instant system response",
      ab_title: "Background Auto-Boost (Game Detection)",
      ab_desc: "Detects game launch (CS2, Valorant, GTA, Fortnite, etc.), flushes RAM and sets CPU priority to High.",
      ab_active: "Active in background",
      ab_disabled: "Disabled",
      proc_heading: "Background Processes & RAM Usage"
    },
    settings: {
      lang_heading: "Interface Language",
      lang_sub: "Select your preferred display language for WinOptimizer. Changes apply instantly.",
      updates_heading: "Software Updates",
      updates_sub: "Automatic checks for new releases, performance tweaks, and gaming definitions.",
      btn_check: "Check for updates"
    }
  }
};

function applyTranslations(lang) {
  const t = TRANSLATIONS[lang] || TRANSLATIONS.pl;
  
  // Navigation
  document.querySelectorAll('.nav-item').forEach(item => {
    const tab = item.getAttribute('data-tab');
    if (tab && t.nav[tab]) {
      const lbl = item.querySelector('.nav-label');
      if (lbl) lbl.innerText = t.nav[tab];
    }
  });

  // Topbar
  const sub = document.querySelector('.main-subtitle');
  if (sub) sub.innerText = t.topbar.subtitle;

  const btnR = document.getElementById('btn-create-restore-pt');
  if (btnR) { const s = btnR.querySelector('span'); if (s) s.innerText = t.topbar.btn_restore; }

  const btnE = document.getElementById('btn-restart-explorer');
  if (btnE) { const s = btnE.querySelector('span'); if (s) s.innerText = t.topbar.btn_explorer; }

  const btnRef = document.getElementById('btn-refresh-procs');
  if (btnRef) { const s = btnRef.querySelector('span'); if (s) s.innerText = t.topbar.btn_refresh; }

  // Metric cards
  const cardTitles = document.querySelectorAll('.metric-card .card-title');
  if (cardTitles[0]) cardTitles[0].innerText = t.dashboard.cpu_title;
  if (cardTitles[1]) cardTitles[1].innerText = t.dashboard.ram_title;
  if (cardTitles[2]) cardTitles[2].innerText = t.dashboard.disk_title;

  const cardSubs = document.querySelectorAll('.metric-sub');
  if (cardSubs[0]) cardSubs[0].innerText = t.dashboard.metric_load;
  if (cardSubs[1]) cardSubs[1].innerText = t.dashboard.metric_usage;
  if (cardSubs[2]) cardSubs[2].innerText = t.dashboard.metric_usage;

  // Hero Boost
  const heroTitle = document.querySelector('.hero-header-title h2');
  if (heroTitle) heroTitle.innerText = t.dashboard.hero_title;

  const heroDesc = document.querySelector('.hero-desc');
  if (heroDesc) heroDesc.innerText = t.dashboard.hero_desc;

  const btnBoost = document.querySelector('#btn-1click-boost span');
  if (btnBoost) btnBoost.innerText = t.dashboard.btn_boost;

  const btnRam = document.querySelector('#btn-clean-ram-quick span');
  if (btnRam) btnRam.innerText = t.dashboard.btn_ram;

  const chkItems = document.querySelectorAll('.hero-checklist li');
  if (chkItems.length >= 4) {
    chkItems[0].innerHTML = '<span class="chk-icon">&#10004;</span> ' + t.dashboard.chk1;
    chkItems[1].innerHTML = '<span class="chk-icon">&#10004;</span> ' + t.dashboard.chk2;
    chkItems[2].innerHTML = '<span class="chk-icon">&#10004;</span> ' + t.dashboard.chk3;
    chkItems[3].innerHTML = '<span class="chk-icon">&#10004;</span> ' + t.dashboard.chk4;
  }

  // Auto-Boost
  const abTitle = document.getElementById('txt-ab-title');
  if (abTitle) abTitle.innerText = t.dashboard.ab_title;

  const abDesc = document.getElementById('txt-ab-desc');
  if (abDesc) abDesc.innerText = t.dashboard.ab_desc;

  // Process table title
  const procH = document.querySelector('.proc-title h3');
  if (procH) procH.innerText = t.dashboard.proc_heading;

  // Settings
  const langH = document.getElementById('txt-lang-heading');
  if (langH) langH.innerText = t.settings.lang_heading;

  const langS = document.getElementById('txt-lang-sub');
  if (langS) langS.innerText = t.settings.lang_sub;

  const updH = document.getElementById('txt-updates-heading');
  if (updH) updH.innerText = t.settings.updates_heading;

  const updS = document.getElementById('txt-updates-sub');
  if (updS) updS.innerText = t.settings.updates_sub;

  const updBtn = document.getElementById('txt-check-updates-btn');
  if (updBtn) updBtn.innerText = t.settings.btn_check;
}

async function setLanguage(lang, persist = true) {
  state.lang = lang;
  
  document.getElementById('btn-lang-pl')?.classList.toggle('active', lang === 'pl');
  document.getElementById('btn-lang-en')?.classList.toggle('active', lang === 'en');
  
  applyTranslations(lang);
  
  if (persist) {
    const api = getApi();
    if (api && api.set_system_language) {
      await api.set_system_language(lang);
    }
  }
}

// SVG Gauge calculation
const GAUGE_CIRCUMFERENCE = 2 * Math.PI * 40; // ~251.327

function setGaugePercent(elementId, percent) {
  const el = document.getElementById(elementId);
  if (!el) return;
  const clamped = Math.max(0, Math.min(100, percent));
  const offset = GAUGE_CIRCUMFERENCE - (clamped / 100) * GAUGE_CIRCUMFERENCE;
  el.style.strokeDasharray = `${GAUGE_CIRCUMFERENCE}`;
  el.style.strokeDashoffset = `${offset}`;
}

// Generate smooth sparkline SVG path
function updateSparkline(svgId, points, isPurple = false) {
  const svg = document.getElementById(svgId);
  if (!svg) return;
  const width = 120;
  const height = 40;
  const max = 100;
  const min = 0;
  
  if (points.length < 2) return;
  
  const step = width / (points.length - 1);
  const coords = points.map((p, i) => {
    const x = i * step;
    const y = height - (p / max) * (height - 8) - 4;
    return { x, y };
  });

  let linePath = `M ${coords[0].x} ${coords[0].y}`;
  for (let i = 1; i < coords.length; i++) {
    linePath += ` L ${coords[i].x} ${coords[i].y}`;
  }

  const fillPath = `${linePath} L ${width} ${height} L 0 ${height} Z`;
  const gradId = isPurple ? 'purple-grad' : 'cyan-grad';
  const strokeColor = isPurple ? '#a855f7' : '#00d2ff';

  svg.innerHTML = `
    <defs>
      <linearGradient id="${gradId}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="${strokeColor}" stop-opacity="0.3"/>
        <stop offset="100%" stop-color="${strokeColor}" stop-opacity="0.0"/>
      </linearGradient>
    </defs>
    <path class="spark-fill" d="${fillPath}" fill="url(#${gradId})"/>
    <path class="spark-line" d="${linePath}" fill="none" stroke="${strokeColor}" stroke-width="2" stroke-linecap="round"/>
  `;
}

// Toast notification helper
function showToast(message, type = 'info', icon = '🚀') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span class="toast-icon">${icon}</span>
    <span class="toast-text">${message}</span>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(60px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Check if pywebview API is ready
function getApi() {
  if (window.pywebview && window.pywebview.api) {
    return window.pywebview.api;
  }
  return null;
}

// Helper to wait for pywebview initialization
function onApiReady(callback) {
  if (window.pywebview && window.pywebview.api) {
    callback(window.pywebview.api);
  } else {
    window.addEventListener('pywebviewready', () => {
      callback(window.pywebview.api);
    });
  }
}

// ==========================================================================
// DASHBOARD LOGIC & TELEMETRY
// ==========================================================================

async function fetchTelemetry() {
  const api = getApi();
  if (!api) return;

  try {
    const data = await api.get_dashboard_data();
    if (!data || !data.cpu) return;

    // CPU
    const cpuPct = Math.round(data.cpu.percent);
    document.getElementById('cpu-pct').innerText = `${cpuPct}%`;
    setGaugePercent('cpu-gauge', cpuPct);
    document.getElementById('cpu-footer').innerText = `${data.cpu.freq_ghz}  |  ${data.cpu.cores_info}`;
    document.getElementById('cpu-temp-val').innerText = `${data.cpu.temp}°C`;

    state.cpuHistory.push(cpuPct);
    if (state.cpuHistory.length > 8) state.cpuHistory.shift();
    updateSparkline('cpu-sparkline', state.cpuHistory, false);

    // RAM
    const ramPct = Math.round(data.ram.percent);
    document.getElementById('ram-pct').innerText = `${ramPct}%`;
    setGaugePercent('ram-gauge', ramPct);
    document.getElementById('ram-footer').innerText = data.ram.info;

    state.ramHistory.push(ramPct);
    if (state.ramHistory.length > 8) state.ramHistory.shift();
    updateSparkline('ram-sparkline', state.ramHistory, true);

    // DISK
    const diskPct = Math.round(data.disk.percent);
    document.getElementById('disk-pct').innerText = `${diskPct}%`;
    setGaugePercent('disk-gauge', diskPct);
    document.getElementById('disk-footer').innerText = data.disk.info;

    // GPU & FPS
    if (data.gpu) {
      document.getElementById('gpu-temp-val').innerText = `${data.gpu.temp}°C`;
    }
    document.getElementById('fps-val').innerText = `${data.fps || 180}`;

    // System Status Pill
    const pill = document.getElementById('system-status-pill');
    const pillText = document.getElementById('system-status-text');
    if (data.system_status) {
      pillText.innerText = data.system_status;
    }

    // Auto-Boost State
    if (data.auto_boost) {
      const chk = document.getElementById('chk-auto-boost');
      if (chk && document.activeElement !== chk) {
        chk.checked = data.auto_boost.enabled;
      }
      const badge = document.getElementById('ab-active-status');
      if (badge) {
        if (data.auto_boost.active_game) {
          badge.innerText = state.lang === 'en' ? `Boosting: ${data.auto_boost.active_game}` : `Wykryto: ${data.auto_boost.active_game}`;
          badge.className = 'badge active';
        } else if (data.auto_boost.enabled) {
          badge.innerText = state.lang === 'en' ? 'Active in background' : 'Działa w tle';
          badge.className = 'badge active';
        } else {
          badge.innerText = state.lang === 'en' ? 'Disabled' : 'Wyłączony';
          badge.className = 'badge system';
        }
      }
    }

    // Notifications from Auto-Boost daemon
    if (data.notifications && data.notifications.length > 0) {
      data.notifications.forEach(msg => {
        showToast(msg, 'success', '⚡');
      });
    }

    // Top processes table
    if (data.processes && data.processes.length > 0) {
      renderProcessTable(data.processes);
    }
  } catch (err) {
    console.error("Telemetry fetch error:", err);
  }
}

function getIconClassForProcess(name) {
  const low = name.toLowerCase();
  if (low.includes('chrome')) return 'chrome-icon';
  if (low.includes('brave')) return 'brave-icon';
  if (low.includes('discord')) return 'discord-icon';
  if (low.includes('steam')) return 'steam-icon';
  if (low.includes('antimalware') || low.includes('msmpeng')) return 'defender-icon';
  if (low.includes('explorer')) return 'explorer-icon';
  if (low.includes('memcompression') || low.includes('system')) return 'system-icon';
  return 'generic-icon';
}

function renderProcessTable(processes) {
  const tbody = document.getElementById('proc-table-body');
  if (!tbody) return;

  tbody.innerHTML = '';
  processes.forEach((proc, idx) => {
    const tr = document.createElement('tr');
    const iconClass = getIconClassForProcess(proc.name);
    const isPurple = idx % 2 === 1;
    const barClass = isPurple ? 'purple' : (idx === 0 ? 'cyan' : 'blue');
    const memPct = proc.memory_percent || Math.min(100, Math.round(proc.memory_mb / 80));
    const statusClass = proc.is_system ? 'system' : 'active';
    const statusText = proc.is_system ? 'Systemowy' : 'Aktywny';

    tr.innerHTML = `
      <td>
        <div class="proc-name-cell">
          <div class="app-icon ${iconClass}"></div>
          <span class="p-name">${proc.name}</span>
        </div>
      </td>
      <td>
        <div class="ram-usage-cell">
          <span class="ram-num">${proc.memory_str || (proc.memory_mb + ' MB')}</span>
          <div class="p-progress-track">
            <div class="p-progress-fill ${barClass}" style="width: ${Math.max(8, memPct)}%;"></div>
          </div>
        </div>
      </td>
      <td><span class="cpu-num">${proc.cpu_percent}%</span></td>
      <td>
        <svg class="spark-mini" viewBox="0 0 80 18">
          <path d="M 0 ${12 + (idx%3)*2} L 20 ${8 + (idx%4)*2} L 40 ${14 - (idx%3)*2} L 60 ${7 + (idx%2)*3} L 80 9" fill="none" stroke="${isPurple ? '#a855f7' : '#00d2ff'}" stroke-width="1.8"/>
        </svg>
      </td>
      <td style="text-align: right;">
        <div class="status-cell">
          <span class="badge ${statusClass}">${statusText}</span>
          <button class="btn-more" data-pid="${proc.pid}" title="Zakończ proces">&#8942;</button>
        </div>
      </td>
    `;

    const moreBtn = tr.querySelector('.btn-more');
    moreBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      openProcContextMenu(e, proc.pid);
    });

    tbody.appendChild(tr);
  });
}

function openProcContextMenu(e, pid) {
  state.selectedProcPid = pid;
  const menu = document.getElementById('proc-context-menu');
  menu.style.display = 'block';
  menu.style.left = `${e.clientX - 180}px`;
  menu.style.top = `${e.clientY + 5}px`;
}

document.addEventListener('click', () => {
  const menu = document.getElementById('proc-context-menu');
  if (menu) menu.style.display = 'none';
});

// Kill process
document.getElementById('ctx-kill-proc')?.addEventListener('click', async () => {
  const api = getApi();
  if (api && state.selectedProcPid) {
    const res = await api.kill_proc(state.selectedProcPid);
    showToast(res.message, res.success ? 'info' : 'warning', res.success ? '⚡' : '⚠️');
    fetchTelemetry();
  }
});

// ==========================================================================
// 1-CLICK BOOST & SAFETY BUTTONS
// ==========================================================================

document.getElementById('btn-1click-boost')?.addEventListener('click', async () => {
  const btn = document.getElementById('btn-1click-boost');
  const originalHtml = btn.innerHTML;
  btn.innerHTML = `<span>Optymalizowanie...</span>`;
  btn.disabled = true;

  const api = getApi();
  if (api) {
    try {
      const res = await api.run_1click_boost();
      showToast(res.message, 'success', '🚀');
      fetchTelemetry();
    } catch (e) {
      showToast('Nie udało się wykonać optymalizacji.', 'warning', '⚠️');
    }
  }

  btn.innerHTML = originalHtml;
  btn.disabled = false;
});

document.getElementById('btn-clean-ram-quick')?.addEventListener('click', async () => {
  const api = getApi();
  if (api) {
    const res = await api.clean_ram();
    showToast(res.message, 'success', '💾');
    fetchTelemetry();
  }
});

document.getElementById('btn-rollback-all')?.addEventListener('click', async () => {
  if (!confirm("Czy na pewno chcesz cofnąć wszystkie zmiany w rejestrze do pierwotnego stanu?")) return;
  const api = getApi();
  if (api) {
    const res = await api.rollback_all_registry();
    showToast(res.message, 'info', '🔄');
  }
});

// Auto-Boost background switch
document.getElementById('chk-auto-boost')?.addEventListener('change', async (e) => {
  const api = getApi();
  if (api && api.toggle_auto_boost) {
    const res = await api.toggle_auto_boost(e.target.checked);
    showToast(res.message, res.enabled ? 'success' : 'info', '⚡');
    const badge = document.getElementById('ab-active-status');
    if (badge) {
      badge.innerText = res.enabled ? (state.lang === 'en' ? 'Active in background' : 'Działa w tle') : (state.lang === 'en' ? 'Disabled' : 'Wyłączony');
      badge.className = res.enabled ? 'badge active' : 'badge system';
    }
  }
});

// Language selectors
document.getElementById('btn-lang-pl')?.addEventListener('click', () => setLanguage('pl', true));
document.getElementById('btn-lang-en')?.addEventListener('click', () => setLanguage('en', true));

// Software updates check
document.getElementById('btn-check-updates')?.addEventListener('click', async () => {
  const api = getApi();
  if (!api || !api.check_for_updates) return;
  const btn = document.getElementById('btn-check-updates');
  const statusBox = document.getElementById('update-status-box');
  btn.disabled = true;
  if (statusBox) {
    statusBox.style.display = 'inline';
    statusBox.style.color = '#94a3b8';
    statusBox.innerText = state.lang === 'en' ? 'Checking for updates...' : 'Sprawdzanie aktualizacji...';
  }
  try {
    const res = await api.check_for_updates();
    if (statusBox) {
      statusBox.innerText = res.message;
      statusBox.style.color = res.has_update ? '#38bdf8' : '#10b981';
    }
    showToast(res.message, res.has_update ? 'info' : 'success', '🚀');
  } catch (err) {
    if (statusBox) {
      statusBox.innerText = state.lang === 'en' ? 'Check failed.' : 'Błąd sprawdzania.';
      statusBox.style.color = '#f87171';
    }
  } finally {
    btn.disabled = false;
  }
});

document.getElementById('btn-create-restore-pt')?.addEventListener('click', async () => {
  showToast("Tworzenie punktu przywracania...", "info", "🛡️");
  const api = getApi();
  if (api) {
    const res = await api.create_restore_point_action();
    showToast(res.message, res.success ? 'success' : 'warning', '🛡️');
  }
});

document.getElementById('btn-restart-explorer')?.addEventListener('click', async () => {
  const api = getApi();
  if (api) {
    const res = await api.restart_explorer_action();
    showToast(res.message, 'info', '🔄');
  }
});

document.getElementById('btn-refresh-procs')?.addEventListener('click', () => {
  fetchTelemetry();
  showToast("Odświeżono listę procesów", "info", "🔄");
});

// Window controls
document.getElementById('win-min')?.addEventListener('click', () => getApi()?.window_minimize());
document.getElementById('win-max')?.addEventListener('click', () => getApi()?.window_maximize());
document.getElementById('win-close')?.addEventListener('click', () => getApi()?.window_close());

// ==========================================================================
// NAVIGATION & TABS SWITCHER
// ==========================================================================

const navItems = document.querySelectorAll('.nav-item');
navItems.forEach(item => {
  item.addEventListener('click', () => {
    const tabName = item.getAttribute('data-tab');
    if (!tabName) return;

    navItems.forEach(n => n.classList.remove('active'));
    item.classList.add('active');

    document.querySelectorAll('.tab-view').forEach(v => v.classList.remove('active'));
    const targetView = document.getElementById(`tab-${tabName}`);
    if (targetView) targetView.classList.add('active');

    state.activeTab = tabName;
    handleTabOpened(tabName);
  });
});

function handleTabOpened(tabName) {
  if (tabName === 'cleaner') loadCleanerTab();
  else if (tabName === 'storage') loadStorageTab();
  else if (tabName === 'gaming') loadGamingTab();
  else if (tabName === 'profiles') loadProfilesTab();
  else if (tabName === 'privacy') loadPrivacyTab();
  else if (tabName === 'startup') loadStartupTab();
  else if (tabName === 'bloatware') loadBloatwareTab();
  else if (tabName === 'settings') loadSettingsTab();
}

// ==========================================================================
// TAB 2: CLEANER
// ==========================================================================

async function loadCleanerTab() {
  const api = getApi();
  if (!api) return;

  // Check open browsers
  const browsers = await api.get_open_browsers();
  const banner = document.getElementById('browser-warning-banner');
  if (browsers && browsers.length > 0) {
    banner.classList.remove('hidden');
    document.getElementById('browser-warning-text').innerText = 
      `Wykryto otwarte przeglądarki (${browsers.join(', ')}). Zamknij je dla pełnego czyszczenia cache.`;
  } else {
    banner.classList.add('hidden');
  }

  // Scan targets
  const grid = document.getElementById('cleaner-categories-grid');
  grid.innerHTML = '<div class="empty-state">Skanowanie lokalizacji...</div>';

  const targets = await api.scan_cleaner_targets();
  state.cleanerTargets = targets;
  renderCleanerTargets();
}

function renderCleanerTargets() {
  const grid = document.getElementById('cleaner-categories-grid');
  grid.innerHTML = '';
  state.selectedCleanerKeys.clear();

  let list = [];
  if (Array.isArray(state.cleanerTargets)) {
    list = state.cleanerTargets;
  } else if (state.cleanerTargets && state.cleanerTargets.categories) {
    list = Object.entries(state.cleanerTargets.categories).map(([k, v]) => ({
      key: k,
      name: v.name || k,
      desc: v.desc || '',
      size_bytes: v.size || 0,
      size_str: v.size_str || '0 B',
      default_check: true
    }));
  }

  let totalBytes = 0;

  list.forEach(t => {
    const isChecked = t.default_check !== undefined ? t.default_check : true;
    if (isChecked) {
      state.selectedCleanerKeys.add(t.key);
      totalBytes += (t.size_bytes || 0);
    }

    const card = document.createElement('div');
    card.className = 'clean-card';
    card.innerHTML = `
      <div class="clean-card-left">
        <input type="checkbox" class="clean-chk" data-key="${t.key}" ${isChecked ? 'checked' : ''}>
        <div class="clean-details">
          <span class="clean-title">${t.name}</span>
          <span class="clean-desc">${t.desc}</span>
        </div>
      </div>
      <div class="clean-size-badge">${t.size_str}</div>
    `;

    const chk = card.querySelector('.clean-chk');
    chk.addEventListener('change', () => {
      if (chk.checked) state.selectedCleanerKeys.add(t.key);
      else state.selectedCleanerKeys.delete(t.key);
      updateCleanerTotal();
    });

    card.addEventListener('click', (e) => {
      if (e.target !== chk) {
        chk.checked = !chk.checked;
        chk.dispatchEvent(new Event('change'));
      }
    });

    grid.appendChild(card);
  });

  updateCleanerTotal();
}

function updateCleanerTotal() {
  let totalBytes = 0;
  const list = Array.isArray(state.cleanerTargets) ? state.cleanerTargets : [];
  list.forEach(t => {
    if (state.selectedCleanerKeys.has(t.key)) {
      totalBytes += (t.size_bytes || 0);
    }
  });

  const mb = Math.round(totalBytes / (1024 * 1024));
  const text = mb > 1024 ? `${(mb / 1024).toFixed(2)} GB` : `${mb} MB`;
  document.getElementById('cleaner-total-selected').innerText = text;
}

document.getElementById('btn-close-browsers')?.addEventListener('click', async () => {
  const api = getApi();
  if (api) {
    const res = await api.close_all_browsers();
    showToast(res.message, 'info', '🌐');
    loadCleanerTab();
  }
});

document.getElementById('btn-scan-cleaner')?.addEventListener('click', loadCleanerTab);

document.getElementById('btn-execute-clean')?.addEventListener('click', async () => {
  const api = getApi();
  if (!api || state.selectedCleanerKeys.size === 0) {
    showToast("Zaznacz co najmniej jedną pozycję do usunięcia.", "warning", "⚠️");
    return;
  }

  const keys = Array.from(state.selectedCleanerKeys);
  const res = await api.clean_cleaner_targets(keys);
  showToast(`Zwolniono ${res.freed_str} (usunięto ${res.count} plików)`, 'success', '🧹');
  loadCleanerTab();
  fetchTelemetry();
});

// ==========================================================================
// TAB 3: STORAGE & FILE HUNTER
// ==========================================================================

function loadStorageTab() {
  // Setup sub-pills
  const pillHunter = document.getElementById('pill-file-hunter');
  const pillApps = document.getElementById('pill-app-uninstaller');
  const subHunter = document.getElementById('subview-file-hunter');
  const subApps = document.getElementById('subview-app-uninstaller');

  pillHunter.onclick = () => {
    pillHunter.classList.add('active');
    pillApps.classList.remove('active');
    subHunter.classList.add('active');
    subApps.classList.remove('active');
  };

  pillApps.onclick = () => {
    pillApps.classList.add('active');
    pillHunter.classList.remove('active');
    subApps.classList.add('active');
    subHunter.classList.remove('active');
    loadAppsList();
  };
}

document.getElementById('btn-start-storage-scan')?.addEventListener('click', async () => {
  const api = getApi();
  if (!api) return;

  const btn = document.getElementById('btn-start-storage-scan');
  const originalHtml = btn.innerHTML;
  btn.innerHTML = `<span>Skanowanie...</span>`;
  btn.disabled = true;

  const loc = document.getElementById('sel-storage-location').value;
  const minSize = document.getElementById('sel-storage-min-size').value;
  const age = document.getElementById('sel-storage-age').value;
  const cat = document.getElementById('sel-storage-category').value;

  const tbody = document.getElementById('storage-table-body');
  tbody.innerHTML = '<tr><td colspan="7" class="empty-state">Skanowanie dysku w toku...</td></tr>';

  try {
    const res = await api.scan_storage_files(loc, minSize, age, cat);
    state.storageFiles = res.files || [];
    document.getElementById('storage-file-count').innerText = res.total_count;
    document.getElementById('storage-total-size').innerText = res.total_size_str;
    renderStorageFiles();
    showToast(`Znaleziono ${res.total_count} plików (${res.total_size_str})`, 'info', '🔍');
  } catch (err) {
    showToast('Błąd podczas skanowania plików.', 'warning', '⚠️');
  } finally {
    btn.innerHTML = originalHtml;
    btn.disabled = false;
  }
});

function renderStorageFiles() {
  const tbody = document.getElementById('storage-table-body');
  tbody.innerHTML = '';
  state.selectedFilePaths.clear();

  if (state.storageFiles.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" class="empty-state">Brak plików spełniających wybrane kryteria.</td></tr>';
    return;
  }

  state.storageFiles.forEach(f => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><input type="checkbox" class="file-chk" data-path="${f.path}"></td>
      <td><strong>${f.name}</strong></td>
      <td><span class="badge active">${f.category}</span></td>
      <td><span style="font-family: var(--font-mono); color: var(--accent-cyan);">${f.size_str}</span></td>
      <td style="color: var(--text-muted);">${f.accessed_days_ago} dni temu</td>
      <td style="color: var(--text-dim); max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${f.path}">${f.path}</td>
      <td style="text-align: right;">
        <button class="btn-glass btn-sm btn-open-folder" data-path="${f.path}" title="Pokaż w folderze">📂</button>
      </td>
    `;

    const chk = tr.querySelector('.file-chk');
    chk.addEventListener('change', () => {
      if (chk.checked) state.selectedFilePaths.add(f.path);
      else state.selectedFilePaths.delete(f.path);
    });

    tr.querySelector('.btn-open-folder').addEventListener('click', (e) => {
      e.stopPropagation();
      getApi()?.open_file_in_explorer(f.path);
    });

    tbody.appendChild(tr);
  });
}

document.getElementById('chk-storage-master')?.addEventListener('change', (e) => {
  const checked = e.target.checked;
  document.querySelectorAll('.file-chk').forEach(c => {
    c.checked = checked;
    c.dispatchEvent(new Event('change'));
  });
});

document.getElementById('btn-storage-select-all')?.addEventListener('click', () => {
  const master = document.getElementById('chk-storage-master');
  master.checked = !master.checked;
  master.dispatchEvent(new Event('change'));
});

document.getElementById('btn-storage-delete-selected')?.addEventListener('click', async () => {
  const api = getApi();
  if (!api || state.selectedFilePaths.size === 0) {
    showToast("Zaznacz pliki, które chcesz usunąć.", "warning", "⚠️");
    return;
  }

  if (!confirm(`Czy na pewno chcesz bezpowrotnie usunąć ${state.selectedFilePaths.size} zaznaczonych plików?`)) return;

  const paths = Array.from(state.selectedFilePaths);
  const res = await api.delete_storage_files(paths);
  showToast(`Usunięto ${res.count} plików. Zwolniono ${res.freed_str}`, 'success', '🗑️');
  document.getElementById('btn-start-storage-scan').click();
});

// App Uninstaller
async function loadAppsList() {
  const api = getApi();
  if (!api) return;

  const tbody = document.getElementById('apps-table-body');
  tbody.innerHTML = '<tr><td colspan="5" class="empty-state">Wczytywanie listy programów...</td></tr>';

  const apps = await api.get_installed_apps();
  state.installedApps = apps || [];
  renderAppsTable(state.installedApps);
}

function renderAppsTable(apps) {
  const tbody = document.getElementById('apps-table-body');
  tbody.innerHTML = '';

  if (apps.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" class="empty-state">Brak zainstalowanych programów.</td></tr>';
    return;
  }

  apps.forEach(app => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${app.name}</strong></td>
      <td style="color: var(--text-muted);">${app.publisher || 'Nieznany'}</td>
      <td style="font-family: var(--font-mono);">${app.version || '-'}</td>
      <td style="color: var(--text-dim);">${app.install_date || '-'}</td>
      <td style="text-align: right;">
        <button class="btn-danger btn-sm btn-uninstall" title="Uruchom deinstalator">Odinstaluj</button>
      </td>
    `;

    tr.querySelector('.btn-uninstall').addEventListener('click', async () => {
      if (!confirm(`Czy chcesz uruchomić deinstalator dla "${app.name}"?`)) return;
      const api = getApi();
      if (api) {
        showToast(`Uruchamianie deinstalatora: ${app.name}...`, 'info', '🗑️');
        const res = await api.uninstall_application(app.uninstall_string);
        showToast(res.message, res.success ? 'info' : 'warning', 'ℹ️');
      }
    });

    tbody.appendChild(tr);
  });
}

document.getElementById('input-app-search')?.addEventListener('input', (e) => {
  const query = e.target.value.toLowerCase();
  const filtered = state.installedApps.filter(a => a.name.toLowerCase().includes(query) || (a.publisher && a.publisher.toLowerCase().includes(query)));
  renderAppsTable(filtered);
});

document.getElementById('btn-refresh-apps')?.addEventListener('click', loadAppsList);

// ==========================================================================
// TAB 4: GAMING & FPS TWEAKS
// ==========================================================================

async function loadGamingTab() {
  const api = getApi();
  if (!api) return;

  const tweaks = await api.get_gaming_tweaks();
  const grid = document.getElementById('gaming-tweaks-grid');
  grid.innerHTML = '';

  tweaks.forEach(tw => {
    const card = document.createElement('div');
    card.className = 'tweak-card';
    const isChecked = (tw.is_enabled ?? tw.is_active) ? true : false;
    card.innerHTML = `
      <div class="tweak-info">
        <span class="tweak-name">${tw.name}</span>
        <span class="tweak-desc">${tw.desc}</span>
      </div>
      <label class="switch">
        <input type="checkbox" class="tweak-toggle" ${isChecked ? 'checked' : ''}>
        <span class="slider"></span>
      </label>
    `;

    const toggle = card.querySelector('.tweak-toggle');
    toggle.addEventListener('change', async () => {
      const res = await api.toggle_gaming_tweak(tw.id, toggle.checked);
      showToast(res.message, res.success ? 'success' : 'warning', '⚡');
    });

    grid.appendChild(card);
  });
}

document.getElementById('btn-gaming-enable-all')?.addEventListener('click', async () => {
  const api = getApi();
  if (api) {
    const res = await api.enable_all_gaming();
    showToast(res.message, 'success', '🚀');
    loadGamingTab();
  }
});

document.getElementById('btn-gaming-restore-all')?.addEventListener('click', async () => {
  const api = getApi();
  if (api) {
    const res = await api.restore_default_gaming();
    showToast(res.message, 'info', '🔄');
    loadGamingTab();
  }
});

document.getElementById('btn-flush-dns')?.addEventListener('click', async () => {
  const api = getApi();
  if (api) {
    const res = await api.flush_dns_action();
    showToast(res.message, 'success', '🌐');
  }
});

// ==========================================================================
// TAB 5: GAME PROFILES
// ==========================================================================

async function loadProfilesTab() {
  const api = getApi();
  if (!api) return;

  const profiles = await api.get_game_profiles();
  const grid = document.getElementById('game-profiles-grid');
  grid.innerHTML = '';

  const list = Array.isArray(profiles) ? profiles : Object.values(profiles || {});
  list.forEach(prof => {
    const card = document.createElement('div');
    card.className = 'profile-card';
    const isFiveM = prof.id === 'fivem' || prof.id === 'gta_fivem' || prof.special_action === 'clean_fivem';
    let extraButton = '';
    if (isFiveM) {
      extraButton = `<button class="btn-boost-primary btn-sm btn-fivem-clean" style="margin-top: 10px;">${prof.action_label || 'Wyczyść Cache FiveM'}</button>`;
    }

    const args = prof.launch_args || prof.recommended_args || 'Standard';

    card.innerHTML = `
      <div class="tweak-info">
        <span class="tweak-name">${prof.icon ? prof.icon + ' ' : ''}${prof.name}</span>
        <span class="tweak-desc">${prof.description}</span>
        <div style="margin-top: 8px; font-size: 11px; color: var(--accent-cyan);">
          Parametry: <code>${args}</code>
        </div>
        ${prof.tips ? `<div style="margin-top: 6px; font-size: 11px; color: var(--text-dim); line-height: 1.4;">${prof.tips}</div>` : ''}
        ${extraButton}
      </div>
      <button class="btn-glass btn-sm btn-apply-profile">Zastosuj Profil</button>
    `;

    card.querySelector('.btn-apply-profile').addEventListener('click', () => {
      showToast(`Zastosowano profil: ${prof.name}`, 'success', '🎯');
    });

    if (isFiveM) {
      card.querySelector('.btn-fivem-clean')?.addEventListener('click', async () => {
        const res = await api.clean_fivem_action();
        showToast(res.message, res.success ? 'success' : 'warning', '🧹');
      });
    }

    grid.appendChild(card);
  });
}

// ==========================================================================
// TAB 6: PRIVACY & DEBLOAT
// ==========================================================================

async function loadPrivacyTab() {
  const api = getApi();
  if (!api) return;

  const tweaks = await api.get_privacy_tweaks();
  const grid = document.getElementById('privacy-tweaks-grid');
  grid.innerHTML = '';

  tweaks.forEach(tw => {
    const card = document.createElement('div');
    card.className = 'tweak-card';
    const isChecked = (tw.is_enabled ?? tw.is_active) ? true : false;
    card.innerHTML = `
      <div class="tweak-info">
        <span class="tweak-name">${tw.name}</span>
        <span class="tweak-desc">${tw.desc}</span>
      </div>
      <label class="switch">
        <input type="checkbox" class="tweak-toggle" ${isChecked ? 'checked' : ''}>
        <span class="slider"></span>
      </label>
    `;

    const toggle = card.querySelector('.tweak-toggle');
    toggle.addEventListener('change', async () => {
      const res = await api.toggle_privacy_tweak(tw.id, toggle.checked);
      showToast(res.message, res.success ? 'success' : 'warning', '🛡️');
    });

    grid.appendChild(card);
  });
}

document.getElementById('btn-privacy-disable-all')?.addEventListener('click', async () => {
  const api = getApi();
  if (api) {
    const res = await api.disable_all_privacy();
    showToast(res.message, 'success', '🛡️');
    loadPrivacyTab();
  }
});

// ==========================================================================
// TAB 7: AUTOSTART
// ==========================================================================

async function loadStartupTab() {
  const api = getApi();
  if (!api) return;

  const items = await api.get_startup_items();
  const tbody = document.getElementById('startup-table-body');
  tbody.innerHTML = '';

  if (!items || items.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4" class="empty-state">Brak zarejestrowanych aplikacji autostartu.</td></tr>';
    return;
  }

  items.forEach(item => {
    const tr = document.createElement('tr');
    const impactClass = item.impact === 'Wysoki' ? 'system' : 'active';
    const isChecked = (item.is_enabled ?? item.enabled) ? true : false;
    tr.innerHTML = `
      <td><strong>${item.name}</strong></td>
      <td style="color: var(--text-dim); max-width: 350px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${item.command}">${item.command}</td>
      <td><span class="badge ${impactClass}">${item.impact || 'Średni'}</span></td>
      <td style="text-align: right;">
        <label class="switch">
          <input type="checkbox" class="startup-toggle" ${isChecked ? 'checked' : ''}>
          <span class="slider"></span>
        </label>
      </td>
    `;

    const toggle = tr.querySelector('.startup-toggle');
    toggle.addEventListener('change', async () => {
      const res = await api.toggle_startup_item(item.id, toggle.checked);
      showToast(res.message, res.success ? 'info' : 'warning', '⚡');
    });

    tbody.appendChild(tr);
  });
}

document.getElementById('btn-startup-disable-all')?.addEventListener('click', async () => {
  const api = getApi();
  if (api) {
    const res = await api.toggle_all_startup(false);
    showToast(res.message, 'info', '⚡');
    loadStartupTab();
  }
});

document.getElementById('btn-startup-refresh')?.addEventListener('click', loadStartupTab);

// ==========================================================================
// TAB 8: BLOATWARE
// ==========================================================================

async function loadBloatwareTab() {
  const api = getApi();
  if (!api) return;

  const apps = await api.get_bloatware_apps();
  const grid = document.getElementById('bloatware-grid');
  grid.innerHTML = '';

  const installedApps = (apps || []).filter(a => a.installed !== false);

  if (installedApps.length === 0) {
    grid.innerHTML = '<div class="empty-state">System jest czysty — brak zbędnych aplikacji bloatware.</div>';
    return;
  }

  installedApps.forEach(app => {
    const pkgName = app.package_name || app.id;
    const item = document.createElement('div');
    item.className = 'bloat-item';
    item.innerHTML = `
      <div class="bloat-info">
        <strong style="color: #ffffff;">${app.name}</strong>
        <div style="font-size: 11px; color: var(--text-dim);">${pkgName}</div>
      </div>
      <button class="btn-danger btn-sm btn-del-bloat">Odinstaluj</button>
    `;

    item.querySelector('.btn-del-bloat').addEventListener('click', async () => {
      if (!confirm(`Czy chcesz usunąć pakiet ${app.name}?`)) return;
      const res = await api.uninstall_bloatware_app(pkgName);
      showToast(res.message, res.success ? 'success' : 'warning', '📦');
      loadBloatwareTab();
    });

    grid.appendChild(item);
  });
}

// ==========================================================================
// TAB 9: SETTINGS & LEGAL
// ==========================================================================

async function loadSettingsTab(defaultSubtab = 'specs') {
  const api = getApi();
  if (!api) return;

  // Setup sub-pills
  const pills = [
    { id: 'pill-set-specs', subId: 'subview-set-specs' },
    { id: 'pill-set-privacy', subId: 'subview-set-privacy' },
    { id: 'pill-set-eula', subId: 'subview-set-eula' },
    { id: 'pill-set-licenses', subId: 'subview-set-licenses' },
    { id: 'pill-set-faq', subId: 'subview-set-faq' }
  ];

  pills.forEach(p => {
    const btn = document.getElementById(p.id);
    if (!btn) return;
    btn.onclick = () => {
      pills.forEach(x => {
        document.getElementById(x.id)?.classList.remove('active');
        document.getElementById(x.subId)?.classList.remove('active');
      });
      btn.classList.add('active');
      document.getElementById(p.subId)?.classList.add('active');
    };
  });

  // Switch to specific subtab if requested
  if (defaultSubtab && defaultSubtab !== 'specs') {
    const target = pills.find(x => x.id.includes(defaultSubtab));
    if (target) {
      document.getElementById(target.id)?.click();
    }
  }

  // Load hardware specs
  const data = await api.get_dashboard_data();
  if (data && data.cpu) {
    document.getElementById('spec-cpu').innerText = data.cpu.name || '-';
    document.getElementById('spec-gpu').innerText = (data.gpu && data.gpu.name) || '-';
    document.getElementById('spec-ram').innerText = `${data.ram.total_gb} GB RAM`;
  }

  // Load legal documents
  if (!state.legalTexts) {
    const docs = await api.get_legal_documents();
    if (docs) {
      state.legalTexts = docs;
      document.getElementById('text-privacy-policy').innerText = docs.privacy_policy || '';
      document.getElementById('text-eula').innerText = docs.eula || '';
      document.getElementById('text-licenses').innerText = docs.licenses || '';
      document.getElementById('text-faq').innerText = docs.smartscreen_faq || '';
    }
  }
}

// ==========================================================================
// FIRST-RUN ONBOARDING MODAL & CONSENT
// ==========================================================================

async function checkLegalConsent() {
  const api = getApi();
  if (!api) return;

  const status = await api.get_legal_status();
  const modal = document.getElementById('modal-onboarding');
  if (!modal) return;

  if (!status.has_consented) {
    modal.classList.remove('hidden');

    const chkEula = document.getElementById('chk-accept-eula');
    const chkRestore = document.getElementById('chk-initial-restore');
    const btnAccept = document.getElementById('btn-accept-onboarding');

    chkEula.addEventListener('change', () => {
      btnAccept.disabled = !chkEula.checked;
    });

    btnAccept.addEventListener('click', async () => {
      btnAccept.disabled = true;
      btnAccept.innerHTML = `<span>Tworzenie konfiguracji...</span>`;

      const createRestore = chkRestore.checked;
      const res = await api.accept_legal_terms(createRestore);

      modal.classList.add('hidden');
      showToast("Gotowe! Witamy w WinOptimizer.", "success", "🚀");

      if (res.restore_point) {
        showToast(res.restore_point.message, res.restore_point.success ? "success" : "warning", "🛡️");
      }
    });

    // Links to preview EULA / Privacy Policy directly from onboarding modal
    document.getElementById('link-show-eula')?.addEventListener('click', (e) => {
      e.preventDefault();
      modal.classList.add('hidden');
      document.querySelector('[data-tab="settings"]')?.click();
      loadSettingsTab('eula');
    });

    document.getElementById('link-show-privacy')?.addEventListener('click', (e) => {
      e.preventDefault();
      modal.classList.add('hidden');
      document.querySelector('[data-tab="settings"]')?.click();
      loadSettingsTab('privacy');
    });
  } else {
    modal.classList.add('hidden');
  }
}

// ==========================================================================
// INITIALIZATION
// ==========================================================================

window.addEventListener('DOMContentLoaded', () => {
  // Start telemetry loop & legal check once API is ready
  onApiReady(async (api) => {
    // Restore language preference
    try {
      if (api.get_current_language) {
        const savedLang = await api.get_current_language();
        if (savedLang) {
          setLanguage(savedLang, false);
        }
      }
    } catch (e) {
      console.error("Lang init error:", e);
    }

    // Check updates silently on start
    try {
      if (api.check_for_updates) {
        api.check_for_updates().then(updateRes => {
          if (updateRes && updateRes.has_update) {
            showToast(`Nowa wersja ${updateRes.latest_version} jest dostępna!`, 'info', '✨');
          }
        });
      }
    } catch (e) {}

    checkLegalConsent();
    fetchTelemetry();
    setInterval(fetchTelemetry, 2500);
  });
});

