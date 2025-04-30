# Github Pages

The content is generated using Python with Jinja2 templates in `pages-source` directory
and served via GitHub pages from `pages/` directory.

## Prerequisites

* Python 3.10 or higher
* [uv](https://pypi.org/project/uv/)
* [GitHub CLI](https://cli.github.com/) - for deployment

## Local development

```
uv sync
uv run -m pages_src.generate --dev
# in another terminal
uv run -m http.server -d .data/pages
```

View the pages at http://localhost:8000
