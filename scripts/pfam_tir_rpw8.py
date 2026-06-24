# -*- coding: utf-8 -*-
"""
@Time ： 2024/3/11 9:21
@Auth ： zhenyaliu
@File ：pfam_tir_rpw8.py
@IDE ：PyCharm
@Mail：zhenyaliu77@gmail.com

"""
import subprocess
import argparse
import os
import re
import shutil


def parse_args():
    parser = argparse.ArgumentParser(description='Predicting TIR and RPW8 module of Rpredictor')
    parser.add_argument('--fasta', type=str, default='./data', help='path to the fasta file')
    parser.add_argument('--dir', type=str, default='./work', help='path to the work file')
    parser.add_argument(
        '--paircoil2',
        type=str,
        default='/home/pxxiao/tools/paircoil2/paircoil2/paircoil2',
        help='path to the Paircoil2 executable',
    )
    return parser.parse_args()

def is_file_empty(file_path):
    return os.stat(file_path).st_size == 0

def create_file_empty(file_path):
    with open(file_path,"w") as f:
        pass

def check_required_tools(paircoil2_executable):
    missing_tools = [tool for tool in ("pfam_scan.pl", "ps_scan.pl") if shutil.which(tool) is None]
    if missing_tools:
        print("[!] Error: required commands are missing from the current environment:")
        for tool in missing_tools:
            print(f"    - {tool}")
        print("[!] Install ProSite pftools into the pfam_scan environment, for example:")
        print("[!] conda install -n pfam_scan -c bioconda pftools -y")
        raise SystemExit(1)
    if not os.path.isfile(paircoil2_executable) or not os.access(paircoil2_executable, os.X_OK):
        print(f"[!] Error: Paircoil2 executable is missing or not executable: {paircoil2_executable}")
        raise SystemExit(1)

def process_pfam(path,first):
    if first == True:
        tir = {}
        rpw8 = {}
        with open(path,"r") as f:
            for i in f.readlines():
                i = i.strip()
                if i != "" and "#" not in i:
                    if re.search("CL0173",i) != None:
                        if "Family" in i:
                            target = re.findall(r"\d+\.?\d*", i.split("Family")[0])
                        else:
                            target = re.findall(r"\d+\.?\d*", i.split("Domain")[0])
                        tir[i.split(" ")[0]] = []
                        tir[i.split(" ")[0]].append(target[1]+"-"+target[2])
                        continue
                    else:
                        target = re.findall(r"\d+\.?\d*", i.split("Family")[0])
                        rpw8[i.split(" ")[0]] = []
                        rpw8[i.split(" ")[0]].append(target[1]+"-"+target[2])
                        continue
                else:
                    continue
        return tir,rpw8
    else:
        dic = {}
        with open(path,"r") as f:
            for i in f.readlines():
                i = i.strip()
                if i != "" and "#" not in i:
                    target = re.findall(r"\d+\.?\d*", i.split("Domain")[0])
                    dic[i.split(" ")[0]] = []
                    dic[i.split(" ")[0]].append(target[1]+"-"+target[2])
        return dic

def prosite(path):
    tir = {}
    rpw8 = {}
    with open(path, "r") as f:
        for i in f.readlines():
            i = i.strip()
            if i.split("\t")[3] == "PS50104":
                if i.split("\t")[0] not in tir.keys():
                    tir[i.split("\t")[0]] = []
                    tir[i.split("\t")[0]].append(i.split("\t")[1]+"-"+i.split("\t")[2])
                else:
                    tir[i.split("\t")[0]].append(i.split("\t")[1]+"-"+i.split("\t")[2])
            else:
                if i.split("\t")[0] not in rpw8.keys():
                    rpw8[i.split("\t")[0]] = []
                    rpw8[i.split("\t")[0]].append(i.split("\t")[1]+"-"+i.split("\t")[2])
                else:
                    rpw8[i.split("\t")[0]].append(i.split("\t")[1]+"-"+i.split("\t")[2])
    return tir,rpw8

def paircoil2(path):
    target = {}
    tmp = []
    with open(path, "r") as f:
        for i in f.readlines():
            i = i.strip()
            if "Sequence Code" in i:
                if tmp != []:
                    target[list(target.keys())[-1]].append(tmp[0] + "-" + tmp[-1])
                    tmp = []
                target[">"+i.split(": ")[1]] = []

            else:
                if "#" not in i:
                    cc = re.findall(r"\d+\.?\d*", i)
                    if float(cc[1]) <= 0.1:
                        tmp.append(cc[0])
                    else:
                        if tmp != [] and float(cc[1]) > 0.1:
                            target[list(target.keys())[-1]].append(tmp[0]+"-"+tmp[-1])
                            tmp = []
                else:
                    continue
        if tmp != []:
            target[list(target.keys())[-1]].append(tmp[0] + "-" + tmp[-1])
    target = {key: value for key, value in target.items() if target[key] != []}
    return target

