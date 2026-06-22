#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'EOF'
Usage:
  pipeline.sh --fasta <file_or_dir> [options]

Options:
  --fasta PATH              A FASTA file or a directory containing .fa/.fasta files.
  --esm-lrr-python PATH     Python executable for the ESM-LRR step.
  --esm-lrr-env ENV         Conda environment name/path for ESM-LRR if --esm-lrr-python is not set.
  --pfam-env ENV            Conda environment name/path for Pfam/ProSite steps. Default: pfam_scan
  --signalp-env ENV         Conda environment name/path for SignalP step. Default: signalp
  -h, --help                Show this help.
EOF
}

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
work_path="$(cd "${script_dir}/.." && pwd)"

fasta=""
esm_lrr_python=""
esm_lrr_env="esm-lrr"
pfam_env="pfam_scan"
signalp_env="signalp"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --fasta)
            fasta="${2:-}"
            shift 2
            ;;
        --esm-lrr-python)
            esm_lrr_python="${2:-}"
            shift 2
            ;;
        --esm-lrr-env)
            esm_lrr_env="${2:-}"
            shift 2
            ;;
        --pfam-env)
            pfam_env="${2:-}"
            shift 2
            ;;
        --signalp-env)
            signalp_env="${2:-}"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "[!] Error: unknown argument: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

if [[ -z "$fasta" ]]; then
    echo "[!] Error: --fasta is required" >&2
    usage >&2
    exit 2
fi

if [[ ! -f "${work_path}/models/esm1v_t33_650M_UR90S_1.pt" || ! -f "${work_path}/models/esm_lrr.pickle" ]]; then
    echo "[!] Error: required model files are missing:" >&2
    [[ -f "${work_path}/models/esm1v_t33_650M_UR90S_1.pt" ]] || echo "    - ${work_path}/models/esm1v_t33_650M_UR90S_1.pt" >&2
    [[ -f "${work_path}/models/esm_lrr.pickle" ]] || echo "    - ${work_path}/models/esm_lrr.pickle" >&2
    exit 1
fi

load_conda() {
    if declare -F conda >/dev/null 2>&1; then
        return
    fi

    local conda_base=""
    if command -v conda >/dev/null 2>&1; then
        conda_base="$(conda info --base)"
    elif [[ -n "${CONDA_EXE:-}" ]]; then
        conda_base="$(dirname "$(dirname "$CONDA_EXE")")"
    fi

    if [[ -z "$conda_base" || ! -f "${conda_base}/etc/profile.d/conda.sh" ]]; then
        echo "[!] Error: cannot locate conda.sh. Activate conda first, then rerun this script." >&2
        exit 1
    fi

    # shellcheck disable=SC1090
    source "${conda_base}/etc/profile.d/conda.sh"
}

run_in_conda() {
    local env_ref="$1"
    shift

    load_conda
    conda activate "$env_ref"
    "$@"
    conda deactivate
}

run_esm_lrr() {
    local protein_path="$1"
    if [[ -n "$esm_lrr_python" ]]; then
        "$esm_lrr_python" "${script_dir}/esm-lrr.py" --fasta "$protein_path" --dir "$work_path"
    else
        run_in_conda "$esm_lrr_env" python "${script_dir}/esm-lrr.py" --fasta "$protein_path" --dir "$work_path"
    fi
}

collect_fastas() {
    local input_path="$1"
    if [[ -d "$input_path" ]]; then
        find "$input_path" -maxdepth 1 -type f \( -iname "*.fa" -o -iname "*.fasta" \) | sort
    elif [[ -f "$input_path" ]]; then
        printf '%s\n' "$input_path"
    else
        echo "[!] Error: path ${input_path} does not exist" >&2
        exit 1
    fi
}

mapfile -t protein_paths < <(collect_fastas "$fasta")
if [[ "${#protein_paths[@]}" -eq 0 ]]; then
    echo "[!] Error: no valid FASTA files were found" >&2
    exit 1
fi

echo "[*] work_path: ${work_path}"
echo "[*] Preparing to process ${#protein_paths[@]} protein files"

for protein_path in "${protein_paths[@]}"; do
    file_name="$(basename "$protein_path")"
    printf '\n==================================================\n'
    echo "fasta file: ${file_name}"
    printf '==================================================\n'

    run_in_conda "$pfam_env" python "${script_dir}/pfam_pk_nb.py" --fasta "$protein_path" --dir "$work_path"
    run_in_conda "$signalp_env" python "${script_dir}/signal_rlk_rlp.py" --fasta "$protein_path" --dir "$work_path"
    run_esm_lrr "$protein_path"
    run_in_conda "$pfam_env" python "${script_dir}/pfam_lysm.py" --fasta "$protein_path" --dir "$work_path"
    run_in_conda "$pfam_env" python "${script_dir}/pfam_tir_rpw8.py" --fasta "$protein_path" --dir "$work_path"
done
