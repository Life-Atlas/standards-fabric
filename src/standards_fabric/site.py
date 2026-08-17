"""Render site/index.html — a self-contained viewer (data embedded, no external requests)."""
from __future__ import annotations

import json
import os

from .twin import ROOT

SITE = os.path.join(ROOT, "site")
TEMPLATE = os.path.join(SITE, "template.html")


def render_site(payload: dict) -> str:
    with open(TEMPLATE, encoding="utf-8") as f:
        tpl = f.read()
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = tpl.replace("/*__DATA__*/null", data)
    out = os.path.join(SITE, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return out
