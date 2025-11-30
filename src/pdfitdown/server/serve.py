try:
    import os
    import shutil
    from tempfile import mkdtemp
    from typing import cast
    from pathlib import Path
    from mimetypes import guess_extension
    from starlette.applications import Starlette
    from starlette.responses import StreamingResponse
    from starlette.exceptions import HTTPException
    from starlette.requests import Request
    from starlette.routing import Route
    from starlette.datastructures import UploadFile
    from starlette.middleware import Middleware
    from ..pdfconversion import Converter

    STARLETTE_AVAILABLE = True
except ImportError:
    STARLETTE_AVAILABLE = False

if STARLETTE_AVAILABLE:

    def _build_pdfitdown_route(
        converter: Converter,
        path: str,
        middleware: list[Middleware] | None = None,
        name: str | None = None,
        uploaded_file_field: str = "file_upload",
    ) -> Route:
        """
        Build a Starlette route for PDF conversion using PdfItDown.

        Args:
            converter (Converter): The PdfItDown converter instance.
            path (str): The route path to mount.
            middleware (list[Middleware] | None): Optional list of Starlette middleware.
            name (str | None): Optional route name.
            uploaded_file_field (str): The form field name for the uploaded file.

        Returns:
            Route: A Starlette Route configured for PDF conversion.
        """

        async def pdfitdown_route(request: Request) -> StreamingResponse:
            if request.method.lower() != "post":
                raise HTTPException(
                    status_code=405, detail=f"Method not allowed: {request.method}"
                )
            async with request.form() as form:
                temp_dir = mkdtemp()
                if isinstance((uploaded_file := form[uploaded_file_field]), UploadFile):
                    extension = (
                        guess_extension(
                            uploaded_file.headers.get("Content-Type", "text/plain")
                        )
                        or ".txt"
                    )
                    file_name = uploaded_file.filename or "filename" + extension
                    file_content = await uploaded_file.read()
                else:
                    file_name = "filename.txt"
                    file_content = bytes(
                        cast(str, form[uploaded_file_field]), encoding="utf-8"
                    )
                tmp = os.path.join(temp_dir, file_name)
                with open(tmp, "wb") as f:
                    f.write(file_content)
                output_filename = file_name.replace(Path(file_name).suffix, ".pdf")
                output_path = os.path.join(temp_dir, output_filename)
                try:
                    converter.convert(tmp, output_path)
                    with open(output_path, "rb") as f:
                        pdf_bytes = f.read()
                    return StreamingResponse(
                        content=iter([pdf_bytes]),
                        status_code=200,
                        media_type="application/pdf",
                        headers={
                            "Content-Disposition": f'attachment; filename="{output_filename}"'
                        },
                    )
                except Exception as e:
                    raise HTTPException(
                        status_code=500, detail=f"Internal server error: {e}"
                    )
                finally:
                    shutil.rmtree(temp_dir, ignore_errors=True)

        return Route(
            path=path,
            endpoint=pdfitdown_route,
            methods=["POST"],
            name=name,
            middleware=middleware,
        )

    def mount(
        app: Starlette,
        converter: Converter,
        path: str,
        middleware: list[Middleware] | None = None,
        name: str | None = None,
        uploaded_file_field: str = "file_upload",
    ) -> Starlette:
        """
        Mount the PdfItDown PDF conversion route to a Starlette app.

        Args:
            app (Starlette): The Starlette application instance.
            converter (Converter): The PdfItDown converter instance.
            path (str): The route path to mount.
            middleware (list[Middleware] | None): Optional list of Starlette middleware.
            name (str | None): Optional route name.
            uploaded_file_field (str): The form field name for the uploaded file.

        Returns:
            Starlette: The Starlette app with the PDF conversion route mounted.
        """
        app.routes.append(
            _build_pdfitdown_route(
                converter, path, middleware, name, uploaded_file_field
            )
        )
        return app
else:

    def _build_pdfitdown_route(*args, **kwargs):
        """
        Build a Starlette route for PDF conversion using PdfItDown.

        Args:
            converter (Converter): The PdfItDown converter instance.
            path (str): The route path to mount.
            middleware (list[Middleware] | None): Optional list of Starlette middleware.
            name (str | None): Optional route name.
            uploaded_file_field (str): The form field name for the uploaded file.

        Returns:
            Route: A Starlette Route configured for PDF conversion.
        """
        raise NotImplementedError(
            "You need to install the 'server' dependency group for this function to work: `pip install pdfitdown[server]`. Alternatively, you can install 'startlette' directly: `pip install starlette`"
        )

    def mount(*args, **kwargs):
        """
        Mount the PdfItDown PDF conversion route to a Starlette app.

        Args:
            app (Starlette): The Starlette application instance.
            converter (Converter): The PdfItDown converter instance.
            path (str): The route path to mount.
            middleware (list[Middleware] | None): Optional list of Starlette middleware.
            name (str | None): Optional route name.
            uploaded_file_field (str): The form field name for the uploaded file.

        Returns:
            Starlette: The Starlette app with the PDF conversion route mounted.
        """
        raise NotImplementedError(
            "You need to install the 'server' dependency group for this function to work: `pip install pdfitdown[server]`. Alternatively, you can install 'startlette' directly: `pip install starlette`"
        )
