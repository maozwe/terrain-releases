"""Regenerate index.json from whatever is under files/.

The app reads this one file instead of walking GitHub's Contents API. That API
allows 60 requests an hour to an unauthenticated caller, counted per IP, and a
surveyor who has just opened four folders on shared mobile data is exactly the
caller who would exhaust it — with no way to tell that apart from the files
being gone. One request, CDN-cached, no limit.

Deliberately carries no timestamp and no commit sha. The output is a pure
function of the tree, so a run that changes nothing produces no diff, and the
workflow can skip the commit instead of filling the history with empty ones.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = ROOT / "files"
OUT = ROOT / "index.json"

RAW_BASE = "https://raw.githubusercontent.com/maozwe/terrain-releases/main"

# Not content. A folder README explains the folder to someone browsing GitHub;
# showing it as a file in the app just puts a README in front of the surveyor
# in every single folder.
HIDDEN_NAMES = {"README.md", ".gitkeep", ".DS_Store", "Thumbs.db"}


def _url(rel_posix: str) -> str:
    """A raw URL for a repo-relative path.

    Percent-encoding matters here: these folders are Hebrew, and an unencoded
    path works in a browser (which encodes it for you) while failing from Dart's
    http client, which does not.
    """
    from urllib.parse import quote

    return f"{RAW_BASE}/{quote(rel_posix)}"


def _node(path: Path) -> dict | None:
    rel = path.relative_to(ROOT).as_posix()

    if path.is_dir():
        children = []
        # Directories first, then files, each alphabetically — the order the
        # app shows, decided here rather than in the client so both stay the
        # same if another client is ever written.
        for child in sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
            if child.name in HIDDEN_NAMES or child.name.startswith("."):
                continue
            node = _node(child)
            if node is not None:
                children.append(node)
        return {
            "name": path.name,
            "path": rel,
            "type": "dir",
            "children": children,
            # Counted here so the app can say "3 פריטים" without walking the
            # subtree itself.
            "count": len(children),
        }

    return {
        "name": path.name,
        "path": rel,
        "type": "file",
        "size": path.stat().st_size,
        "url": _url(rel),
    }


def main() -> None:
    if not FILES.is_dir():
        raise SystemExit("files/ does not exist")

    tree = _node(FILES)
    OUT.write_text(
        json.dumps({"root": "files", "tree": tree}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    def count(node: dict) -> int:
        if node["type"] == "file":
            return 1
        return sum(count(c) for c in node["children"])

    print(f"indexed {count(tree)} files")


if __name__ == "__main__":
    main()
