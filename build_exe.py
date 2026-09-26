import os
import sys
import subprocess
import shutil

def build():
    print("============================================================")
    print("      WINOPTIMIZER 2.0 PRO - KOMPLETNY SYSTEM BUDOWANIA     ")
    print("============================================================")

    project_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(project_dir, "dist")
    dist_installer_dir = os.path.join(project_dir, "dist_installer")
    icon_path = os.path.join(project_dir, "assets", "icon.ico")
    desktop_dir = os.path.join(os.environ.get("USERPROFILE", "C:\\Users\\Jedynka"), "Desktop")

    # Krok 1: Kompilacja PyInstaller
    print("\n[1/3] Kompilacja samodzielnego pliku WinOptimizer.exe (PyInstaller)...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=WinOptimizer",
        "--noconsole",
        "--onefile",
        "--uac-admin",
        f"--icon={icon_path}",
        "--collect-all=webview",
        f"--add-data={project_dir}/web;web",
        f"--add-data={project_dir}/assets;assets",
        os.path.join(project_dir, "main.py")
    ]

    res = subprocess.run(cmd, cwd=project_dir)
    if res.returncode != 0:
        print("\n[-] Błąd podczas kompilacji PyInstaller.")
        return False

    exe_path = os.path.join(dist_dir, "WinOptimizer.exe")
    print(f"[+] Utworzono: {exe_path}")

    # Krok 2: Generowanie grafik instalatora
    print("\n[2/3] Sprawdzanie i generowanie grafik instalatora...")
    try:
        from create_installer_artwork import make_large_banner, make_small_banner
        make_large_banner()
        make_small_banner()
    except Exception as e:
        print(f"[*] Uwaga przy generowaniu grafik: {e}")

    # Krok 3: Kompilacja Instalatora Inno Setup
    print("\n[3/3] Kompilacja nowoczesnego instalatora Windows (Inno Setup 6)...")
    iscc_candidates = [
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Inno Setup 6", "ISCC.exe"),
        "C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe",
        "C:\\Program Files\\Inno Setup 6\\ISCC.exe"
    ]
    iscc_path = None
    for cand in iscc_candidates:
        if os.path.exists(cand):
            iscc_path = cand
            break

    installer_created = False
    if iscc_path:
        iss_file = os.path.join(project_dir, "installer_setup.iss")
        res_iscc = subprocess.run([iscc_path, iss_file], cwd=project_dir)
        if res_iscc.returncode == 0:
            installer_path = os.path.join(dist_installer_dir, "WinOptimizer_Setup_v2.0_Pro.exe")
            print(f"[+] Utworzono instalator: {installer_path}")
            installer_created = True
        else:
            print("[-] Błąd kompilacji Inno Setup.")
    else:
        print("[!] ISCC.exe nie znaleziony. Pomijam tworzenie instalatora.")

    # Kopiowanie na Pulpit
    print("\n[*] Kopiowanie plików wynikowych na Pulpit...")
    try:
        # Portable exe
        if os.path.exists(exe_path):
            shutil.copy2(exe_path, os.path.join(project_dir, "WinOptimizer.exe"))
            if os.path.exists(desktop_dir):
                shutil.copy2(exe_path, os.path.join(desktop_dir, "WinOptimizer.exe"))
                print(f"  -> Pulpit: {os.path.join(desktop_dir, 'WinOptimizer.exe')}")

        # Setup exe
        if installer_created:
            setup_path = os.path.join(dist_installer_dir, "WinOptimizer_Setup_v2.0_Pro.exe")
            shutil.copy2(setup_path, os.path.join(project_dir, "WinOptimizer_Setup_v2.0_Pro.exe"))
            if os.path.exists(desktop_dir):
                shutil.copy2(setup_path, os.path.join(desktop_dir, "WinOptimizer_Setup_v2.0_Pro.exe"))
                print(f"  -> Pulpit: {os.path.join(desktop_dir, 'WinOptimizer_Setup_v2.0_Pro.exe')}")
    except Exception as e:
        print(f"[*] Błąd kopiowania: {e}")

    print("\n" + "="*60)
    print("[+] WSZYSTKO GOTOWE W 100%!")
    print("="*60 + "\n")
    return True

if __name__ == "__main__":
    build()
