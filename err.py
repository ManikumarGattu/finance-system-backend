with open("pip_error2.txt", "r", encoding="utf-16le", errors="ignore") as f:
    for line in f:
        if "Failed to build" in line or "error" in line.lower() or "Collecting" in line:
            print(line.strip()[:100])
