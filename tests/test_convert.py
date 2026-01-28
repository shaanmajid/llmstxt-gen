"""Tests for HTML to Markdown conversion."""

from llmstxt_standalone.convert import html_to_markdown


def test_html_to_markdown_basic():
    html = """
    <article>
        <h1>Title</h1>
        <p>This is <strong>bold</strong> text.</p>
    </article>
    """
    result = html_to_markdown(html)
    assert "# Title" in result
    assert "**bold**" in result


def test_html_to_markdown_removes_images():
    html = """
    <article>
        <p>Text</p>
        <img src="test.png" alt="test">
    </article>
    """
    result = html_to_markdown(html)
    assert "img" not in result.lower()
    assert "test.png" not in result


def test_html_to_markdown_removes_headerlinks():
    html = """
    <article>
        <h2>Section<a href="#section" class="headerlink">¶</a></h2>
    </article>
    """
    result = html_to_markdown(html)
    assert "¶" not in result
    assert "headerlink" not in result


def test_html_to_markdown_preserves_code_language():
    html = """
    <article>
        <pre><code class="language-python">print("hello")</code></pre>
    </article>
    """
    result = html_to_markdown(html)
    assert "```python" in result
    assert 'print("hello")' in result


def test_html_to_markdown_default_mkdocs_theme():
    """Test that [role="main"] selector works for default MkDocs theme."""
    html = """
    <html>
    <body>
    <nav class="navbar"><a href="/">Home</a></nav>
    <div class="col-md-9" role="main">
        <h1>Main Content</h1>
        <p>This should be extracted.</p>
    </div>
    <footer>Footer</footer>
    </body>
    </html>
    """
    result = html_to_markdown(html)
    assert "# Main Content" in result
    assert "This should be extracted" in result
    assert "navbar" not in result.lower()
    assert "Footer" not in result
