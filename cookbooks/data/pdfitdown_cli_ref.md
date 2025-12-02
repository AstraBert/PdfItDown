**PdfItDown** comes with a command line application from which you can comfortably convert all your files without actually touching a single line of code.

Based on [click](https://click.palletsprojects.com/en/stable/), the CLI is designed to offer a seamless experience, with almost as much control of inputs and outputs as if you were to write the flow in python: it is then the perfect choice if you want an easy and intuitive approach to file conversion, without getting your hands dirty with code.

## Usage

Below are some example commands for using PdfItDown from the terminal, along with explanations for each option and scenario:

### Convert a single file to PDF

Use this command to convert a single file (e.g., a Markdown file) to PDF and set a custom title in the PDF metadata:

```bash
pdfitdown -i README.md -o README.pdf -t "README"
```
- `-i README.md`: Specifies the input file to convert.
- `-o README.pdf`: Sets the output PDF file path.
- `-t "README"`: Sets the PDF title metadata.

### Convert multiple files with custom output paths

You can convert several files at once, specifying a matching output PDF for each input:

```bash
pdfitdown -i test0.png -i test1.md -o testoutput0.pdf -o testoutput1.pdf
```
- Multiple `-i` flags: List each input file you want to convert.
- Multiple `-o` flags: Provide an output path for each input file, in the same order.

### Convert multiple files with inferred output paths

If you omit the output file paths, PdfItDown will automatically generate PDF filenames based on your input files:

```bash
pdfitdown -i test0.png -i test1.csv
```
- Output files will be named after the input files, with `.pdf` extensions.

### Bulk convert all files in a directory

To convert every file in a directory to PDF in one go:

```bash
pdfitdown -d tests/data/testdir
```
- `-d tests/data/testdir`: Specifies the directory containing files to convert. All supported files in this directory will be converted to PDF.

---

For more details on available options, run:

```bash
pdfitdown --help
```