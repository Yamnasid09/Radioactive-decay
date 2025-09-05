#!/usr/bin/env bash
set -e

# usage: ./run.sh [mode] [isotope] [unit] [N0] [tmax] [dt] [seed]
# defaults: mc f18 min 100000 240 1 42

mode=${1:-mc}
iso=${2:-f18}
unit=${3:-min}
n0=${4:-100000}
tmax=${5:-240}
dt=${6:-1}
seed=${7:-42}

python -m src.cli simulate --mode "$mode" --isotope "$iso" --half-life-unit "$unit" \
  --n0 "$n0" --tmax "$tmax" --dt "$dt" --seed "$seed" --plot

python -m src.cli analyze --run-dir data/runs/last --out images

echo "✔ Done → data/runs/last (data), images/ (plots)"