def run_paircoil2(executable, input_path, output_path):
    input_path = os.path.abspath(input_path)
    output_path = os.path.abspath(output_path)

    if is_file_empty(input_path):
        create_file_empty(output_path)
        return {}

    executable = os.path.abspath(executable)
    install_dir = os.path.dirname(executable)
    try:
        subprocess.run(
            [executable, "-win", "21", input_path, output_path],
            cwd=install_dir,
            check=True,
        )
    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            "Paircoil2 failed. Verify that its .paircoil2 configuration file and "
            f"table files are available in {install_dir}. Command: "
            f"{' '.join(error.cmd)}"
        ) from error

    if not os.path.isfile(output_path):
        raise RuntimeError(f"Paircoil2 did not create the expected output file: {output_path}")
    return paircoil2(output_path)

def ProteinToDict(path):
    #Return a dictionary with id as key and sequence as value
    protein_seq = ''
    new_protein_seq = ''
    protein_id = ''
    protein_id_seq = {}
    fin_protein = open(path,'r')
    for i in fin_protein.readlines():
        i = i.strip('\n')
        if re.search('>',i) != None and protein_seq != '':
            for j in protein_seq:
                    new_protein_seq += j
            protein_id_seq[protein_id] = new_protein_seq
            new_protein_seq = ''
            protein_seq = ''
            protein_id = ''
        if re.search('>',i) != None:
            protein_id = i.split(" ")[0]
            continue
        protein_seq += i
    for j in protein_seq:
        new_protein_seq += j
        protein_id_seq[protein_id] = new_protein_seq
        fin_protein.close()
    return protein_id_seq

def generate_protein(protein,dic,outpath):
    with open(outpath,"w") as w:
        for key in dic.keys():
            for kkey in protein.keys():
                if re.search(key,kkey) != None:
                    w.write(kkey+"\n")
                    w.write(protein[kkey]+"\n")
                    break
                else:
                    continue

def generate_protein_nopknb(protein,dic,outpath):
    with open(outpath,"w") as w:
        for key in protein.keys():
            if key not in list(dic.keys()):
                w.write(key+"\n")
                w.write(protein[key]+"\n")
            else:
                continue

def writeprotein(protein,path):
    with open(path,"w") as f:
        for k in protein.keys():
            f.write(k+"\n")
            f.write(protein[k]+"\n")


