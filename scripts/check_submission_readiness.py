#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


def contains_any(text: str, needles: list[str]) -> bool:
    return any(needle in text for needle in needles)


def main() -> int:
    issues: list[str] = []

    submission = (ROOT / "SUBMISSION.md").read_text(encoding="utf-8")
    landing = (ROOT / "landing" / "index.html").read_text(encoding="utf-8")

    if contains_any(
        submission,
        [
            "Owner to paste the final YouTube unlisted URL after recording.",
            "Owner to attach a screenshot of the app",
            "Owner to replace with final name, role, and contact details.",
        ],
    ):
        issues.append("SUBMISSION.md still contains owner-supplied placeholders for demo, cover image, or team details.")

    if "Demo workflow" in landing:
        issues.append("landing/index.html is still using the fallback demo block instead of a real embedded demo.")

    if "https://github.com/Ridwannurudeen/fixfirst-edge" not in landing:
        issues.append("landing/index.html is not pointing at the canonical GitHub repository.")

    if "cover.svg" not in landing:
        issues.append("landing/index.html is missing the cover/share asset metadata.")

    cover = ROOT / "landing" / "cover.svg"
    if not cover.exists():
        issues.append("landing/cover.svg is missing.")

    if issues:
        print("Submission readiness: NOT READY")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Submission readiness: READY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
