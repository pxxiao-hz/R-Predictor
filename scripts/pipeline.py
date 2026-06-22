# -*- coding: utf-8 -*-
"""
@Time ： 2024/3/7 14:33
@Auth ： zhenyaliu
@File ：pipeline.py
@IDE ：PyCharm
@Mail：zhenyaliu77@gmail.com

"""
import argparse
import os
import subprocess


def check_required_files(work_path):
    required_files = [
        os.path.join(work_path, "models", "esm1v_t33_650M_UR90S_1.pt"),
        os.path.join(work_path, "models", "esm_lrr.pickle"),
    ]
    missing_files = [path for path in required_files if not os.path.isfile(path)]
    if missing_files:
        print("[!] Error: required model files are missing:")
        for path in missing_files:
            print(f"    - {path}")
        print("[!] Download the ESM-1v and ESM-LRR model files and place them in the models directory.")
        raise SystemExit(1)


def conda_env_args(env_ref):
    if os.path.sep in env_ref or env_ref.startswith("."):
        return ["-p", env_ref]
    return ["-n", env_ref]


def main():

    parser = argparse.ArgumentParser(description="R-Predictor Pipeline")
    parser.add_argument("--fasta", required=True, help="A single protein file or a directory containing multiple protein files")
    parser.add_argument(
        "--esm-lrr-env",
        default="esm-lrr",
        help="Conda environment name or absolute path for the ESM-LRR step",
    )
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    work_path = os.path.dirname(script_dir)

    print(f"[*] work_path: {work_path}")

    input_path = os.path.abspath(args.fasta)
    protein_paths = []

    if os.path.isdir(input_path):
        for f in os.listdir(input_path):
            full_path = os.path.join(input_path, f)
            if os.path.isfile(full_path):
                if f.lower().endswith(('.fasta', '.fa')):
                    protein_paths.append(full_path)

    elif os.path.isfile(input_path):
        protein_paths.append(input_path)
    else:
        print(f"[!] Error: path {input_path} does not exist")
        return

    if not protein_paths:
        print("[!] Error: no valid files were found at the specified path")
        return

    check_required_files(work_path)

    print(f"[*] Preparing to process {len(protein_paths)} protein files")

    for protein_path in protein_paths:
        file_name = os.path.basename(protein_path)
        print(f"\n" + "="*50)
        print(f"fasta file: {file_name}")
        print("="*50)

        steps = [
            ("pfam_scan", "pfam_pk_nb.py"),
            ("signalp", "signal_rlk_rlp.py"),
            (args.esm_lrr_env, "esm-lrr.py"),
            ("pfam_scan", "pfam_lysm.py"),
            ("pfam_scan", "pfam_tir_rpw8.py"),
        ]
        for env_ref, script_name in steps:
            script_path = os.path.join(script_dir, script_name)
            subprocess.run(
                [
                    "conda",
                    "run",
                    *conda_env_args(env_ref),
                    "python",
                    script_path,
                    "--fasta",
                    protein_path,
                    "--dir",
                    work_path,
                ],
                check=True,
            )


if __name__ == "__main__":
    main()
