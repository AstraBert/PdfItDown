"""Markdown to pdf converter based on markdown_it and fitz."""
import io
import typing
import pathlib
from markdown_it import MarkdownIt
import fitz


class Section:
    """Markdown section."""

    def __init__(
      self,
      text: str,
      toc: bool = True,
      root: str = ".",
      paper_size: str = "A4",
      borders: tuple = (36, 36, -36, -36)
    ):
        """Create md section with given properties."""
        self.text = text
        self.toc = toc
        self.root = root
        # https://pymupdf.readthedocs.io/en/latest/functions.html#paper_size
        self.paper_size = paper_size
        self.borders = borders


class MarkdownPdf:
    """Converter class."""

    meta = {
      "creationDate": fitz.get_pdf_now(),
      "modDate": fitz.get_pdf_now(),
      "creator": "PyMuPDF library: https://pypi.org/project/PyMuPDF",
      "producer": None,
      "title": None,
      "author": None,
      "subject": None,
      "keywords": None,
    }

    def __init__(self, toc_level: int = 6, mode: str = 'commonmark'):
        """Create md -> pdf converter with given TOC level and mode of md parsing."""
        self.toc_level = toc_level
        self.toc = []

        # zero, commonmark, js-default, gfm-like
        # https://markdown-it-py.readthedocs.io/en/latest/using.html#quick-start
        self.m_d = (MarkdownIt(mode).enable('table'))  # Enable support for tables

        self.out_file = io.BytesIO()
        self.writer = fitz.DocumentWriter(self.out_file)
        self.page = 0

    @staticmethod
    def _recorder(elpos):
        """Call function invoked during story.place() for making a TOC."""
        if not elpos.open_close & 1:  # only consider "open" items
            return
        if not elpos.toc:
            return

        if 0 < elpos.heading <= elpos.pdfile.toc_level:  # this is a header (h1 - h6)
            elpos.pdfile.toc.append((
                elpos.heading,
                elpos.text,
                elpos.pdfile.page,
                elpos.rect[1],  # top of written rectangle (use for TOC)
            ))

    def add_section(self, section: Section, user_css: typing.Optional[str] = None) -> None:
        """Add markdown section to pdf."""
        rect = fitz.paper_rect(section.paper_size)
        where = rect + section.borders
        story = fitz.Story(html=self.m_d.render(section.text), archive=section.root, user_css=user_css)
        more = 1
        while more:  # loop outputting the story
            self.page += 1
            device = self.writer.begin_page(rect)
            more, _ = story.place(where)  # layout into allowed rectangle
            story.element_positions(self._recorder, {"toc": section.toc, "pdfile": self})
            story.draw(device)
            self.writer.end_page()

    def save(self, file_name: typing.Union[str, pathlib.Path]) -> None:
        """Save pdf to file."""
        self.writer.close()
        doc = fitz.open("pdf", self.out_file)
        doc.set_metadata(self.meta)
        if self.toc_level > 0:
            doc.set_toc(self.toc)
        doc.save(file_name)
        doc.close()