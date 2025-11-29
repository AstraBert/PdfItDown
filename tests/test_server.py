import pytest
import os
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.testclient import TestClient
from pdfitdown.server import mount
from pdfitdown.pdfconversion import Converter


@pytest.fixture(scope="module")
def starlette_app() -> Starlette:
    async def hello_world(request: Request) -> PlainTextResponse:
        return PlainTextResponse(content="hello world!")

    routes = [
        Route(path="/hello", endpoint=hello_world, methods=["GET"], name="hello_world")
    ]

    return Starlette(routes=routes)


@pytest.fixture()
def files_for_api() -> list[tuple[str, str]]:
    initial_files = [
        ("test.txt", "text/plain"),
        ("test0.png", "image/png"),
        (
            "test1.pptx",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ),
        ("outputfiles/sample.pdf", "application/pdf"),
    ]
    return [(os.path.join("tests/data", file[0]), file[1]) for file in initial_files]


def test_mount_adds_route(starlette_app: Starlette) -> None:
    c = Converter()
    name = "pdfitdown"
    path = "/conversions/pdf"
    app = mount(
        app=starlette_app,
        converter=c,
        path=path,
        name=name,
    )
    assert isinstance(app, Starlette)
    assert len(app.routes) == 2
    assert app.routes[1].name == "pdfitdown"
    assert app.routes[1].methods == set(["POST"])
    assert app.routes[1].path == "/conversions/pdf"


def test_pdfitdown_route(
    starlette_app: Starlette, files_for_api: list[tuple[str, str]]
) -> None:
    c = Converter()
    name = "pdfitdown"
    path = "/conversions/pdf"
    app = mount(
        app=starlette_app,
        converter=c,
        path=path,
        name=name,
    )
    client = TestClient(app=app)
    for file in files_for_api:
        with open(file[0], "rb") as f:
            file_data = f.read()
        response = client.post(
            "/conversions/pdf",
            files={"file_upload": (os.path.basename(file[0]), file_data, file[1])},
        )
        assert response.status_code == 200
        assert (
            response.headers.get("content-type") is not None
            and response.headers.get("content-type") == "application/pdf"
        )
        assert len(response.content) > 0


def test_pdfitdown_route_errors(starlette_app: Starlette) -> None:
    c = Converter()
    name = "pdfitdown"
    path = "/conversions/pdf"
    app = mount(
        app=starlette_app,
        converter=c,
        path=path,
        name=name,
    )
    client = TestClient(app=app)
    response = client.get("/conversions/pdf")
    assert response.status_code == 405
    png_bytes = b""  # will raise empty image error for the converter
    response = client.post(
        "/conversions/pdf",
        files={"file_upload": ("notanimage.png", png_bytes, "image/png")},
    )
    assert response.status_code == 500
