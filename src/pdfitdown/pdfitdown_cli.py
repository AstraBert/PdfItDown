from argparse import ArgumentParser
from pdfconversion import Converter
import sys
from termcolor import cprint
import warnings
from pydantic import ValidationError

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
                       help="Title to include in the PDF metadata. Default: 'File Converted with PdfItDown'",
                       required=False, default="File Converted with PdfItDown", type=str)
    args = parser.parse_args()
    inf = args.inputfile
    outf = args.outputfile
    titl = args.title
    conv = Converter()
    try:
        outf = conv.convert(inf, outf, titl)
        cprint("Conversion successful!🎉", color="green", attrs=["bold"], file=sys.stdout)
        sys.exit(0)
    except ValidationError as e:
        cprint(f"ERROR! Error:\n\n{e}\n\nwas raised during conversion",color="red", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()