import sys
import os
import time
import json
import threading

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import webview
from core.api_bridge import ApiBridge
from core.auto_boost import auto_boost_daemon

test_summary = {
    "passed": [],
    "failed": [],
    "js_errors": [],
    "console_logs": []
}

def automated_tester(window):
    print("[TEST] Waiting for pywebview DOM and WebView2 initialization...")
    ready = False
    for attempt in range(40):
        try:
            res = window.evaluate_js("document.readyState")
            if res in ("complete", "interactive"):
                ready = True
                break
        except Exception:
            pass
        time.sleep(0.5)

    time.sleep(1.0)
    print("[TEST] WebView2 ready. Starting automated UI click test...")

    # Inject error tracking
    init_script = """
    window.__test_errors = [];
    window.__test_logs = [];
    window.onerror = function(msg, url, line, col, err) {
        window.__test_errors.push({type: 'error', msg: msg, line: line, col: col, stack: err ? err.stack : ''});
    };
    window.addEventListener('unhandledrejection', function(event) {
        window.__test_errors.push({type: 'promise_rejection', reason: String(event.reason)});
    });
    const origLog = console.log;
    const origErr = console.error;
    console.error = function(...args) {
        window.__test_errors.push({type: 'console_error', msg: args.map(a => String(a)).join(' ')});
        origErr.apply(console, args);
    };
    """
    window.evaluate_js(init_script)

    def run_step(step_name, js_code):
        try:
            res = window.evaluate_js(js_code)
            test_summary["passed"].append({"step": step_name, "result": res})
            print(f"  [PASS] {step_name}")
            return res
        except Exception as e:
            test_summary["failed"].append({"step": step_name, "error": str(e)})
            print(f"  [FAIL] {step_name}: {e}")
            return None

    # Step 1: Check Onboarding / Dismiss if open
    run_step("1. Check and dismiss Onboarding if present", """
    (function() {
        const modal = document.getElementById('modal-onboarding');
        if (modal && !modal.classList.contains('hidden')) {
            const chk = document.getElementById('chk-accept-eula');
            if (chk) { chk.checked = true; chk.dispatchEvent(new Event('change')); }
            const btn = document.getElementById('btn-accept-onboarding');
            if (btn && !btn.disabled) { btn.click(); return 'Accepted onboarding'; }
        }
        return 'Onboarding already closed';
    })()
    """)
    time.sleep(1.0)

    # Step 2: Dashboard metrics & actions
    run_step("2. Dashboard - Verify Gauges & Values", """
    (function() {
        const cpu = document.getElementById('cpu-pct').innerText;
        const ram = document.getElementById('ram-pct').innerText;
        const disk = document.getElementById('disk-pct').innerText;
        return { cpu, ram, disk };
    })()
    """)

    run_step("2b. Dashboard - Test Metric Cards Click", """
    (function() {
        document.getElementById('card-metric-cpu')?.click();
        const tabAfterCpu = state.activeTab;
        document.querySelector('.nav-item[data-tab="dashboard"]')?.click();
        return { tabAfterCpu };
    })()
    """)
    time.sleep(0.5)

    run_step("3. Dashboard - Quick Clean RAM Button", """
    (function() {
        const btn = document.getElementById('btn-clean-ram-quick');
        if (btn) { btn.click(); return 'Clicked Clean RAM'; }
        return 'Button not found';
    })()
    """)
    time.sleep(1.0)

    run_step("3b. Dashboard - 1-Click Game Boost Execution", """
    (function() {
        const btn = document.getElementById('btn-1click-boost');
        if (btn) { btn.click(); return 'Triggered 1-Click Boost'; }
        return 'Boost btn not found';
    })()
    """)
    time.sleep(2.0)

    run_step("3c. Toast - Verify Object Notification Formatting", """
    (function() {
        showToast({ message_pl: 'Test powiadomienia Auto-Boost', message_en: 'Auto-Boost Test Notification' }, 'success', '⚡');
        const toasts = document.querySelectorAll('.toast-text');
        const lastText = toasts[toasts.length - 1]?.innerText || '';
        return { lastText, isCleanText: !lastText.includes('[object') };
    })()
    """)
    time.sleep(0.5)

    run_step("4. Dashboard - Toggle Auto-Boost Switch", """
    (function() {
        const chk = document.getElementById('chk-auto-boost');
        if (chk) {
            const prev = chk.checked;
            chk.checked = !prev;
            chk.dispatchEvent(new Event('change'));
            return 'Toggled Auto-Boost to ' + chk.checked;
        }
        return 'Switch not found';
    })()
    """)
    time.sleep(0.8)

    run_step("5. Dashboard - Refresh Processes Button", """
    (function() {
        const btn = document.getElementById('btn-refresh-procs');
        if (btn) { btn.click(); return 'Clicked Refresh Procs'; }
        return 'Btn not found';
    })()
    """)
    time.sleep(0.8)

    # Step 3: Tab switching & testing
    tabs = [
        ('cleaner', 'Czyszczenie Dysku'),
        ('storage', 'Pliki & Pamiec'),
        ('gaming', 'Gaming & FPS'),
        ('profiles', 'Profile Gier'),
        ('privacy', 'Debloat & Prywatnosc'),
        ('startup', 'Autostart'),
        ('bloatware', 'Aplikacje Systemowe'),
        ('settings', 'Ustawienia & Prawo')
    ]

    for tab_id, tab_label in tabs:
        run_step(f"Switch to Tab: {tab_label}", f"""
        (function() {{
            const nav = document.querySelector('.nav-item[data-tab="{tab_id}"]');
            if (nav) {{ nav.click(); return 'Switched to {tab_id}'; }}
            return 'Tab {tab_id} not found';
        }})()
        """)
        time.sleep(1.2)

        # Tab-specific tests
        if tab_id == 'cleaner':
            run_step("Cleaner - Check categories rendered", """
            (function() {
                const cards = document.querySelectorAll('.clean-card');
                const total = document.getElementById('cleaner-total-selected').innerText;
                return { card_count: cards.length, total_selected: total };
            })()
            """)
            run_step("Cleaner - Click Rescan", """
            (function() {
                document.getElementById('btn-scan-cleaner')?.click();
                return 'Clicked Rescan';
            })()
            """)
            time.sleep(1.0)

        elif tab_id == 'storage':
            run_step("Storage - Test File Hunter Scan", """
            (function() {
                const selLoc = document.getElementById('sel-storage-location');
                if (selLoc) selLoc.value = 'USER';
                const selSize = document.getElementById('sel-storage-min-size');
                if (selSize) selSize.value = '100';
                const btn = document.getElementById('btn-start-storage-scan');
                if (btn) { btn.click(); return 'Clicked Start Storage Scan on USER'; }
                return 'Btn not found';
            })()
            """)
            time.sleep(2.0)
            run_step("Storage - Check File Hunter Results", """
            (function() {
                const count = document.getElementById('storage-file-count').innerText;
                const total = document.getElementById('storage-total-size').innerText;
                const rows = document.querySelectorAll('#storage-table-body tr');
                return { count, total, rendered_rows: rows.length };
            })()
            """)
            run_step("Storage - Switch to App Uninstaller Subview", """
            (function() {
                document.getElementById('pill-app-uninstaller')?.click();
                return 'Switched to App Uninstaller';
            })()
            """)
            time.sleep(1.5)
            run_step("Storage - Check App Uninstaller List", """
            (function() {
                const rows = document.querySelectorAll('#apps-table-body tr');
                return { rendered_apps_count: rows.length };
            })()
            """)
            run_step("Storage - Filter Apps by search input", """
            (function() {
                const input = document.getElementById('input-app-search');
                if (input) {
                    input.value = 'windows';
                    input.dispatchEvent(new Event('input'));
                    const filtered = document.querySelectorAll('#apps-table-body tr');
                    return { filtered_count: filtered.length };
                }
                return 'Input not found';
            })()
            """)

        elif tab_id == 'gaming':
            run_step("Gaming - Check tweaks count", """
            (function() {
                const cards = document.querySelectorAll('#gaming-tweaks-grid .tweak-card');
                return { tweaks_count: cards.length };
            })()
            """)
            run_step("Gaming - Flush DNS Cache Button", """
            (function() {
                document.getElementById('btn-flush-dns')?.click();
                return 'Clicked Flush DNS';
            })()
            """)
            time.sleep(0.8)

        elif tab_id == 'profiles':
            run_step("Profiles - Check game profile cards", """
            (function() {
                const cards = document.querySelectorAll('#game-profiles-grid .profile-card');
                return { profiles_count: cards.length };
            })()
            """)
            run_step("Profiles - Click Apply Profile on First Game", """
            (function() {
                const btn = document.querySelector('.btn-apply-profile');
                if (btn) { btn.click(); return 'Clicked Apply Profile'; }
                return 'No profile button found';
            })()
            """)
            time.sleep(0.5)

        elif tab_id == 'privacy':
            run_step("Privacy - Check privacy tweaks count", """
            (function() {
                const cards = document.querySelectorAll('#privacy-tweaks-grid .tweak-card');
                return { privacy_tweaks_count: cards.length };
            })()
            """)

        elif tab_id == 'startup':
            run_step("Startup - Check startup items", """
            (function() {
                const rows = document.querySelectorAll('#startup-table-body tr');
                return { startup_items_count: rows.length };
            })()
            """)

        elif tab_id == 'bloatware':
            run_step("Bloatware - Check bloatware list", """
            (function() {
                const items = document.querySelectorAll('#bloatware-grid .bloat-item');
                return { bloatware_items_count: items.length };
            })()
            """)

        elif tab_id == 'settings':
            run_step("Settings - Check Hardware Specs Display", """
            (function() {
                const os = document.getElementById('spec-os').innerText;
                const cpu = document.getElementById('spec-cpu').innerText;
                const gpu = document.getElementById('spec-gpu').innerText;
                const ram = document.getElementById('spec-ram').innerText;
                return { os, cpu, gpu, ram };
            })()
            """)
            run_step("Settings - Test Language Switcher to EN", """
            (function() {
                document.getElementById('btn-lang-en')?.click();
                return { new_title: document.querySelector('.main-subtitle')?.innerText };
            })()
            """)
            time.sleep(0.8)
            run_step("Settings - Test Language Switcher back to PL", """
            (function() {
                document.getElementById('btn-lang-pl')?.click();
                return { restored_title: document.querySelector('.main-subtitle')?.innerText };
            })()
            """)
            time.sleep(0.8)
            run_step("Settings - Check Sub-pills (EULA, Privacy, Licenses, FAQ)", """
            (function() {
                const pPriv = document.getElementById('pill-set-privacy');
                if (pPriv) pPriv.click();
                const privLen = document.getElementById('text-privacy-policy')?.innerText.length || 0;

                const pEula = document.getElementById('pill-set-eula');
                if (pEula) pEula.click();
                const eulaLen = document.getElementById('text-eula')?.innerText.length || 0;

                const pLic = document.getElementById('pill-set-licenses');
                if (pLic) pLic.click();
                const licLen = document.getElementById('text-licenses')?.innerText.length || 0;

                const pFaq = document.getElementById('pill-set-faq');
                if (pFaq) pFaq.click();
                const faqLen = document.getElementById('text-faq')?.innerText.length || 0;

                return { privLen, eulaLen, licLen, faqLen };
            })()
            """)
            time.sleep(0.8)
            run_step("Settings - Click Check for Updates Button", """
            (function() {
                const btn = document.getElementById('btn-check-updates');
                if (btn) { btn.click(); return 'Clicked Check Updates'; }
                return 'Btn not found';
            })()
            """)
            time.sleep(1.5)

    # Collect captured JS errors
    collected_errors = window.evaluate_js("window.__test_errors || []")
    test_summary["js_errors"] = collected_errors
    print(f"\n[TEST COMPLETE] Collected {len(collected_errors)} JS errors during run.")

    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(test_summary, f, indent=2, ensure_ascii=False)

    print("[TEST] Results saved to test_results.json. Closing window.")
    time.sleep(1.0)
    window.destroy()

def main():
    auto_boost_daemon.start()
    bridge = ApiBridge()
    html_path = os.path.join(PROJECT_ROOT, "web", "index.html")

    window = webview.create_window(
        title="WinOptimizer 2.0 Pro - E2E Automated Test",
        url=html_path,
        js_api=bridge,
        width=1280,
        height=820,
        frameless=False,
        background_color='#070a13'
    )
    bridge.set_window(window)

    t = threading.Thread(target=automated_tester, args=(window,), daemon=True)
    t.start()

    webview.start(debug=False)

if __name__ == "__main__":
    main()
