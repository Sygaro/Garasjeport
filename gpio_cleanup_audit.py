import os

LGPIO_MARKERS = [
    "import lgpio",
    "lgpio.gpiochip_open",
    "lgpio.gpio_claim_input",
    "lgpio.gpio_read",
    "lgpio.gpio_write",
    "lgpio.gpiochip_close",
]

PIGPIO_MARKERS = [
    "import pigpio",
    "pigpio.pi()"
]

PROJECT_ROOT = "."  # Kjør fra rotmappen til prosjektet


def scan_file(filepath):
    findings = {"lgpio": [], "pigpio": []}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for i, line in enumerate(lines, start=1):
            for marker in LGPIO_MARKERS:
                if marker in line:
                    findings["lgpio"].append((i, line.strip()))
            for marker in PIGPIO_MARKERS:
                if marker in line:
                    findings["pigpio"].append((i, line.strip()))
    except Exception as e:
        pass  # Hopper over binære filer eller problemer
    return findings


def main():
    print("🔍 GPIO Cleanup Audit\n")
    for root, _, files in os.walk(PROJECT_ROOT):
        for file in files:
            if not file.endswith(".py"):
                continue
            path = os.path.join(root, file)
            findings = scan_file(path)

            if findings["lgpio"] or findings["pigpio"]:
                print(f"📄 {path}")
                if findings["lgpio"]:
                    print("  ⚠️  lgpio-forekomster:")
                    for lineno, line in findings["lgpio"]:
                        print(f"    {lineno}: {line}")
                if findings["pigpio"]:
                    print("  ✅ pigpio-forekomster:")
                    for lineno, line in findings["pigpio"]:
                        print(f"    {lineno}: {line}")
                print("-" * 60)


if __name__ == "__main__":
    main()