def main(args):
    check_required_tools(args.paircoil2)
    work_dir = os.path.abspath(args.dir)
    new_dir = os.path.join(work_dir, "tmp")
    outcome_dir = os.path.join(work_dir, "outcome")
    prefix = os.path.splitext(os.path.basename(args.fasta))[0]
    #tnl rnl nl cnl
    if is_file_empty(new_dir+"/"+prefix+"_nb_lrr.fasta") != True:
        nb_lrr_tir_rpw8_path = "pfam_scan.pl -fasta "+new_dir+"/"+prefix+"_nb_lrr.fasta"+" -dir "+args.dir+"/hmm/Tir_Rpw8_HMM -outfile "+new_dir+"/"+prefix+"_nb_lrr_tir_rpw8.txt"
        subprocess.run(nb_lrr_tir_rpw8_path,shell=True,check=True)
        nb_lrr_tir_rpw8_path2 = "ps_scan.pl -o pff -d "+args.dir+"/hmm/tir_rpw8.dat "+new_dir+"/"+prefix+"_nb_lrr.fasta"+" > "+new_dir+"/"+prefix+"_nb_lrr_tir_rpw8_prosite.txt"
        subprocess.run(nb_lrr_tir_rpw8_path2,shell=True,check=True)
        protein_nb_lrr = ProteinToDict(new_dir+"/"+prefix+"_nb_lrr.fasta")
        nb_lrr_tir_pfam,nb_lrr_rpw8_pfam = process_pfam(new_dir+"/"+prefix+"_nb_lrr_tir_rpw8.txt",True)
        nb_lrr_tir_prosite,nb_lrr_rpw8_prosite = prosite(new_dir+"/"+prefix+"_nb_lrr_tir_rpw8_prosite.txt")
        nb_lrr_tir = {**nb_lrr_tir_pfam,**nb_lrr_tir_prosite}
        nb_lrr_rpw8 = {**nb_lrr_rpw8_pfam,**nb_lrr_rpw8_prosite}
        generate_protein(protein_nb_lrr,nb_lrr_tir,new_dir+"/"+prefix+"_nb_lrr_tir.fasta")
        generate_protein(protein_nb_lrr,nb_lrr_rpw8,new_dir+"/"+prefix+"_nb_lrr_rpw8.fasta")
        protein_nb_lrr_tir = ProteinToDict(new_dir+"/"+prefix+"_nb_lrr_tir.fasta")
        writeprotein(protein_nb_lrr_tir,args.dir+"/outcome/"+prefix+"_tnl.fasta")
        protein_nb_lrr_rpw8 = ProteinToDict(new_dir+"/"+prefix+"_nb_lrr_rpw8.fasta")
        writeprotein(protein_nb_lrr_rpw8,args.dir+"/outcome/"+prefix+"_rnl.fasta")
        tnl_rnl = {**protein_nb_lrr_tir,**protein_nb_lrr_rpw8}
        generate_protein_nopknb(protein_nb_lrr,tnl_rnl,new_dir+"/"+prefix+"_nb_lrr_notir_norpw8.fasta")
        protein_nb_lrr_notir_norpw8 = ProteinToDict(new_dir+"/"+prefix+"_nb_lrr_notir_norpw8.fasta")
        # here to run paircoil2
        cnl_input = os.path.join(new_dir, prefix + "_nb_lrr_notir_norpw8.fasta")
        cnl_output = os.path.join(new_dir, prefix + "_nb_lrr_notir_norpw8_cc.txt")
        nb_lrr_notir_norpw8_cc = run_paircoil2(args.paircoil2, cnl_input, cnl_output)
        cnl_fasta = os.path.join(new_dir, prefix + "_nb_lrr_notir_norpw8_cc.fasta")
        generate_protein(protein_nb_lrr_notir_norpw8, nb_lrr_notir_norpw8_cc, cnl_fasta)
        protein_nb_lrr_notir_norpw8_cc = ProteinToDict(cnl_fasta)
        writeprotein(protein_nb_lrr_notir_norpw8_cc, os.path.join(outcome_dir, prefix + "_cnl.fasta"))
        nl_fasta = os.path.join(new_dir, prefix + "_nb_lrr_notir_norpw8_nocc.fasta")
        generate_protein_nopknb(protein_nb_lrr_notir_norpw8, nb_lrr_notir_norpw8_cc, nl_fasta)
        protein_nb_lrr_notir_norpw8_nocc = ProteinToDict(nl_fasta)
        writeprotein(protein_nb_lrr_notir_norpw8_nocc, os.path.join(outcome_dir, prefix + "_nl.fasta"))
    else:
        create_file_empty(new_dir+"/"+prefix+"_nb_lrr_tir.fasta")
        create_file_empty(args.dir+"/outcome/"+prefix+"_tnl.fasta")
        create_file_empty(new_dir+"/"+prefix+"_nb_lrr_rpw8.fasta")
        create_file_empty(args.dir+"/outcome/"+prefix+"_rnl.fasta")
        create_file_empty(new_dir+"/"+prefix+"_nb_lrr_notir_norpw8.fasta")
        create_file_empty(args.dir+"/outcome/"+prefix+"_nl.fasta")
        create_file_empty(new_dir+"/"+prefix+"_nb_lrr_cc.fasta")
        create_file_empty(args.dir+"/outcome/"+prefix+"_cnl.fasta")

    #tn rn n cn
    if is_file_empty(new_dir+"/"+prefix+ "_nb_nolrr.fasta") != True:
        nb_nolrr_tir_rpw8_path = "pfam_scan.pl -fasta " + new_dir+"/"+prefix+ "_nb_nolrr.fasta" + " -dir "+args.dir+"/hmm/Tir_Rpw8_HMM -outfile " + new_dir+"/"+prefix + "_nb_nolrr_tir_rpw8.txt"
        subprocess.run(nb_nolrr_tir_rpw8_path, shell=True, check=True)
        nb_nolrr_tir_rpw8_path2 = "ps_scan.pl -o pff -d "+args.dir+"/hmm/tir_rpw8.dat "+new_dir+"/"+prefix+"_nb_nolrr.fasta"+" > "+new_dir+"/"+prefix+"_nb_nolrr_tir_rpw8_prosite.txt"
        subprocess.run(nb_nolrr_tir_rpw8_path2,shell=True,check=True)
        protein_nb_nolrr = ProteinToDict(new_dir+"/"+prefix + "_nb_nolrr.fasta")
        nb_nolrr_tir_pfam, nb_nolrr_rpw8_pfam = process_pfam(new_dir+"/"+prefix + "_nb_nolrr_tir_rpw8.txt", True)
        nb_nolrr_tir_prosite,nb_nolrr_rpw8_prosite = prosite(new_dir+"/"+prefix+"_nb_nolrr_tir_rpw8_prosite.txt")
        nb_nolrr_tir = {**nb_nolrr_tir_pfam,**nb_nolrr_tir_prosite}
        nb_nolrr_rpw8 = {**nb_nolrr_rpw8_pfam,**nb_nolrr_rpw8_prosite}
        generate_protein(protein_nb_nolrr, nb_nolrr_tir, new_dir+"/"+prefix + "_nb_nolrr_tir.fasta")
        generate_protein(protein_nb_nolrr, nb_nolrr_rpw8, new_dir+"/"+prefix + "_nb_nolrr_rpw8.fasta")
        protein_nb_nolrr_tir = ProteinToDict(new_dir+"/"+prefix + "_nb_nolrr_tir.fasta")
        writeprotein(protein_nb_nolrr_tir,args.dir+"/outcome/"+prefix+"_tn.fasta")
        protein_nb_nolrr_rpw8 = ProteinToDict(new_dir+"/"+prefix + "_nb_nolrr_rpw8.fasta")
        writeprotein(protein_nb_nolrr_rpw8,args.dir+"/outcome/"+prefix+"_rn.fasta")
        tn_rn = {**protein_nb_nolrr_tir, **protein_nb_nolrr_rpw8}
        generate_protein_nopknb(protein_nb_nolrr, tn_rn, new_dir+"/"+prefix + "_nb_nolrr_notir_norpw8.fasta")
        protein_nb_nolrr_notir_norpw8 = ProteinToDict(new_dir+"/"+prefix + "_nb_nolrr_notir_norpw8.fasta")
        # here to run paircoil2
        cn_input = os.path.join(new_dir, prefix + "_nb_nolrr_notir_norpw8.fasta")
        cn_output = os.path.join(new_dir, prefix + "_nb_nolrr_notir_norpw8_cc.txt")
        nb_nolrr_notir_norpw8_cc = run_paircoil2(args.paircoil2, cn_input, cn_output)
        cn_fasta = os.path.join(new_dir, prefix + "_nb_nolrr_notir_norpw8_cc.fasta")
        generate_protein(protein_nb_nolrr_notir_norpw8, nb_nolrr_notir_norpw8_cc, cn_fasta)
        protein_nb_nolrr_notir_norpw8_cc = ProteinToDict(cn_fasta)
        writeprotein(protein_nb_nolrr_notir_norpw8_cc, os.path.join(outcome_dir, prefix + "_cn.fasta"))
        n_fasta = os.path.join(new_dir, prefix + "_nb_nolrr_notir_norpw8_nocc.fasta")
        generate_protein_nopknb(protein_nb_nolrr_notir_norpw8, nb_nolrr_notir_norpw8_cc, n_fasta)
        protein_nb_nolrr_notir_norpw8_nocc = ProteinToDict(n_fasta)
        writeprotein(protein_nb_nolrr_notir_norpw8_nocc, os.path.join(outcome_dir, prefix + "_n.fasta"))
    else:
        create_file_empty(new_dir+"/"+prefix+"_nb_nolrr_tir.fasta")
        create_file_empty(args.dir+"/outcome/"+prefix+"_tn.fasta")
        create_file_empty(new_dir+"/"+prefix+"_nb_nolrr_rpw8.fasta")
        create_file_empty(args.dir+"/outcome/"+prefix+"_rn.fasta")
        create_file_empty(new_dir+"/"+prefix+"_nb_nolrr_cc.fasta")
        create_file_empty(args.dir+"/outcome/"+prefix+"_cn.fasta")
        create_file_empty(new_dir+"/"+prefix+"_nb_nolrr_notir_norpw8_nocc.fasta")
        create_file_empty(args.dir+"/outcome/"+prefix+"_n.fasta")




if __name__ == '__main__':
    args = parse_args()
    main(args)
