# Release Notes — v0.1.0

## Highlights
- CLI-first workflow: `simulate`, `plot`, `analyze` (no YAML needed).
- Simulation modes: deterministic, mc, gillespie (plus reference per-nucleus).
- Plots: images/nt_curve.png, images/log_nt.png, background: *_bg.png, fit: log_fit.png.
- Half-life & λ estimation: `python -m src.analyze --run-dir data/runs/last --out images`.
- Isotope presets: Tc-99m, I-131, Cs-137, Co-60, F-18, C-11, N-13, O-15, I-123, Tl-201, Y-90, Lu-177, Xe-133, Mo-99, Ba-133.
- Docs: CLI Quickstart, Outputs, Background noise, Half-life estimation, Project Structure, Sample Plots.
- CI: GitHub Actions (pytest + smoke plots) + README CI badge.
- License: MIT.

## Getting Started (quick)

    # Monte-Carlo (lambda direct) + plots
    python -m src.cli simulate --mode mc --lambda 0.2 --n0 2000 --tmax 5 --dt 0.1 --seed 1 --plot

    # F-18 in minutes + analysis
    python -m src.cli simulate --mode mc --isotope f18 --half-life-unit min --n0 100000 --tmax 240 --dt 1 --seed 42 --plot
    python -m src.cli analyze --run-dir data/runs/last --out images

## Known Notes
- Keep `--half-life-unit`, `dt`, and `tmax` in the same unit.
- If a YAML exists that overrides flags, rename it or prefer the CLI.
