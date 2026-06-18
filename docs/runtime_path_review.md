# Runtime path review

This repository was reviewed for path-related runtime failures before running on the local server.

## Local server paths

- Scripts: `/home/pxxiao/tools/R-Predictor/R-Predictor/scripts`
- TMHMM: `/home/pxxiao/tools/tmhmm/tmhmm-2.0c/bin/tmhmm`
- Paircoil2: `/home/pxxiao/tools/paircoil2/paircoil2/paircoil2`

## Issues found and fixed

- The README used `python pipeline.py`, but the entrypoint is `scripts/pipeline.py`.
- `scripts/pipeline.py` called child scripts by bare relative filenames, so it only worked from the `scripts/` directory.
- `scripts/pfam_pk_nb.py` and `scripts/signal_rlk_rlp.py` used the author's absolute TMHMM path.
- `scripts/Topaircoil2.py` used the author's absolute Paircoil2 path.
- `scripts/Topaircoil2.py` referenced an undefined variable, `nb_nolrr_notir_norpw8_nocc`, when writing the non-coiled-coil N output.
- `scripts/esm-lrr.py` called `extract.py` by bare relative filename, so it depended on the current working directory.
- Python bytecode cache files are now ignored by Git.

## Remaining recommended cleanup

- Replace shell command string concatenation with `subprocess.run([...], check=True)` throughout the modules.
- Replace repeated `args.fasta.split(".")[0].split("/")[-1]` path parsing with `pathlib.Path(args.fasta).stem`.
- Make TMHMM and Paircoil2 paths command-line arguments or config values instead of hard-coded server paths.
- Add preflight checks for external tools, model files, HMM files, and expected intermediate files.
