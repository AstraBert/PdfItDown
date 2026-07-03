if [[ "$1" == "liteparse" ]]
then
    rm -rf .venv/
    mv pyproject-lit.toml pyproject.toml
    uv sync
    du -h .venv/lib
    mv pyproject.toml pyproject-lit.toml
elif [[ "$1" == "native" ]]
then
    rm -rf .venv/
    mv pyproject-native.toml pyproject.toml
    uv sync
    du -h .venv/lib
    mv pyproject.toml pyproject-native.toml
else
    rm -rf .venv/
    mv pyproject-markitdown.toml pyproject.toml
    uv sync
    du -h .venv/lib
    mv pyproject.toml pyproject-markitdown.toml
fi
