import contextlib
import io
from itertools import repeat
import logging
import time
from pathlib import Path
from typing import Any, Dict, TypeVar

import click
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown as RichMarkdown
from rich.text import Text
from types import ModuleType

logger = logging.getLogger(__name__)


class MarkdownStream:
    live = None
    when = 0
    min_delay = 0.050
    live_window = 6

    def __init__(self, mdargs=None):
        self.printed = []

        if mdargs:
            self.mdargs = mdargs
        else:
            self.mdargs = {}

        self.live = Live(Text(""), refresh_per_second=1.0 / self.min_delay)
        self.live.start()

    def __del__(self):
        if self.live:
            with contextlib.suppress(Exception):
                self.live.stop()

    def update(self, text, final=False) -> None:
        now = time.time()
        if not final and now - self.when < self.min_delay:
            return
        self.when = now

        string_io = io.StringIO()
        console = Console(file=string_io, force_terminal=True)

        markdown = RichMarkdown(text, **self.mdargs)

        console.print(markdown)
        output = string_io.getvalue()

        lines = output.splitlines(keepends=True)
        num_lines = len(lines)

        if not final:
            num_lines -= self.live_window

        if final or num_lines > 0:
            num_printed = len(self.printed)

            show = num_lines - num_printed

            if show <= 0:
                return

            show = lines[num_printed:num_lines]
            show = "".join(show)
            show = Text.from_ansi(show)
            self.live.console.print(show)

            self.printed = lines[:num_lines]

        if final:
            self.live.update(Text(""))
            self.live.stop()
            self.live = None
        else:
            rest = lines[num_lines:]
            rest = "".join(rest)
            # rest = '...\n' + rest
            rest = Text.from_ansi(rest)
            self.live.update(rest)
import os
from xml.etree.ElementTree import Element
import re
def link_fp(line: str, fn: str | Path, lineno: int, render=True) -> Text | str:
    encoded_path = str(fn) if isinstance(fn, Path) else fn
    link = f"{encoded_path}:{lineno}"
    if render:
        return Text.assemble((line, link))
    return f"[{line}]({link})"

