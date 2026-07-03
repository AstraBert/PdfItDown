rm -rf data/*-rs.pdf

if [[ "$1" == "liteparse" ]]
then
    rm -rf .venv/
    mv pyproject-lit.toml pyproject.toml
    uv sync
    mkdir -p results/lit/
    hyperfine --warmup 3 --runs 20 '../../target/release/pdfitdown --inputfile data/office1.docx --outputfile data/office1-rs.pdf' '.venv/bin/pdfitdown --inputfile data/office1.docx --outputfile data/office1-lit-py.pdf' --export-json results/lit/office1.json
    hyperfine --warmup 3 --runs 20 '../../target/release/pdfitdown --inputfile data/office2.xlsx --outputfile data/office2-rs.pdf' '.venv/bin/pdfitdown --inputfile data/office2.xlsx --outputfile data/office2-lit-py.pdf' --export-json results/lit/office2.json
    hyperfine --warmup 3 --runs 20 '../../target/release/pdfitdown --inputfile data/office3.pptx --outputfile data/office3-rs.pdf' '.venv/bin/pdfitdown --inputfile data/office3.pptx --outputfile data/office3-lit-py.pdf' --export-json results/lit/office3.json
    mv pyproject.toml pyproject-lit.toml
else
    # rm -rf .venv/
    # mv pyproject-markitdown.toml pyproject.toml
    # uv sync
    mkdir -p results/markitdown/
    hyperfine --warmup 3 --runs 20 '../../target/release/pdfitdown --inputfile data/office1.docx --outputfile data/office1-rs.pdf' '.venv/bin/pdfitdown --inputfile data/office1.docx --outputfile data/office1-py.pdf' --export-json results/markitdown/office1.json
    hyperfine --warmup 3 --runs 20 '../../target/release/pdfitdown --inputfile data/office2.xlsx --outputfile data/office2-rs.pdf' '.venv/bin/pdfitdown --inputfile data/office2.xlsx --outputfile data/office2-py.pdf' --export-json results/markitdown/office2.json
    hyperfine --warmup 3 --runs 20 '../../target/release/pdfitdown --inputfile data/office3.pptx --outputfile data/office3-rs.pdf' '.venv/bin/pdfitdown --inputfile data/office3.pptx --outputfile data/office3-py.pdf' --export-json results/markitdown/office3.json
    mv pyproject.toml pyproject-markitdown.toml
fi
