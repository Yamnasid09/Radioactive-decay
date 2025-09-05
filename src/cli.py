# src/cli.py — clean indentation + analyze support

import argparse
import math
import subprocess
import sys

PRESETS = {
    # existing
    "tc99m": ("h", 6.01),
    "i131":  ("d", 8.02),
    "cs137": ("y", 30.05),
    "co60":  ("y", 5.27),

    # new nuclear medicine favorites
    "f18":   ("min", 109.77),  # 1.8295 h
    "c11":   ("min", 20.334),
    "n13":   ("min", 9.965),
    "o15":   ("min", 2.037),
    "i123":  ("h", 13.22),
    "tl201": ("h", 73.1),
    "y90":   ("h", 64.1),      # ~2.67 d
    "lu177": ("d", 6.65),
    "xe133": ("d", 5.25),
    "mo99":  ("h", 66.0),      # ~2.75 d
    "ba133": ("y", 10.52),
}


UNIT_SEC = {"s": 1, "min": 60, "h": 3600, "d": 86400, "y": 365.25 * 86400}


def _lambda_in_unit_from_half_life(half_life_value: float, half_life_unit: str, out_unit: str) -> float:
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
    p.add_argument("-V", "--version", action="version", version="radioactive-decay-sim 0.1.0")
    sub = p.add_subparsers(dest="cmd", required=True)

    # simulate
    ps = sub.add_parser("simulate", help="Run a simulation")
    ps.add_argument("--mode", choices=["deterministic", "mc"], default="mc")
    ps.add_argument("--isotope", choices=sorted(PRESETS.keys()))
    ps.add_argument("--half-life", type=float, dest="half_life")
    ps.add_argument("--half-life-unit", choices=list(UNIT_SEC.keys()), default="h")
    ps.add_argument("--lambda", type=float, dest="lambda_")
    ps.add_argument("--n0", type=int, default=10000)
    ps.add_argument("--tmax", type=float, default=10.0)
    ps.add_argument("--dt", type=float, default=0.05)
    ps.add_argument("--seed", type=int)
    ps.add_argument("--plot", action="store_true")

    # plot
    pp = sub.add_parser("plot", help="Plot a saved run")
    pp.add_argument("--run-dir", default="data/runs/last")
    pp.add_argument("--out", default="images")

    # bg (add Poisson background and plot)
    pb = sub.add_parser("bg", help="Add Poisson background to a saved run and plot")
    pb.add_argument("--run-dir", default="data/runs/last")
    pb.add_argument("--bg-rate", type=float, required=True)
    pb.add_argument("--seed", type=int, default=0)
    pb.add_argument("--out", default="images")


    # analyze
    pa = sub.add_parser("analyze", help="Estimate λ and half-life")
    pa.add_argument("--run-dir", default="data/runs/last")
    pa.add_argument("--out", default="images")

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
            _run([sys.executable, "-m", "src.plotting", "--run-dir", "data/runs/last", "--out", "images"])
        return

    if args.cmd == "plot":
        _run([sys.executable, "-m", "src.plotting", "--run-dir", args.run_dir, "--out", args.out])
        return

    if args.cmd == "analyze":
        _run([sys.executable, "-m", "src.analyze", "--run-dir", args.run_dir, "--out", args.out])
        return
        
    if args.cmd == "bg":
        _run([sys.executable, "src/plot_with_bg.py",
              "--run-dir", args.run_dir, "--bg-rate", str(args.bg_rate),
              "--seed", str(args.seed), "--out", args.out])
        return


if __name__ == "__main__":
    main()