class Markdown:
    """Stream formatted JSON-like text to the terminal with live updates."""

    def __init__(self, data=None, mdargs=None, style="default", save=None, min_delay=0.05, live_window=6):
        logger.debug(f"Initializing MarkdownStreamer with data: {data}")
        self.data = data or {}
        self.mdargs = mdargs or {}
        self.style = style
        self.console = Console(style=self.style)
        self._save = save
        self.min_delay = min_delay
        self.live_window = live_window
        self.last_update_time = time.time()
        self.printed_lines = []

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> None:
        """Load JSON data into the MarkdownStreamer."""
        return cls(data=json_data)
    @classmethod
    def from_web(cls, url: str | Element) -> None:
            from mrender.web2md import html_to_markdown_with_depth
            from bs4 import BeautifulSoup
            from httpx import get
            if not isinstance(url, str):
                return cls(html_to_markdown_with_depth(url, 0))
            response = get(url)

            return cls(html_to_markdown_with_depth(Element(BeautifulSoup(response.text, "html.parser").prettify()), 0))
    @classmethod
    def show_pytype(cls, type_: TypeVar) -> None:
        from mrender.render import display_rich_output
        display_rich_output(type_)

    @classmethod
    def from_docs(cls,moduleorpath:str |ModuleType) -> None:
        from mrender.docs2md import generate_docs
        import inspect
        if not isinstance(moduleorpath, (str, ModuleType)):
            moduleorpath = inspect.getmodule(moduleorpath)
        if isinstance(moduleorpath, ModuleType):
            moduleorpath = moduleorpath.__file__
        return cls(generate_docs(moduleorpath))

    def getlines(self, data=None, depth=0):
        """Generate Markdown from JSON with headers based on depth."""
        markdown_lines = []
        indent = "  " * depth
        depth = min(3, depth)
        if isinstance(data, dict):
            if "name" in data:
                title = f"\n{indent}{'#' * max(1, depth)} {data['name']}"
                if "brief" in data and data["brief"]:
                    title += f" - {data['brief']}"
                else:
                    title += "\n"
                markdown_lines.append(title)
            
            # Only process members if we have them and aren't in compact mode
            if "members" in data and isinstance(data["members"], dict):
                if "brief" in data and data["brief"]:
                    for member_name, member_info in data["members"].items():
                        markdown_lines.append(f"{indent}- **{member_name}** {'- ' + member_info['brief'] if 'brief' in member_info else ''}\n")
                    for member_name, member_info in data["members"].items():
                        markdown_lines.append(f"{indent}- **{member_name}**\n")
                
            if "doc" in data and data["doc"]:
                # Format documentation with proper indentation
                doc_lines = str(data["doc"]).split("\n")
                formatted_doc = []
                for line in doc_lines:
                    if line.strip():
                        if line.startswith('@param'):
                            # Format parameter documentation
                            formatted_doc.append(f"{indent}> **{line.strip()}**")
                        else:
                            formatted_doc.append(f"{indent}> {line.strip()}")
                markdown_lines.extend(formatted_doc)
                markdown_lines.append('')
                
            # Handle return type if available
            if "return_type" in data and data["return_type"]:
                markdown_lines.append(f"{indent}**Returns:** `{data['return_type']}`\n")
                
            # Handle members and other attributes
            for key, value in data.items():
                if key in ("name", "doc", "return_type"):
                    continue
                    
                if key == "members" and isinstance(value, dict):
                    for member_name, member_info in value.items():
                        markdown_lines.extend(self.getlines(member_info, depth + 1))
                elif isinstance(value, (dict, list)):
                    markdown_lines.append(f"\n{indent}- **{key}**:\n")
                    markdown_lines.extend(self.getlines(value, depth + 1))
                elif isinstance(value, str) and value:
                    # Handle file links
                    if key == "path" and "file://" in value:
                        markdown_lines.append(f"{indent}- **{key}**: {value}\n")
                    else:
                        markdown_lines.append(f"{indent}- **{key}**: {value}\n")

        elif isinstance(data, list):
            for item in data:
                markdown_lines.extend(self.getlines(item, depth))
        self.lines = markdown_lines
        return markdown_lines

    # def generate_markdown(self, data: Any = None, depth: int = 0) -> list:
    #     """Generate Markdown lines from data dynamically based on any keys."""
    #     markdown_lines = []
    #     indent = "  " * depth

    #     if isinstance(data, dict):
    #         for key, value in data.items():
    #             formatted_key = key.capitalize()
    #             if isinstance(value, dict):
    #                 markdown_lines.append(f"\n{indent}**{formatted_key}:**\n")
    #                 markdown_lines.extend(self.generate_markdown(value, depth + 1))
    #             elif isinstance(value, list):
    #                 markdown_lines.append(f"\n{indent}**{formatted_key}:**\n")
    #                 for item in value:
    #                     if isinstance(item, dict):
    #                         markdown_lines.append(f"{indent}- ")
    #                         markdown_lines.extend(self.generate_markdown(item, depth + 2))
    #                     else:
    #                         markdown_lines.append(f"{indent}- {item}\n")
    #             elif isinstance(value, str) and value.startswith("[") and value.endswith("/]"):
    #                 markdown_lines.append(Text(value))
    #             else:
    #                 formatted_value = self.format_value(key, value)
    #                 markdown_lines.append(f"{indent}**{formatted_key}:** {formatted_value}\n")
    #     elif isinstance(data, list):
    #         for item in data:
    #             if isinstance(item, dict):
    #                 markdown_lines.extend(self.generate_markdown(item, depth))
    #             elif isinstance(item, str) and item.startswith("[") and item.endswith("/]"):
    #                 markdown_lines.append(Text(item))
    #             else:
    #                 markdown_lines.append(f"{indent}- {item}\n")
    #     elif isinstance(data, str) and data.startswith("[") and data.endswith("/]"):
    #         markdown_lines.append(Text(data))
    #         pass
    #     else:

    #         markdown_lines.append(f"{indent}{data}\n")

    #     return markdown_lines

    def format_value(self, key: str, value: Any) -> str:
        """Format the value based on its key and type."""
        code_keys = {"signature", "code"}
        if key.lower() in code_keys and isinstance(value, str):
            return f"```python\n{value}\n```"
        elif isinstance(value, str) and (value.startswith("http://") or value.startswith("https://")):
            return f"[{value}]({value})"
        else:
            return str(value)

    # def getlines(self, data=None, depth=0):
    #     """Generate Markdown from JSON with headers based on depth."""
    #     data = data if data else self.data
    #     markdown_lines = self.generate_markdown(data, depth)
    #     return markdown_lines

    def rich(self, data=None, mdargs=None):
        """Render the markdown content using the Rich library."""
        mdargs = mdargs or {}
        data = data or self.data
        data = "\n".join(self.getlines(data))
        self.console.print(RichMarkdown(data)) 
        return RichMarkdown(data, **mdargs)

    def save(self, data=None, outfile: str = None):
        """Save the markdown content to a file."""
        data = data or self.data
        data = "\n".join(self.getlines(data))
        print(data)
        outfile = outfile or self._save or "output.md"
        Path(outfile).write_text(data)
        return  self
    def stream(self, speed_factor=40000, outfile: str = None):
        """Stream the markdown content dynamically based on its length."""
        self._save = bool(outfile)
        data = "\n".join(self.getlines(self.data))
        if self._save:
            Path(outfile).write_text(data)
        markdown_content = "\n".join(self.getlines(self.data))
        content_length = len(markdown_content)
        if content_length == 0:
            logger.error("No content to stream.")
            return
        speed = max(0.01, min(0.1, speed_factor / content_length))  # Adjust speed dynamically
        speed /= 2
        refresh_speed = 1 / 20

        pm = MarkdownStream()

        for i in range(6, len(markdown_content)):
            pm.update(markdown_content[:i], final=False)
            time.sleep(speed * refresh_speed)

        pm.update(markdown_content, final=True)

