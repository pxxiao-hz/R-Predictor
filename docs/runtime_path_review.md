# Runtime path review

This repository was reviewed for path-related runtime failures before running on the local server.

## Local server paths

- Scripts: `/home/pxxiao/tools/R-Predictor/R-Predictor/scripts`
- TMHMM: `/home/pxxiao/tools/tmhmm/tmhmm-2.0c/bin/tmhmm`
- Paircoil2: `/home/pxxiao/tools/paircoil2/paircoil2/paircoil2`

## Issues found and fixed

- The README used `python pipeline.py`, but the entrypoint is `scripts/pipeline.py`.
- `scripts/pipeline.py` called child scripts by bare relative filenames, so it only worked from the `scripts/` directory.
- `scripts/pipeline.py` now checks required ESM model files before running the pipeline, so missing models fail fast.
- `scripts/esm-lrr.py` now checks for `scikit-learn==1.2.2` before running ESM embedding, because newer scikit-learn versions cannot load `esm_lrr.pickle`. It also reports NumPy/scikit-learn binary incompatibility clearly.
- `scripts/extract.py` now handles PyTorch >= 2.6 legacy ESM checkpoint loading by setting `weights_only=False` for trusted local model files.
- `scripts/pfam_pk_nb.py` and `scripts/signal_rlk_rlp.py` used the author's absolute TMHMM path.
- `scripts/Topaircoil2.py` used the author's absolute Paircoil2 path.
- `scripts/Topaircoil2.py` referenced an undefined variable, `nb_nolrr_notir_norpw8_nocc`, when writing the non-coiled-coil N output.
- `scripts/esm-lrr.py` called `extract.py` by bare relative filename, so it depended on the current working directory.
- Python bytecode cache files are now ignored by Git.

## Remaining recommended cleanup

- Place `models/esm1v_t33_650M_UR90S_1.pt` and `models/esm_lrr.pickle` under the repository `models/` directory before running.
- Recreate or fix the `esm-lrr` environment with `python=3.11`, `numpy=1.24.4`, `scipy=1.10.1`, and `scikit-learn=1.2.2` if pickle loading or binary compatibility fails.
- Keep ESM checkpoint files from trusted sources only, because legacy checkpoint loading uses pickle-compatible behavior.
- Replace shell command string concatenation with `subprocess.run([...], check=True)` throughout the modules.
- Replace repeated `args.fasta.split(".")[0].split("/")[-1]` path parsing with `pathlib.Path(args.fasta).stem`.
- Make TMHMM and Paircoil2 paths command-line arguments or config values instead of hard-coded server paths.
- Add preflight checks for external tools, model files, HMM files, and expected intermediate files.
