from argparse import ArgumentParser
try:
    from pdfconversion import Converter
except ModuleNotFoundError:
    from .pdfconversion import Converter
import sys
from termcolor import cprint
import warnings
from pydantic import ValidationError

warnings.filterwarnings("ignore")

def main():
    parser = ArgumentParser()
    parser.add_argument("-i", "--inputfile", 
                       help="Path to the input file(s) that need to be converted to PDF. The path should be comma separated: input1.csv,input2.md,...,inputN.xml.",
                       required=False, type=str, default=None)
    parser.add_argument("-o", "--outputfile",
                       help="Path to the output PDF file(s). If more than one input file is provided, you should provide an equally long list of output files. The path should be comma separated: output1.pdf,output2.pdf,...,outputN.pdf. Defaults to 'None'",
                       required=False, type=str, default=None)
    parser.add_argument("-t", "--title",
                       help="Title to include in the PDF metadata. Default: 'File Converted with PdfItDown'. If more than one file is provided, it will be ignored.",
                       required=False, default="File Converted with PdfItDown", type=str)
    parser.add_argument("-d", "--directory",
                       help="Directory whose files you want to bulk-convert to PDF. If the --inputfile argument is also provided, it will be ignored. Defaults to None.",
                       required=False, default=None, type=str)
    parser.add_argument("-r", "--reader",
                       help="Reader to extract text from files, must be one of 'markitdown', 'llamaparse', 'docling'",
                       required=False, default='markitdown', type=str)
    parser.add_argument("-k", "--api_key",
                       help="API key for LlamaCloud services, required only with 'llamaparse' as reader. Defaults to None.",
                       required=False, default=None, type=str)
    args = parser.parse_args()
    inf = args.inputfile
    outf = args.outputfile
    diri = args.directory
    titl = args.title
    rdr = args.reader
    apk = args.api_key
    conv = Converter(reader=rdr, llamacloud_api_key=apk)
    try:
        if inf is not None:
            if outf is not None and len(inf.split(",")) > 1:
                outf = conv.multiple_convert(inf.split(","), outf.split(","))
                cprint("Conversion successful!🎉", color="green", attrs=["bold"], file=sys.stdout)
                sys.exit(0)
            elif outf is None and len(inf.split(",")) > 1:
                outf = conv.multiple_convert(inf.split(","), outf)
                cprint("Conversion successful!🎉", color="green", attrs=["bold"], file=sys.stdout)
                sys.exit(0)
            elif outf is not None and len(inf.split(",")) == 1:
                outf = conv.convert(inf.split(",")[0], outf.split(",")[0], title=titl)
                cprint("Conversion successful!🎉", color="green", attrs=["bold"], file=sys.stdout)
                sys.exit(0)
            else:
                cprint(f"ERROR! Invalid input provided, check your input and output files",color="red", file=sys.stderr)
                sys.exit(1)
        elif inf is None and diri is None:
            cprint(f"ERROR! You should provide at least one of --inputfile or --directory",color="red", file=sys.stderr)
            sys.exit(1)
        else:
            outf = conv.convert_directory(diri)
            cprint("Conversion successful!🎉", color="green", attrs=["bold"], file=sys.stdout)
            sys.exit(0)
    except ValidationError as e:
        cprint(f"ERROR! Error:\n\n{e}\n\nwas raised during conversion",color="red", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()