def recursive_read(file, include=None, depth=0, max_depth=5):
    """Recursively read files or directories and return their content as a dictionary."""
    if depth > max_depth and max_depth > 0:
        return {}
    include = include or {".json", ".md", ".txt", ".yaml", ".toml", ".py"}
    data = {}
    file_path = Path(file).resolve()
    print(f"Reading path: {file_path}")
    if file_path.is_file() and file_path.suffix in include and "__pycache__" not in str(file_path) and ".pyc" not in str(file_path):
        print(f"Reading file: {file_path}")
        logger.info(f"Reading file: {file_path}")
        content = file_path.read_text()
        if file_path.suffix == ".py":
            data[str(file_path)] =  "\n# " + file_path.name + "\n" + "```python\n" + content + "\n```\n"
        else:
            data[str(file_path)] = content
    elif file_path.is_dir():
        print(f"Reading directory: {file_path}")
        for sub_path in [p for p in file_path.iterdir() if "__pycache__" not in str(p) and ".pyc" not in str(p)]:
            print(f"Reading sub-path: {sub_path}")
            child = recursive_read(sub_path, include, depth + 1, max_depth)
            print(f"Child: {child}")
            data.update(child)
    return data


@click.command("mdstream")
@click.argument("file", type=click.Path(exists=True))
@click.option("--depth", "-d", default=-1, help="Depth of headers")
@click.option("--save", "-s", help="Save markdown content to a file")
def cli(file, depth, save):
    """Stream markdown content from a file."""
    data = recursive_read(file,depth=0,max_depth=depth) 
    md_streamer = Markdown(data=data, save=save)
    from rich.traceback import install
    install(show_locals=True)
    md_streamer.stream()


def example():
    """Run an example with predefined JSON data."""
    json_data = [
        {
            "name": "markdown-to-json",
            "version": "2.1.2",
            "summary": "Markdown to dict and json deserializer",
            "latest_release": "2024-09-20T20:38:56",
            "author": "Nathan Vack",
            "earliest_release": {"version": "1.0.0", "upload_time": "2015-12-10T21:01:13", "requires_python": None},
            "urls": {
                "Bug Tracker": "https://github.com/njvack/markdown-to-json/issues",
                "Change Log": "https://github.com/njvack/markdown-to-json/blob/main/CHANGELOG.md",
            },
            "description": "# Markdown to JSON converter\n## Description\nA simple tool...",
            "requires_python": ">=3.8",
        }
    ]

    md_streamer = Markdown(data=json_data)
    md_streamer.stream()


if __name__ == "__main__":
    cli()
