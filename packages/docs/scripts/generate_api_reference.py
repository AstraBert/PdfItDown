from re import sub as replace_regex
from sys import exit as exit_with_code
from pathlib import Path
from inspect import getmembers, isfunction
from pdfitdown.pdfconversion import Converter
from pdfitdown.pdfconversion._default_callback import convert_file
from pdfitdown.pdfconversion.models import OsPath, MultipleConversion
from pdfitdown.server import mount
from argparse import ArgumentParser
from typing import Callable, TypeVar, Type, TypedDict, Any

T = TypeVar("T")

def fn_to_markdown(fn: Callable) -> str:
    name = fn.__name__
    description = replace_regex(r"([A-Za-z0-9_]*)\s+\([A-Za-z0-9\[\]\|\s\,]*\)", r"`\g<0>`", (fn.__doc__ or "").replace("\n", "\n\n").replace("Args", "_Args_").replace("Returns", "_Returns_").replace("Raises", "_Raises_"))

    return f"### `{name}`\n\n{description}\n\n"

def class_to_markdown(cls: Type[T]) -> str:
    cls_name = cls.__name__
    cls_description = cls.__doc__

    methods = []

    i = 1

    for name, method in getmembers(cls, predicate=isfunction):
        if name.startswith("_"):
            continue
        method_des = replace_regex(r"([A-Za-z0-9_]*)\s+\([A-Za-z0-9\[\]\|\s\,]*\)", r"`\g<0>`", (method.__doc__ or "").replace("\n", "\n\n").replace("Args", "_Args_").replace("Returns", "_Returns_").replace("Raises", "_Raises_"))
        methods.append(
            f"{i}. `{name}`\n\n{method_des}\n\n"
        )
        i+=1

    doc =  f"### `{cls_name}`\n\n{cls_description}\n\n"
    if len(methods) > 0:
        doc += "**Methods**\n\n"
        for m in methods:
            doc += m
    return doc + "\n\n"

class ModuleRepr(TypedDict):
    title: str
    description: str
    functions: list[Callable]
    classes: list[Any]

class DocumentationPiece(TypedDict):
    files: dict[str, ModuleRepr]

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument(
        "--check",
        action="store_true",
        required=False,
        default=False
    )

    args = parser.parse_args()

    DOCS_TO_FNS: DocumentationPiece = {
        "files": {
            "api-reference/server.mdx": {"title": "API Reference - Server", "description": "API reference for server-related functions", "functions": [mount], "classes": []},
            "api-reference/converter.mdx": {"title": "API Reference - Conversion", "description": "AP reference for conversion-related functions and classes", "functions": [convert_file], "classes": [Converter]},
            "api-reference/models.mdx": {"title": "API Reference - Models", "description": "API reference for data models", "functions": [], "classes": [OsPath, MultipleConversion]}
        }
    }

    would_be_changed = False


    for doc in DOCS_TO_FNS["files"]:
        content = f"---\ntitle: {DOCS_TO_FNS['files'][doc]['title']}\ndescription: {DOCS_TO_FNS['files'][doc]['description']}\n---\n\n"
        if DOCS_TO_FNS["files"][doc]["classes"]:
            content += "## Classes\n\n"
            for cls in DOCS_TO_FNS["files"][doc]["classes"]:
                content += class_to_markdown(cls)
        if DOCS_TO_FNS["files"][doc]["functions"]:
            content += "## Functions\n\n"
            for fn in DOCS_TO_FNS["files"][doc]["functions"]:
                content += fn_to_markdown(fn)

        if not args.check:
            with open(doc, "w") as f:
                f.write(content)
        else:
            if Path(doc).exists():
                with open(doc, "r") as f:
                    original_content = f.read()
                if original_content != content:
                    print(f"File {doc} would be changed")
                    would_be_changed = True
                else:
                    print(f"File {doc} is up to date!")
            else:
                print(f"File {doc} does not exist and would be written")
                exit_with_code(1)
    if would_be_changed:
        print("API reference docs are not up-to-date, please run `make docs`.")
        exit_with_code(1)
    exit_with_code(0)
            

