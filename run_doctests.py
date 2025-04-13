import re  # hey look, it's the `re` module
import sys
from doctest import DocTestParser, DocTestRunner
from pathlib import Path

CODEBLOCK_RE = re.compile(
    r"""
    ```py(?:thon)?\n
    (?P<code>.+?)\n
    ```\n
    (?:
        <!--
        \s*\^opts\s+
        (?P<options>[^-#]+)  # space-separated options
        (?:\#[^-\n]+)?       # comment
        -->
    )?
    """,
    re.DOTALL | re.UNICODE | re.VERBOSE,
)


def make_context() -> dict[str, object]:
    return {"re": re}


def get_lineno(string: str, pos: int) -> int:
    match = None
    for lineno, match in enumerate(re.finditer(r"\n|$", string), 1):
        if match.start() >= pos:
            return lineno
    return -1


executed = 0
skipped = 0

runner = DocTestRunner()
for md_path in Path().glob("./docs/**/*.md"):
    markdown = md_path.read_text()
    context = make_context()
    for match in CODEBLOCK_RE.finditer(markdown):
        options = set((match["options"] or "").casefold().strip().split())
        if "skip" in options:
            skipped += 1
            continue
        executed += 1
        code = match["code"]

        lineno = get_lineno(markdown, match.start("code"))
        doctest = DocTestParser().get_doctest(
            code, context, str(md_path), str(md_path), lineno)
        runner.run(doctest, clear_globs=False)

        if "keep_context" not in options:
            context = make_context()

results = runner.summarize()

if results.failed > 0:
    sys.exit(1)
else:
    print(f"{executed} snippets executed")
    print(f"{skipped} snippets skipped")