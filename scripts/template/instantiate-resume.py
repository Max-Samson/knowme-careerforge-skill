#!/usr/bin/env python3
"""Bind supplied facts to independent blank canvases; publish only complete output.

canvas.html owns layout, not candidate content. Each <!-- resume:NAME --> slot
must occur exactly once. sample-profile.json is gallery-only input, never an automatic fallback.
The shared profile contract validates and normalizes every input document.
Omitting --profile deliberately produces a blank canvas.
"""

import argparse
from collections import Counter
from html import escape
from html.parser import HTMLParser
import json
import importlib.util
import os
from pathlib import Path
import re
import sys
import tempfile

SLOTS = {"styles", "document-title", "basics", "summary", "skills",
         "experience", "projects", "education", "certifications", "language"}
SLOT = re.compile(r"<!-- resume:([a-z-]+) -->|{{ resume:(language) }}")
LABELS = {
    "zh": {"document-title": "个人简历", "summary": "个人简介", "skills": "专业技能",
           "experience": "工作经历", "projects": "项目经历", "education": "教育背景", "certifications": "证书"},
    "en": {"document-title": "Resume", "summary": "Summary", "skills": "Skills",
           "experience": "Experience", "projects": "Projects", "education": "Education", "certifications": "Certifications"},
}



FONT_PRESETS = {
    "system": "",
    "arial-unicode": """/* Explicit local font: a missing face must fail font QA, not silently pass. */
@font-face { font-family: "KnowMe Unicode"; src: local("Arial Unicode MS"); font-weight: 400; font-style: normal; }
:root { --primitive-font-sans: "KnowMe Unicode", Arial, sans-serif; --resume-font-body: "KnowMe Unicode", Arial, sans-serif; }
""",
}


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


