# Contributing

Thanks for helping! This is a small teaching project, but we keep a few basics.

## Setup
    python -m pip install -r requirements.txt
    python -m pip install -e .
    pytest -q

## Running things
- Quick run: `./run.sh`
- CLI: `raddecay simulate ...`, `raddecay analyze ...`, `raddecay bg ...`
- Plots land in `images/` (ignored by git); published examples live in `assets/`
- Repro runs: `data/runs/<timestamp>/` and symlink `data/runs/last`

## Tests & style
- Add/modify tests under `tests/`; run `pytest -q`
- Keep random seeds fixed in tests
- Prefer vectorized NumPy; use Numba only where it clearly wins

## Benchmarks
    python -m src.bench
    # outputs: assets/bench_runtime.csv, assets/bench_runtime.png

## Commit messages
- Conventional-ish: `feat: ...`, `fix: ...`, `docs: ...`, `chore: ...`, `ci: ...`
- One change per commit when possible

## Releasing
- Bump version in `pyproject.toml` and `CITATION.cff`
- Update `CHANGELOG.md`
- Tag: `git tag -a vX.Y.Z -m "..." && git push origin vX.Y.Z`
- Create GitHub release; Zenodo creates the DOI automatically
