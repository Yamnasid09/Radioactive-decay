# src/cli.py  — minimal, indentation-safe CLI

import argparse
import math
import subprocess
import sys

PRESETS = {
    "tc99m": ("h", 6.01),
    "i131":  ("d", 8.02),
    "cs137": ("y", 30.05),
    "co60":  ("y", 5.27),
}

UNIT_SEC = {"s": 1, "min": 60, "h": 3600, "d": 86400, "y": 365.25 * 86400}


def _lambda_in_unit_from_half_life(half_life_value: float, half_life_unit: str, out_unit: str) -> float:
    """Convert half-life (value, unit) to lambda in 1/out_unit."""
    seconds = half_life_value * UNIT_SEC[half_life_unit]
    lam_per_sec = math.log(2) / seconds
    return lam_per_sec * UNIT_SEC[out_unit]


def _resolve_lambda(args) -> float:
    # priority: --lambda > --half-life > --isotope
    if args.lambda_ is not None:
        return float(args.lambda_)
    if args.half_life is not None:
        return _lambda_in_unit_from_half_life(args.half_life, args.half_life_unit, args.half_life_unit)
    if args.isotope:
        preset_unit, preset_hl = PRESETS[args.isotope]
        out_unit = args.half_life_unit or preset_unit
        return _lambda_in_unit_from_half_life(preset_hl, preset_unit, out_unit)
    raise SystemExit("Provide --lambda OR --half-life (+ unit) OR --isotope")


def _run(cmd: list[str]) -> None:
    print("[cmd]", " ".join(cmd))
    subprocess.check_call(cmd)


def main() -> None:
    p = argparse.ArgumentParser(description="Run radioactive-decay simulations and plots")
    sub = p.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("simulate", help="Run a simulation")
    ps.add_argument("--mode", choices=["deterministic", "mc", "gillespie", "chain"], default="mc")
    ps.add_argument("--isotope", choices=sorted(PRESETS.keys()))
    ps.add_argument("--half-life", type=float, dest="half_life")
    ps.add_argument("--half-life-unit", choices=list(UNIT_SEC.keys()), default="h")
    ps.add_argument("--lambda", type=float, dest="lambda_")
    ps.add_argument("--n0", type=int, default=10000)
    ps.add_argument("--tmax", type=float, default=10.0)
    ps.add_argument("--dt", type=float, default=0.05)
    ps.add_argument("--seed", type=int)
    ps.add_argument("--plot", action="store_true")

    pp = sub.add_parser("plot", help="Plot a saved run")
    pp.add_argument("--run-dir", default="data/runs/last")

    args = p.parse_args()

    if args.cmd == "simulate":
        lam = _resolve_lambda(args)
        cmd = [
            sys.executable, "-m", "src.simulate",
            "--mode", args.mode,
            "--n0", str(args.n0),
            "--lambda", str(lam),
            "--tmax", str(args.tmax),
            "--dt", str(args.dt),
        ]
        if args.seed is not None:
            cmd += ["--seed", str(args.seed)]
        _run(cmd)
        if args.plot:
            _run([sys.executable, "-m", "src.plotting", "--run-dir", "data/runs/last"])
        return

    if args.cmd == "plot":
        _run([sys.executable, "-m", "src.plotting", "--run-dir", args.run_dir])
        return


if __name__ == "__main__":
    main()