class CanvasContract(HTMLParser):
    """Reject absent, duplicate, unknown or non-content-context binding slots."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.slots = []

    def handle_starttag(self, tag, attrs):
        if tag == "html" and not self.stack and attrs.count(("lang", "{{ resume:language }}")) == 1:
            self.slots.append("language")
        if tag not in {"meta", "link", "br", "hr", "img", "input", "wbr"}:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack.pop() != tag:
            raise ValueError(f"Malformed canvas closing tag: {tag}")

    def handle_comment(self, data):
        if not data.strip().startswith("resume:"):
            return
        name = data.strip()[7:]
        parent = self.stack[-1] if self.stack else None
        valid = (parent == "head" if name == "styles" else
                 parent == "title" if name == "document-title" else
                 "body" in self.stack and parent in {"main", "aside", "div", "header", "section", "td", "body"})
        if not valid:
            raise ValueError(f"Invalid canvas slot context: {name}")
        self.slots.append(name)


def validate_canvas(canvas):
    parser = CanvasContract()
    parser.feed(canvas)
    parser.close()
    expected = Counter(SLOTS)
    if parser.stack or Counter(parser.slots) != expected or Counter(m.group(1) or m.group(2) for m in SLOT.finditer(canvas)) != expected:
        raise ValueError("Canvas must contain every named resume slot exactly once")


def profile_contract():
    path = get_project_root() / "scripts" / "contracts" / "profile.py"
    spec = importlib.util.spec_from_file_location("careerforge_profile_contract", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def text_field(obj, key):
    value = obj.get(key)
    return "" if value is None else str(value)


def records(obj, key):
    return obj.get(key) or []


def strings(obj, key):
    return obj.get(key) or []


def highlight_keywords(text, keywords):
    """Match plain text once, then escape each slice; never search generated HTML."""
    words = sorted({kw.strip() for kw in keywords if kw.strip()}, key=lambda kw: (-len(kw), kw))
    if not words:
        return escape(text, quote=True)
    alternatives = [
        (r"(?<!\w)" if re.match(r"\w", word[0]) else "") + re.escape(word)
        + (r"(?!\w)" if re.match(r"\w", word[-1]) else "")
        for word in words
    ]
    pattern = re.compile("|".join(alternatives), re.I)
    parts, offset = [], 0
    for match in pattern.finditer(text):
        parts.extend((escape(text[offset:match.start()]), "<strong>", escape(match.group()), "</strong>"))
        offset = match.end()
    parts.append(escape(text[offset:]))
    return "".join(parts)


def render_profile_into_html(html_str, profile, keywords=None, *, css=""):
    validate_canvas(html_str)
    profile = profile_contract().normalize_profile(profile)
    language = profile.get("language") or "zh-CN"
    if not re.fullmatch(r"(?:en|zh)(?:-[A-Za-z0-9]{1,8})*", language, re.I):
        raise ValueError("Unsupported canvas language; use an en or zh language tag")
    labels = LABELS[language.split("-")[0].lower()]
    basics = profile.get("basics") or {}
    keywords = keywords or []

    def element(tag, cls, value):
        return f'<{tag} class="{cls}">{highlight_keywords(value, keywords)}</{tag}>' if value else ""

    def field(obj, key, cls="fact-text", tag="p"):
        return element(tag, cls, text_field(obj, key))

    def section(key, content):
        label = labels[key]
        if not content:
            return ""
        return f'<section class="resume-section" id="{key}"><h2 class="section-title">{label}</h2>{content}</section>'

    def bullets(obj):
        content = "".join(field(b, "text", "fact-bullet", "li") for b in records(obj, "bullets"))
        return f'<ul class="bullet-list">{content}</ul>' if content else ""

    def dates(obj):
        return element("span", "date-range", " – ".join(filter(None, (text_field(obj, "startDate"), text_field(obj, "endDate")))))

    def entries(key, name_key):
        rendered = []
        for item in records(profile, key):
            heading = field(item, name_key, "org-name", "span")
            heading += "".join(field(item, k, "role-badge", "span") for k in ("role", "degree", "field"))
            heading += dates(item)
            content = f'<div class="item-header">{heading}</div>' if heading else ""
            content += field(item, "location") + field(item, "summary")
            gpa = item.get("gpa")
            if gpa is not None and gpa != "":
                content += element("p", "edu-detail", f"GPA: {gpa}")
            content += field(item, "repoUrl") + field(item, "demoUrl")
            content += "".join(element("span", "tech-tag", t) for t in strings(item, "techStack"))
            content += "".join(element("p", "edu-detail", honor) for honor in strings(item, "honors"))
            content += bullets(item)
            if content:
                rendered.append(f'<div class="{key[:-1] if key == "projects" else key}-item">{content}</div>')
        return "".join(rendered)

    name = text_field(basics, "name")
    basic_html = element("h1", "candidate-name", name) + field(basics, "title", "job-target")
    contacts = "".join(field(basics, k, "contact-item", "span") for k in ("phone", "email", "location", "github", "website"))
    if contacts:
        basic_html += f'<div class="contact-grid">{contacts}</div>'
    skill_rows = []
    for skill in records(profile, "skills"):
        category = field(skill, "category", "skill-category", "span")
        items = strings(skill, "items")
        # highlighted is metadata selecting emphasis, never an additional source of facts.
        content = category + element("span", "skill-items", ("; " if language.lower().startswith("en") else "、").join(items))
        if content:
            skill_rows.append(f'<div class="skill-row">{content}</div>')
    values = {
        "styles": f"<style>\n{css}\n</style>",
        "language": escape(language, quote=True),
        "document-title": escape(name + " - " + labels["document-title"] if name else labels["document-title"]),
        "basics": f'<header class="resume-header">{basic_html}</header>' if basic_html else "",
        "summary": section("summary", field(basics, "summary", "value-prop")),
        "skills": section("skills", "".join(skill_rows)),
        "experience": section("experience", entries("experience", "company")),
        "projects": section("projects", entries("projects", "name")),
        "education": section("education", entries("education", "institution")),
        "certifications": section("certifications", "".join(element("p", "fact-text", item) for item in strings(profile, "certifications"))),
    }
    # One substitution pass: user text resembling a slot is never interpreted.
    return SLOT.sub(lambda match: values[match.group(1) or match.group(2)], html_str)


def resolve_template(root, template_id):
    templates = root / "src" / "templates"
    for folder in sorted(templates.iterdir()):
        if not folder.is_dir() or folder.name == "common":
            continue
        if folder.name == template_id:
            return folder
        metadata = folder / "metadata.json"
        if metadata.exists() and json.loads(metadata.read_text(encoding="utf-8")).get("id") == template_id:
            return folder
    raise ValueError(f"Template '{template_id}' not found")


def instantiate_workspace(template_id, profile_path=None, keywords=None, output_path="workspace/resume.html", quiet=False, font_preset="system"):
    if font_preset not in FONT_PRESETS:
        raise ValueError("Unknown font preset: " + str(font_preset))
    root = get_project_root()
    folder = resolve_template(root, template_id)
    canvas = (folder / "canvas.html").read_text(encoding="utf-8")
    common = root / "src" / "templates" / "common"
    css = "\n".join(path.read_text(encoding="utf-8") for path in
                    (common / "base.css", folder / "style.css", common / "canvas-bindings.css"))
    css += "\n" + FONT_PRESETS[font_preset]
    profile = json.loads(Path(profile_path).read_text(encoding="utf-8")) if profile_path is not None else {}
    profile = profile_contract().load_document(profile)["profile"]
    rendered = render_profile_into_html(canvas, profile, keywords.split(",") if keywords else [], css=css)
    output = Path(output_path)
    if profile_path is not None and output.resolve() == Path(profile_path).resolve():
        raise ValueError("Output must not overwrite the input profile")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=output.parent,
                                         prefix=f".{output.name}.", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(rendered)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    if not quiet:
        print(f"Canvas written: {output.resolve()}")
    return output


class CLIParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)


def main():
    parser = CLIParser(description=__doc__)
    parser.add_argument("--template", "-t", required=True, help="Template directory name or metadata ID")
    parser.add_argument("--profile", "-p", help="Candidate JSON; omitted produces a blank canvas")
    parser.add_argument("--keywords", "-k", help="Comma-separated plain-text keywords")
    parser.add_argument("--output", "-o", default="workspace/resume.html")
    parser.add_argument("--font-preset", choices=sorted(FONT_PRESETS), default="system")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress human diagnostics; JSON result is always emitted")
    result = {"status": "FAIL", "errors": [], "warnings": [], "checks": {"canvasWritten": False}}
    try:
        args = parser.parse_args()
        output = instantiate_workspace(args.template, args.profile, args.keywords, args.output, quiet=True, font_preset=args.font_preset)
        result.update(status="PASS", output=str(output.resolve()))
        result["checks"]["canvasWritten"] = True
    except (OSError, ValueError, TypeError) as error:
        result["errors"].append(str(error))
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
