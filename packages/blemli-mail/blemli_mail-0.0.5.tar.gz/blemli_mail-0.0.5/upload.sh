uv venv
source .venv/bin/activate
uv pip install --upgrade twine
uv pip install --upgrade build
rm -rf dist/*
python3 -m build
python3 -m twine upload --repository pypi dist/* --user __token__
