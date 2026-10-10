"""Falla si algún archivo de public/ o dist/ supera 25 MiB.

Cloudflare Pages no acepta archivos de más de 25 MiB: el deploy fallaría.
Uso:
    python check_size.py
"""

import sys
from pathlib import Path

LIMIT_BYTES = 25 * 1024 * 1024  # 25 MiB
ROOT = Path(__file__).parent
FOLDERS = [ROOT / "public", ROOT / "dist"]


def main() -> None:
    too_big = []
    for folder in FOLDERS:
        if not folder.exists():
            continue
        for file in folder.rglob("*"):
            if file.is_file() and file.stat().st_size > LIMIT_BYTES:
                too_big.append(file)

    if too_big:
        for file in too_big:
            size_mib = file.stat().st_size / 1024 / 1024
            print(f"ERROR: {file.relative_to(ROOT)} ocupa {size_mib:.1f} MiB (máximo 25 MiB)", file=sys.stderr)
        sys.exit(1)

    print("OK: ningún archivo supera 25 MiB.")


if __name__ == "__main__":
    main()
