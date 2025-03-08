from argparse import ArgumentParser
try:
    from .pdfconversion import convert_markdown_to_pdf, convert_to_pdf
except ImportError:
    from pdfconversion import convert_markdown_to_pdf, convert_to_pdf
import os
import sys
from termcolor import cprint
import warnings

warnings.filterwarnings("ignore")

def main():
    parser = ArgumentParser()
    parser.add_argument("-i", "--inputfile", 
                       help="Path to the input file that needs to be converted to PDF",
                       required=True, type=str)
    parser.add_argument("-o", "--outputfile",
                       help="Path to the output PDF file",
                       required=True, type=str)
    parser.add_argument("-t", "--title",
                       help="Title to include in the PDF metadata. Default: 'PDF Title'",
                       required=False, default="PDF Title", type=str)

    args = parser.parse_args()
    inf = args.inputfile
    outf = args.outputfile
    titl = args.title

    if os.path.splitext(inf)[1] not in [".docx", ".html", ".xml", ".csv", ".md", ".pptx", ".xlsx"]:
        cprint(f"ERROR! File format for {inf} not supported, please provide a file that has one of the following formats:\n\n- "+"\n- ".join([".docx", ".html", ".xml", ".csv", ".md", ".pptx", ".xlsx"]),
               color="red", file=sys.stderr)
        sys.exit(1)
    elif os.path.splitext(outf)[1] != ".pdf":
        cprint(f"ERROR! File format for {outf} is not PDF, please provide a PDF file as output",
               color="red", file=sys.stderr)
        sys.exit(2)
    else:
        if os.path.splitext(inf)[1] != ".md":
            try:
                outf = convert_to_pdf(inf, outf, titl)
                cprint("Conversion successful!🎉",
                      color="green", attrs=["bold"], file=sys.stdout)
                sys.exit(0)
            except Exception as e:
                cprint(f"ERROR! Error:\n\n{e}\n\nwas raised during conversion",
                      color="red", file=sys.stderr)
                sys.exit(3)
        else:
            try:
                outf = convert_markdown_to_pdf(inf, outf, titl)
                cprint("Conversion successful!🎉",
                      color="green", attrs=["bold"], file=sys.stdout)
                sys.exit(0)
            except Exception as e:
                cprint(f"ERROR! Error:\n\n{e}\n\nwas raised during conversion",
                      color="red", file=sys.stderr)
                sys.exit(3)

if __name__ == "__main__":
    main()