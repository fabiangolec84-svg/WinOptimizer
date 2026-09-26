import ctypes
import os
import psutil

# Windows API Constants
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_SET_QUOTA = 0x0100

def clean_ram() -> tuple[int, int, int]:
    """
    Cleans system RAM by emptying the working set of accessible processes.
    Returns: (initial_free_mb, final_free_mb, freed_mb)
    """
    mem_before = psutil.virtual_memory()
    initial_free_mb = int(mem_before.available / (1024 * 1024))

    kernel32 = ctypes.windll.kernel32
    psapi = ctypes.windll.psapi

    current_pid = os.getpid()

    # Iterate over all running processes
    for proc in psutil.process_iter(['pid', 'name']):
        pid = proc.info['pid']
        if pid <= 4 or pid == current_pid:
            continue

        try:
            h_process = kernel32.OpenProcess(
                PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA,
                False,
                pid
            )
            if h_process:
                try:
                    psapi.EmptyWorkingSet(h_process)
                finally:
                    kernel32.CloseHandle(h_process)
        except Exception:
            continue

    mem_after = psutil.virtual_memory()
    final_free_mb = int(mem_after.available / (1024 * 1024))
    freed_mb = max(0, final_free_mb - initial_free_mb)

    return initial_free_mb, final_free_mb, freed_mb
