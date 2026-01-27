"""HTML to Markdown conversion."""

from __future__ import annotations

import mdformat
from bs4 import BeautifulSoup, NavigableString, Tag
from markdownify import ATX, MarkdownConverter


def _should_remove(tag: Tag) -> bool:
    """Check if a tag should be removed during autoclean."""
    if tag.name in {"img", "svg"}:
        return True
    if tag.name == "a" and tag.img:
        return True
    classes = tag.get("class") or ()
    if tag.name == "a" and "headerlink" in classes:
        return True
    if "twemoji" in classes:
        return True
    return "tabbed-labels" in classes


def _autoclean(soup: BeautifulSoup | Tag) -> None:
    """Remove unwanted elements from HTML."""
    for element in soup.find_all(_should_remove):
        element.decompose()

    # Unwrap autoref elements
    for element in soup.find_all("autoref"):
        element.replace_with(NavigableString(element.get_text()))

    # Remove line numbers from code blocks
    for element in soup.find_all("table", attrs={"class": "highlighttable"}):
        code = element.find("code")
        if code:
            element.replace_with(
                BeautifulSoup(f"<pre>{code.get_text()}</pre>", "html.parser")
            )


def _get_language(tag: Tag) -> str:
    """Extract language from code block classes.

    The callback receives the <pre> tag, so we need to check:
    1. Classes on the <pre> tag itself
    2. Classes on the parent of <pre>
    3. Classes on child <code> element (common pattern: <pre><code class="language-X">)
    """
    classes: list[str] = list(tag.get("class") or ())

    # Check parent classes
    if tag.parent:
        classes.extend(tag.parent.get("class") or ())

    # Check child <code> element classes
    code_child = tag.find("code")
    if code_child:
        classes.extend(code_child.get("class") or ())

    for css_class in classes:
        if css_class.startswith("language-"):
            return css_class[9:]
    return ""


# Converter with mkdocs-llmstxt-compatible settings
_converter = MarkdownConverter(
    bullets="-",
    code_language_callback=_get_language,
    escape_underscores=False,
    heading_style=ATX,
)


def html_to_markdown(html: str, content_selector: str | None = None) -> str:
    """Convert HTML to clean Markdown.

    Args:
        html: Raw HTML content.
        content_selector: Optional CSS selector for main content.
            Defaults to Material for MkDocs selectors.

    Returns:
        Cleaned Markdown text.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Find main content
    if content_selector:
        content = soup.select_one(content_selector)
    else:
        content = (
            soup.select_one(".md-content__inner")
            or soup.select_one("article")
            or soup.select_one("main")
            or soup
        )

    if content is None:
        return ""

    _autoclean(content)
    md = _converter.convert_soup(content)
    return mdformat.text(md, options={"wrap": "no"}, extensions=("tables",))
