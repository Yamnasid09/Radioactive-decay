# Quickstart

## Install (editable)
    python -m pip install -r requirements.txt
    python -m pip install -e .

## Run a simple Monte-Carlo + plots
    raddecay simulate --mode mc --lambda 0.2 --n0 2000 --tmax 5 --dt 0.1 --seed 1 --plot

## Preset isotope (F-18, minutes) + analysis
    raddecay simulate --mode mc --isotope f18 --half-life-unit min --n0 100000 --tmax 240 --dt 1 --seed 42 --plot
    raddecay analyze --run-dir data/runs/last --out images

## Add Poisson background to latest run
    raddecay bg --run-dir data/runs/last --bg-rate 0.5 --seed 7 --out images
