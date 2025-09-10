# CLI Reference

## simulate (single isotope)
    raddecay simulate --mode {deterministic,mc} [--isotope KEY | --half-life X --half-life-unit U | --lambda L]
                     --n0 N --tmax T --dt DT [--seed S] [--plot]

## plot
    raddecay plot --run-dir data/runs/last --out images

## analyze (λ & half-life fit)
    raddecay analyze --run-dir data/runs/last --out images
Outputs: images/log_fit.png, data/runs/last/fit.json

## bg (add background)
    raddecay bg --run-dir data/runs/last --bg-rate R --seed S --out images
Outputs: images/nt_curve_bg.png, images/log_nt_bg.png

## chain (A→B)
    raddecay chain --mode {deterministic,mc} --n0a N --lambda-a LA --lambda-b LB --tmax T --dt DT
                   [--realizations R] [--seed S] --out images
Outputs: images/chain_na_nb.png, images/chain_log.png
