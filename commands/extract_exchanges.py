"""Extract verbatim exchanges from AI conversation files.

Supports Claude Code (JSONL) and Gemini CLI (JSON).
Suppresses structured content (code, JSON, XML, diffs) to reduce transcript size.
"""
import json
import re
from pathlib import Path


def suppress_structured_content(text: str) -> str:
    """Replace structured content with [TYPE: n unit] markers. No AI summarization."""

    def replace_code_block(match):
        lang = match.group(1) or ''
        code = match.group(2)
        lines = len(code.strip().split('\n')) if code.strip() else 0
        return f"[CODE:{' ' + lang if lang else ''} {lines} lines]"

    text = re.sub(r'```(\w*)\n(.*?)```', replace_code_block, text, flags=re.DOTALL)

    def replace_json(match):
        return f"[JSON: {len(match.group(0).strip().split(chr(10)))} lines]"

    text = re.sub(
        r'^\s*[\{\[]\s*\n(?:.*?"[^"]+"\s*:.*?\n)+\s*[\}\]]',
        replace_json, text, flags=re.MULTILINE,
    )

    def replace_simple_json(match):
        lines = len(match.group(0).strip().split('\n'))
        return f"[JSON: {lines} lines]" if lines >= 3 else match.group(0)

    text = re.sub(r'\{[^{}]*"[^"]+"\s*:[^{}]+\}', replace_simple_json, text, flags=re.DOTALL)

    def replace_xml(match):
        lines = len(match.group(0).strip().split('\n'))
        return f"[XML: {lines} lines]" if lines >= 3 else match.group(0)

    text = re.sub(r'<(\w+)[^>]*>.*?</\1>', replace_xml, text, flags=re.DOTALL)

    def replace_stacktrace(match):
        return f"[STACKTRACE: {len(match.group(0).strip().split(chr(10)))} lines]"

    text = re.sub(
        r'Traceback \(most recent call last\):.*?(?=\n\n|\n[A-Z]|\Z)',
        replace_stacktrace, text, flags=re.DOTALL,
    )
    text = re.sub(
        r'(?:Error|Exception).*?(?:at |in |File ").*?(?:\n\s+.*?){2,}',
        replace_stacktrace, text, flags=re.DOTALL,
    )

    def replace_diff(match):
        return f"[DIFF: {len(match.group(0).strip().split(chr(10)))} lines]"

    text = re.sub(r'@@[^@]+@@.*?(?=\n@@|\n\n|\n[^-+\s]|\Z)', replace_diff, text, flags=re.DOTALL)
    text = re.sub(r'(?:^[-+].*\n){5,}', replace_diff, text, flags=re.MULTILINE)

    def replace_long_list(match):
        items = len(re.findall(r'^\s*(?:[-*]|\d+\.)\s+', match.group(0), re.MULTILINE))
        return f"[LIST: {items} items]"

    text = re.sub(r'(?:^\s*[-*]\s+.+\n){11,}', replace_long_list, text, flags=re.MULTILINE)
    text = re.sub(r'(?:^\s*\d+\.\s+.+\n){11,}', replace_long_list, text, flags=re.MULTILINE)

    text = re.sub(
        r'(?<![a-zA-Z0-9/+])[A-Za-z0-9+/=]{100,}(?![a-zA-Z0-9/+=])',
        lambda m: f"[BINARY: {len(m.group(0))} chars]", text,
    )

    text = re.sub(r'\n{3,}', '\n\n', text)
    return text


def detect_format(file_path: Path) -> str:
    with open(file_path) as f:
        content = f.read()
    try:
        data = json.loads(content)
        if isinstance(data, dict) and 'sessionId' in data:
            return 'gemini'
    except json.JSONDecodeError:
        pass
    if content.strip().startswith('{'):
        return 'claude'
    raise ValueError("Unknown or malformed session file format")


def _get_user_text_claude(msg: dict) -> str | None:
    content = msg.get("message", {})
    if "content" in content:
        c = content["content"]
        if isinstance(c, str):
            if "<command-message>" in c:
                match = re.search(r"<command-message>(.+?)</command-message>", c)
                return f"/{match.group(1)}" if match else None
            return c
        if isinstance(c, list):
            for item in c:
                if isinstance(item, dict):
                    if item.get("type") == "tool_result":
                        return None
                    if item.get("type") == "text":
                        text = item.get("text", "")
                        return None if text.strip().startswith("# /") else text
    if content.get("type") == "tool_result":
        return None
    if content.get("type") == "text":
        return content.get("text")
    return None


def _extract_exchanges_claude(file_path: Path) -> list[dict]:
    messages = []
    with open(file_path) as f:
        for line in f:
            msg = json.loads(line)
            if msg.get("type") in ("user", "assistant"):
                messages.append(msg)

    exchanges = []
    current = {"thinking": [], "said": [], "user": None}

    for msg in messages:
        if msg["type"] == "user":
            user_text = _get_user_text_claude(msg)
            if user_text:
                if current["thinking"] or current["said"]:
                    exchanges.append(current)
                    current = {"thinking": [], "said": [], "user": None}
                current["user"] = user_text
        elif msg["type"] == "assistant":
            content = msg.get("message", {}).get("content", [])
            if isinstance(content, list):
                for block in content:
                    if block.get("type") == "thinking":
                        current["thinking"].append(block.get("thinking", ""))
                    elif block.get("type") == "text":
                        current["said"].append(block.get("text", ""))

    if current["thinking"] or current["said"] or current["user"]:
        exchanges.append(current)
    return exchanges


def _extract_exchanges_gemini(file_path: Path) -> list[dict]:
    with open(file_path) as f:
        data = json.load(f)

    exchanges = []
    current = {"thinking": [], "said": [], "user": None}

    for msg in data.get("messages", []):
        role, text = msg.get("type"), msg.get("content")
        if role == "user" and text:
            if current["said"]:
                exchanges.append(current)
                current = {"thinking": [], "said": [], "user": None}
            current["user"] = text
        elif role == "gemini" and text:
            current["said"].append(text)

    if current["said"] or current["user"]:
        exchanges.append(current)
    return exchanges


def extract_exchanges(file_path: Path) -> list[dict]:
    fmt = detect_format(file_path)
    if fmt == 'claude':
        return _extract_exchanges_claude(file_path)
    elif fmt == 'gemini':
        return _extract_exchanges_gemini(file_path)
    raise ValueError(f"Unknown format: {fmt}")


def format_exchanges(exchanges: list[dict], max_exchanges: int = None, suppress: bool = True) -> str:
    output = ["## Exchanges\n"]
    for i, ex in enumerate(exchanges[:max_exchanges], 1):
        output.append(f"### {i}\n")
        if ex["user"]:
            user_text = suppress_structured_content(ex['user']) if suppress else ex['user']
            output.append(f"**User:**\n{user_text}\n")
        if ex["thinking"]:
            thinking = "\n\n".join(ex["thinking"])
            if suppress:
                thinking = suppress_structured_content(thinking)
            output.append(f"**Thinking:**\n{thinking}\n")
        if ex["said"]:
            said = "\n\n".join(ex["said"])
            if suppress:
                said = suppress_structured_content(said)
            output.append(f"**Said:**\n{said}\n")
        output.append("---\n")
    return "\n".join(output)
