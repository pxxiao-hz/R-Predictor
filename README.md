# R-Predictor

This fork is based on [zhouyflab/R-Predictor](https://github.com/zhouyflab/R-Predictor) and includes local runtime-path and entrypoint fixes for the `/home/pxxiao/tools/R-Predictor/R-Predictor` server deployment.

## Table of Contents
- [Introduction](#Introduction)
- [Installation](#Installation)
  - [Manual installation](#Manualintallation)
  - [Installation details](#Installationdetails)
- [R-Predictor usage](#R-Predictorusage)
- [Inputs](#Inputs)
- [Outputs](#Outputs)
- [Citations](#Citations)
- [Acknowledgements](#Acknowledgements)
## Introduction
This pipeline is designed to automatically annotate 15 distinct domain topologies of disease resistance genes across the entire plant genome.

R-Predictor, designed for the de novo annotation of various R genes integrate four modules for data pre-processing and the identification of different types of proteins. Each module incorporates customized filtering scripts and the best-performing methods identified through benchmarking.

![示例图片](images/pipeline.png)
## Installation
### Manual installation
Manually installing R-Predictor can be cumbersome, but fortunately, these tools it depends on are easy to work with.
- [Pfam36.0](https://ftp.ebi.ac.uk/pub/databases/Pfam/releases/Pfam36.0/) and [PfamA](https://drive.google.com/file/d/17I80EbwOz-JWJAJ1n-8mdJC47jjCe8Yz/view?usp=drive_link)
~~~
conda create -n pfam_scan
conda activate pfam_scan
conda install -c bioconda pfam_scan hmmer hmmer2 -y
pip3 install Bio

Download the PfamA database and move it to the `hmm` directory.
Pfam36.0 for all databases and PfamA for PfamA database.
~~~
- [SignalP 6.0](https://github.com/fteufel/signalp-6.0/blob/main/installation_instructions.md)
~~~
conda create -n signalp
conda activate signalp
conda install -c predector signalp6
signalp6-register signalp-6.0h.fast.tar.gz
~~~
- [TMHMM-2.0](https://services.healthtech.dtu.dk/cgi-bin/sw_request?software=tmhmm&version=2.0c&packageversion=2.0c&platform=Linux)
~~~
The installation details are as follows:
1.Click the hyperlink to download the installation package.
2.Modify the first line of the `tmhmm` in the bin folder to use your own perl path, which can be found by running `which perl`. On line 33, change $opt_basedir=the absolute path of tmhmm-2.0c.
3.Modify the first line of the `tmhmmformat.pl` to use your own perl path.
~~~
- [ESM-1v](https://github.com/facebookresearch/esm/blob/main/README.md) and [model](https://dl.fbaipublicfiles.com/fair-esm/models/esm1v_t33_650M_UR90S_1.pt)
~~~
Download the ESM-1v model and move it to the `models` directory.
ESM-1v for README.md and model for esm1v_t33_650M_UR90S_1.pt.
~~~
- [ESM-LRR](https://github.com/zhouyflab/R-Predictor/) and [model](https://drive.google.com/file/d/1k8Kl9me4ZQpuX9maEGWq4ALbxO3yhkEG/view?usp=sharing)
~~~
conda create -n esm-lrr python=3.11
conda activate esm-lrr
conda install -y \
    numpy=1.24.4 \
    scipy=1.10.1 \
    pytorch=2.7.1 \
    scikit-learn=1.2.2 \
    seaborn=0.13.2 \
    -c pytorch \
    -c conda-forge
conda install -y fair-esm--1.0.2
pip3 install tqdm

Download the ESM-LRR model and move it to the `models` directory.
ESM-LRR for README.md and model for esm_lrr.pickle.
~~~
- [ProSite](https://ftp.expasy.org/databases/prosite/ps_scan/README)
~~~
conda activate pfam_scan
conda install -c bioconda pftools
~~~
- [Paircoil2](https://cb.csail.mit.edu/paircoil2/)
~~~
Place the configuration file .paircoil2 in your home directory and the executable and data files (*.tb) in the directory you will run Paircoil2 in.
It is recommended to use the installation package with the i686 suffix in the tools folder.
~~~
### Installation details
~~~
pfam_scan==1.6
hmmer==3.4
hmmer2==2.3.2
Bio==1.8.1
signalp6==6.0+h
tmhmm==2.0c
pytorch==2.7.1
fair-esm==1.0.2
numpy==1.24.4
scipy==1.10.1
scikit-learn==1.2.2
seaborn==0.13.2
tqdm==4.67.3
pftools==3.2.12

Compatibility notes for this fork:
1. For PyTorch >= 2.6, `scripts/extract.py` already sets `weights_only=False` when loading trusted legacy ESM checkpoints.
2. The `esm-lrr` environment should use `python=3.11`, `numpy=1.24.4`, `scipy=1.10.1`, and `scikit-learn=1.2.2`.
3. Paircoil2 may require a valid `.paircoil2` configuration file in the run directory or home directory.
~~~
**If the above tools cannot be installed via conda or downloaded from the official website, please go to the [tools](tools/) folder.**

## R-Predictor usage
**If you have correctly installed the required dependencies and modified the corresponding paths, R-Predictor will work smoothly.**  
~~~
Make the following checks before running R-Predictor.
1.Unzip the model files of ESM-1v and ESM-LRR, and move them to `models` directory. 
2.Unzip the PfamA database and move it to `hmm` directory. 
3.The local server TMHMM path used by the scripts is `/home/pxxiao/tools/tmhmm/tmhmm-2.0c/bin/tmhmm`.
4.The local server Paircoil2 path used by the scripts is `/home/pxxiao/tools/paircoil2/paircoil2/paircoil2`.
5.The local server scripts directory is `/home/pxxiao/tools/R-Predictor/R-Predictor/scripts`.
6.Before running, confirm that `models/esm1v_t33_650M_UR90S_1.pt` and `models/esm_lrr.pickle` exist.
7.The `esm-lrr` conda environment must use compatible NumPy/scikit-learn versions: `numpy=1.24.4`, `scipy=1.10.1`, and `scikit-learn=1.2.2`.
~~~
~~~
#Run R-Predictor for a single protein file.
python scripts/pipeline.py --fasta <file>

#Run R-Predictor for all proteins files in a folder.
python scripts/pipeline.py --fasta <dir>
~~~

## Input
R-Predictor supports single or multiple protein sequences, which should be in FASTA format.
~~~
>Q9XGM3
METSSISTVEDKPPQHQVFINFRGADLRRRFVSHLVTALKLNNINVFIDDYEDRGQPLDV
LLKRIEESKIVLAIFSGNYTESVWCVRELEKIKDCTDEGTLVAIPIFYKLEPSTVRDLKG
KFGDRFRSMAKGDERKKKWKEAFNLIPNIMGIIIDKKSVESEKVNEIVKAVKTALTGIPP
EGSHNAVVGALGNSNAGTSSGDKKHETFGNEQRLKDLEEKLDRDKYKGTRIIGVVGMPGI
GKTTLLKELYKTWQGKFSRHALIDQIRVKSKHLELDRLPQMLLGELSKLNHPHVDNLKDP
YSQLHERKVLVVLDDVSKREQIDALREILDWIKEGKEGSRVVIATSDMSLTNGLVDDTYM
~~~
**Ensure that the > lines in the FASTA file consist only of > followed by a unique ID for each protein, such as >Q9XGM3.**
## Output
R-Predictor will return 15 protein sequence files, each corresponding to a plant disease-resistance protein with a different domain topology.
~~~
/outcome
  xx_lrr_rlk.fasta
  xx_lysm_rlk.fasta
  xx_s_tm_pk.fasta
  xx_pk.fasta
  xx_lrr_rlp.fasta
  xx_lysm_rlp.fasta
  xx_s_lysm.fasta
  xx.cnl.fasta
  xx.cn.fasta
  xx.tnl.fasta
  xx.tn.fasta
  xx.rnl.fasta
  xx.rn.fasta
  xx.nl.fasta
  xx.n.fasta
~~~
## Citations
Zhenya Liu, Xu Wang, Shuo Cao, Tingyue Lei, Zhuyifu Chen, Mengyan Zhang, Zhongqi Liu, Jiacui Li, Jianzhong Lu, Wenqi Ma, Bingxiong Su, Yanling Peng, Yanshuai Xu, Xiaodong Xu, Wei Zhang, Cong Tan, Chengjie Chen, Yiwen Wang, Yongfeng Zhou, Machine learning empowers precise discovery of disease-resistance genes in plants, Plant Physiology, 2026;, kiag276, https://doi.org/10.1093/plphys/kiag276
## Acknowledgements
This program would like to thank Professor Zhou and Professor Wang for their guidance, and express gratitude to Xu Wang, Tingyue Lei and Zhongqi Liu for their contributions.
