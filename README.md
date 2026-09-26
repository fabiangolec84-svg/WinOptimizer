# 🚀 WinOptimizer 2.0 Pro (Windows & Gaming FPS Booster)

Zaawansowane, kompleksowe narzędzie desktopowe dla graczy i entuzjastów systemu Windows 10/11 do maksymalizacji liczby klatek na sekundę (FPS), eliminacji stutteringu i opóźnień (input lag), usuwania zbędnych plików tymczasowych oraz pełnego debloatingu.

---

## ⚡ Główne Moduły i Możliwości

### 1. 🏠 Pulpit Główny & Monitor Systemu
- **Wskaźniki na żywo**: Obciążenie procesora (CPU), pamięci RAM oraz dysku systemowego `C:`.
- **⚡ 1-Click Game Boost**: Błyskawiczna optymalizacja przed startem gry (Tryb gry, plan Najwyższa Wydajność, czyszczenie RAM i plików tymczasowych).
- **💾 Zwolnij RAM**: Opróżnianie pamięci podręcznej (Standby List) procesów w tle za pomocą natywnego Windows API (`EmptyWorkingSet`).
- **🔥 Top Zasobożerne Procesy**: Podgląd procesów zżerających najwięcej pamięci RAM z możliwością ich natychmiastowego zakończenia.
- **🛡️ Centrum Bezpieczeństwa (Rollback)**: Kopia zapasowa w formacie JSON każdego zmienionego klucza rejestru z możliwością 1-kliknięciowego cofnięcia wszystkich zmian oraz tworzenie Punktów Przywracania Systemu Windows.

### 2. 🧹 Czyszczenie Śmieci & Cache 2.0
- **Lokalizacje**:
  - Pliki tymczasowe użytkownika (`%TEMP%`) i systemowe (`C:\Windows\Temp`)
  - Pamięć podręczna Windows Update (`SoftwareDistribution\Download`)
  - **Delivery Optimization Cache** (P2P cache Windowsa)
  - **DirectX & GPU Shader Cache** (NVIDIA DXCache/GLCache, AMD DxCache, D3DSCache)
  - Pamięć podręczna **Discorda** (`Cache`, `Code Cache`, `GPUCache`)
  - Pamięć podręczna **Spotify** (`Storage Cache`)
  - Pamięć podręczna przeglądarki **Steam** (`htmlcache`)
  - Zrzuty pamięci po awariach (`Crash Dumps`, `WER`)
  - Opróżnianie kosza systemowego wszystkich partycji
  - Pamięć podręczna przeglądarek (Chrome, Edge, Brave, Opera)
- **Monit o otwarte przeglądarki**: Wykrywa otwartego Chrome'a, Edge'a czy Brave'a z przyciskiem szybkiego zamknięcia, aby odblokować pliki cache.
- **Przyciski szybkiego wyboru**: *⭐ Tylko zalecane (bezpieczne)*, *✅ Zaznacz wszystko*, *❌ Odznacz wszystko*.

### 3. ⚡ Gaming & FPS Tweaks (Gaming Suite)
- **Wyłączenie Xbox Game Bar & DVR**: Blokuje nagrywanie ekranu w tle eliminując spadki FPS.
- **Windows Game Mode**: Wymuszenie priorytetu alokacji rdzeni procesora dla okna gry.
- **Raw Mouse Input (Brak akceleracji)**: Wyłączenie "Zwiększ precyzję wskaźnika" dla idealnego celowania 1:1 w grach FPS.
- **Blokada Klawiszy Trwałych (Sticky Keys)**: Blokuje irytujące okno 5x Shift minimalizujące gry.
- **Wyłączenie MPO (Multi-Plane Overlay)**: Rozwiązuje problem migotania ekranu, czarnych klatek i mikro-przycięć na kartach NVIDIA i AMD.
- **Wysoki priorytet MMCSS**: Podnosi priorytet szeregowania wątków gier nad aplikacjami tła.
- **Wyłączenie dławienia sieci (Network Throttling Index)**: Odblokowuje pełną przepustowość pakietów sieciowych dla najniższego pingu.
- **Plan zasilania "Najwyższa wydajność" (Ultimate Performance)** z możliwością powrotu do planu zrównoważonego.
- **Gaming DNS Cloudflare (1.1.1.1 + 1.0.0.1)** + czyszczenie pamięci podręcznej DNS (**Flush DNS**).
- **Klasyczne menu kontekstowe Windows 11**: Szybkie pełne menu prawego przycisku myszy bez "Pokaż więcej opcji".
- **Optymalizacja efektów wizualnych**: Wyłączenie animacji okien i cieni dla responsywności interfejsu.

