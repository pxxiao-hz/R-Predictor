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

def main():

    parser = argparse.ArgumentParser(description="R-Predictor Pipeline")
    parser.add_argument("--fasta", required=True, help="A single protein file or a directory containing multiple protein files")
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

    print(f"[*] Preparing to process {len(protein_paths)} protein files")

    for protein_path in protein_paths:
        file_name = os.path.basename(protein_path)
        print(f"\n" + "="*50)
        print(f"fasta file: {file_name}")
        print("="*50)

        steps = [
            ("pfam_scan", "pfam_pk_nb.py"),
            ("signalp", "signal_rlk_rlp.py"),
            ("esm-lrr", "esm-lrr.py"),
            ("pfam_scan", "pfam_lysm.py"),
            ("pfam_scan", "pfam_tir_rpw8.py"),
        ]
        for env_name, script_name in steps:
            script_path = os.path.join(script_dir, script_name)
            subprocess.run(
                [
                    "conda",
                    "run",
                    "-n",
                    env_name,
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
