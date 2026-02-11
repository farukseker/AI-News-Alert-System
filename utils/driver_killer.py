import psutil


CHROME_KEYWORDS = ["chrome", "chromium", "chromedriver"]


def find_chrome_processes():
    chrome_procs = []
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            name = proc.info["name"] or ""
            cmdline = " ".join(proc.info["cmdline"] or [])
            if any(kw in name.lower() or kw in cmdline.lower() for kw in CHROME_KEYWORDS):
                chrome_procs.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return chrome_procs


def kill_chrome_processes():
    procs = find_chrome_processes()

    if not procs:
        print("[INFO] No Chrome/Chromium processes found.")
        return

    print(f"[INFO] Found {len(procs)} Chrome-related process(es):")
    for p in procs:
        try:
            print(f"  PID {p.pid} | {p.name()} | {' '.join(p.cmdline()[:3])}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    for p in procs:
        try:
            p.kill()
            print(f"[KILLED] PID {p.pid}")
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"[ERROR] Could not kill PID {p.pid}: {e}")

    print("[DONE] All Chrome processes terminated.")


__all__ = "kill_chrome_processes",