# Changelog
All notable changes to this project will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- (Planned) Docs site (Sphinx/MkDocs) with examples gallery
- (Planned) Benchmarks comparing `binomial` vs `per_nucleus` vs `numba`
- (Planned) Parameter sweeps and CSV summaries
- (Planned) Decay chain A→B demo & plots

## [0.1.0] - 2025-09-05
### Added
- CLI-first workflow: `simulate`, `plot`, `analyze` (no YAML needed)
- Isotope presets (Tc-99m, I-131, Cs-137, Co-60, F-18, C-11, N-13, O-15, I-123, Tl-201, Y-90, Lu-177, Xe-133, Mo-99, Ba-133)
- Background counts tool + plots (`*_bg.png`)
- Half-life & λ estimation (`src.analyze`) + `images/log_fit.png`
- Reproducible runs: `data/runs/<timestamp>/` + `data/runs/last` symlink
- CI via GitHub Actions, tests (green badge), license (MIT)
