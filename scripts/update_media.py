from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ASSETS_ROOT = PROJECT_ROOT / "assets"
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def title_from_name(file_name: str) -> str:
    base = Path(file_name).stem
    clean = re.sub(r"^[0-9]+[-_ ]*", "", base)
    clean = re.sub(r"[-_]+", " ", clean).strip()
    if not clean:
        clean = base
    return clean.title()


def image_items(path: Path, category: str | None = None, include_desc: bool = False) -> list[dict]:
    if not path.exists():
        return []

    files = sorted(
        [p for p in path.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS],
        key=lambda p: p.name.lower(),
    )
    items: list[dict] = []
    for index, file_path in enumerate(files, start=1):
        rel = file_path.relative_to(PROJECT_ROOT).as_posix()
        item: dict = {
            "id": index,
            "title": title_from_name(file_path.name),
            "img": rel,
        }
        if category:
            item["cat"] = category
        if include_desc:
            item["desc"] = None
        items.append(item)

    if category == "Woodwork":
        items.sort(
            key=lambda item: (
                0 if re.search(r"swinging garden bench", item["title"], re.I) else 1,
                item["id"],
            )
        )
        for index, item in enumerate(items, start=1):
            item["id"] = index

    return items


def collect_recent(entries: list[dict]) -> list[dict]:
    sorted_entries = sorted(entries, key=lambda item: item["mtime"], reverse=True)
    return [
        {
            "title": item["title"],
            "img": item["img"],
            "category": item["category"],
        }
        for item in sorted_entries
    ]


def pick_featured(entries: list[dict]) -> dict | None:
    if not entries:
        return None
    index = date.today().toordinal() % len(entries)
    item = entries[index]
    return {
        "title": item["title"],
        "img": item["img"],
        "category": item["category"],
    }


def recent_entries_from(path: Path, label: str) -> list[dict]:
    if not path.exists():
        return []

    entries: list[dict] = []
    for file_path in path.iterdir():
        if not file_path.is_file() or file_path.suffix.lower() not in IMAGE_EXTS:
            continue
        rel = file_path.relative_to(PROJECT_ROOT).as_posix()
        entries.append(
            {
                "title": title_from_name(file_path.name),
                "img": rel,
                "category": label,
                "mtime": file_path.stat().st_mtime,
            }
        )
    return entries


for folder in [
    ASSETS_ROOT,
    ASSETS_ROOT / "woodwork",
    ASSETS_ROOT / "photography",
    ASSETS_ROOT / "photography" / "bw",
    ASSETS_ROOT / "photography" / "colour",
    ASSETS_ROOT / "restorations",
]:
    ensure_dir(folder)

woodwork = image_items(ASSETS_ROOT / "woodwork", "Woodwork", include_desc=True)
photography_bw = image_items(ASSETS_ROOT / "photography" / "bw")
photography_color = image_items(ASSETS_ROOT / "photography" / "colour")
restorations = image_items(ASSETS_ROOT / "restorations")

recent_entries: list[dict] = []
recent_entries += recent_entries_from(ASSETS_ROOT / "woodwork", "Woodwork")
recent_entries += recent_entries_from(ASSETS_ROOT / "restorations", "Restoration")
recent_entries += recent_entries_from(ASSETS_ROOT / "photography" / "bw", "Photography BW")
recent_entries += recent_entries_from(ASSETS_ROOT / "photography" / "colour", "Photography Color")

recent = collect_recent(recent_entries)
featured = pick_featured(recent_entries)

stats = {
    "woodwork": len(woodwork),
    "restorations": len(restorations),
    "photos": len(photography_bw) + len(photography_color),
}
stats["total"] = stats["woodwork"] + stats["restorations"] + stats["photos"]

media = {
    "woodwork": woodwork,
    "photography": {
        "bw": photography_bw,
        "color": photography_color,
    },
    "restorations": restorations,
    "recent": recent,
    "stats": stats,
    "featured": featured,
}

media_path = ASSETS_ROOT / "media.json"
with media_path.open("w", encoding="utf-8") as handle:
    json.dump(media, handle, indent=2, ensure_ascii=True)
    handle.write("\n")

print(f"Wrote {media_path}")