### 4. 🎮 Profile Gier (Game Booster Profiles)
- Dedykowane parametry startowe i rekomendacje dla popularnych tytułów:
  - **Counter-Strike 2 (CS2)** – komendy startowe Steam, low latency tick sleep
  - **Valorant** – optymalizacja pod Riot Vanguard i RawInputBuffer
  - **Fortnite** – parametry Unreal Engine 5, Performance Mode
  - **Call of Duty: Warzone** – optymalizacja VRAM Scale i renderera
  - **FiveM / GTA V** – dedykowany czyściciel cache FiveM (rozwiązuje crashe i zwalnia gigabajty miejsca)
  - **Minecraft Java** – optymalne flagi garbage collectora G1GC

### 5. 🛡️ Prywatność & Debloat
- Zatrzymanie telemetrii diagnostycznej (`DiagTrack`, `dmwappushservice`).
- Wyłączenie wyszukiwarki Bing w menu Start (błyskawiczne wyszukiwanie aplikacji lokalnych).
- Wyłączenie Cortany.
- Blokada reklam, podpowiedzi i sponsorowanych kafelków Microsoftu.

### 6. 🚀 Menedżer Autostartu 2.0 (Startup Apps)
- **Kompletna detekcja**:
  - Rejestr 64-bit (`HKCU\Run`, `HKLM\Run`)
  - Rejestr 32-bit (`HKLM\WOW6432Node\Run`)
  - Programy wyłączone (`Run\Disabled`)
  - Folder autostartu użytkownika (`shell:startup`)
  - Folder autostartu wspólny (`shell:common startup`)
- **Dwukierunkowe przełączniki ON / OFF**: Każdy program można włączać i wyłączać w dowolnym momencie.
- **Wyszukiwarka**: Błyskawiczne filtrowanie aplikacji po nazwie.
- **Wskaźnik wpływu**: Etykiety szacowanego wpływu na czas uruchamiania (*Wysoki / Średni / Niski*).
- **Operacje masowe**: *⚡ Wyłącz wszystkie zbędne*, *🔄 Włącz wszystkie*.

### 7. 🗑️ Usuwanie Bloatware (Windows Apps)
- Bezpieczne odinstalowywanie fabrycznych aplikacji UWP (Pogoda, Wiadomości Bing, Solitaire, Centrum Opinii, Porady, Clipchamp itp.).

### 8. 📥 Działanie w Zasobniku Systemowym (System Tray)
- Przycisk *Minimalizuj do Traya* w menu bocznym.
- Działanie w tle obok zegarka z szybkim menu: otwarcie programu, zwolnienie RAM lub wyjście.

---

## 🛠️ Uruchomienie

### Samodzielny plik `.exe`:
W folderze projektu kliknij dwukrotnie:
👉 **`WinOptimizer.exe`** (możesz go skrótem przenieść na Pulpit).

### Uruchomienie ze źródła w Pythonie:
```bash
python main.py
```
*(lub kliknij `run.bat`)*

### Ponowna kompilacja po własnych zmianach:
```bash
python build_exe.py
```
*(lub kliknij `build.bat`)*
