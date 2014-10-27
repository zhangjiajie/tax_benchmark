#!/usr/bin/env python
import os
import sys
import random
import math
from subprocess import call
from ete2 import SeqGroup

def run(query, refseq, taxonomy, method, outdir):
    #assign_taxonomy.py -i repr_set_seqs.fasta -r ref_seq_set.fna -t id_to_taxonomy.txt -m blast/rdp
    print(["assign_taxonomy.py", "-i", query, "-r", refseq, "-t", taxonomy, "-m", method, "-o", outdir])
    call(["assign_taxonomy.py", "-i", query, "-r", refseq, "-t", taxonomy, "-m", method, "-o", outdir, "--rdp_max_memory", "7500"], shell=False)

def check(assignment, truth):
    call(["python", "/home/zhangje/GIT/epabenchmark/calc_stats.py", "-a", assignment, "-t", truth], shell=False)

def autotest(finfolder, method):
    for i in range(1,11):
        query = finfolder  + repr(i) + "testing.fa"
        refseq = finfolder  + repr(i) + "training.fa"
        taxonomy = finfolder  + repr(i) + "training.tax"
        outdir = finfolder  + repr(i) + method + "/"
        run(query, refseq, taxonomy, method, outdir)

def autocheck(finfolder, method):
    for i in range(1,11):
        #t1testing_tax_assignments.txt
        assignment = finfolder + "tt" + repr(i) + method + "/t" + repr(i) + "testing.fa.trim_tax_assignments.txt"
        truth = finfolder + "t" + repr(i) + "testing.tax"
        check(assignment, truth)

def ngssize(fin, start = 0, end = 2428):
    fout1 = open(fin+".trim.afa", "w")
    fout2 = open(fin+".trim.fa", "w")
    seqs = SeqGroup(fin)
    for seq in seqs:
        name = seq[0]
        sequence = seq[1]
        cut = len(sequence)/2
        sequence_trim = sequence[0:cut]
        sequence_trim_nogap = sequence_trim.replace("-","")
        fout1.write(">" + name + "\n")
        fout2.write(">" + name + "\n")
        fout1.write(sequence_trim + "\n")
        fout2.write(sequence_trim_nogap + "\n")
    
    fout1.close()
    fout2.close()
    return fin+".trim.fa"
    

"""
;Level	TP	FP	FP2	TN	FN	PRE	PRE2	REC	F1
Kingdom	509	0	0	0	0	1.000	1.000	1.000	1.000
Phylum	448	3	1	7	50	0.993	0.991	0.900	0.944
Class	384	3	2	48	72	0.992	0.987	0.842	0.911
Order	280	5	4	132	88	0.982	0.969	0.761	0.858
Family	122	4	12	283	88	0.968	0.884	0.581	0.726
Genus	31	3	7	415	53	0.912	0.756	0.369	0.525
Species	2	0	2	492	13	1.000	0.500	0.133	0.235

"""

def autosum(finfolder, method):
    titleline = ""
    rank = ["", 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0]
    allrank = []
    allrank.append(["", 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0])
    allrank.append(["", 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0])
    allrank.append(["", 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0])
    allrank.append(["", 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0])
    allrank.append(["", 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0])
    allrank.append(["", 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0])
    allrank.append(["", 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0.0])
    #print allrank
    for i in range(1,11):
        fsum = finfolder + "t" + repr(i) + method + "/t" + repr(i) + "testing_tax_assignments.txt.stats"
        with open(fsum) as fo:
            lines = fo.readlines()
            titleline = lines[0]
            for j in range(len(lines))[1:]:
                ss = lines[j].strip().split()
                #print("input line: " + lines[j])
                allrank[j-1][0] = ss[0]
                #print(allrank)
                for k in range(9):
                    num = float(ss[k+1])
                    allrank[j-1][k+1] = allrank[j-1][k+1] + num
                #print(allrank)
    #print(allrank)
    fout = open(finfolder + method + ".stas", "w")
    fout.write(titleline)
    for rk in allrank:
        fout.write(rk[0] + "\t")
        fout.write(str(int(rk[1])) + "\t")
        fout.write(str(int(rk[2])) + "\t")
        fout.write(str(int(rk[3])) + "\t")
        fout.write(str(int(rk[4])) + "\t")
        fout.write(str(int(rk[5])) + "\t")
        fout.write(str(rk[6]/10) + "\t")
        fout.write(str(rk[7]/10) + "\t")
        fout.write(str(rk[8]/10) + "\t")
        fout.write(str(rk[9]/10) + "\n")
    fout.close()


if __name__ == "__main__":
    
    #autotest(finfolder = "/panasas/zhangje/epac/tenfold/rdp/", method = "rdp")
    #autotest(finfolder = "/panasas/zhangje/epac/tenfold/gg85/", method = "blast")
    autotest(finfolder = "/home/zhangje/GIT/tax_benchmark/simulation_LTP/ten_fold/", method = "uclust")
    autotest(finfolder = "/home/zhangje/GIT/tax_benchmark/simulation_LTP/ten_fold/", method = "rdp")
    autotest(finfolder = "/home/zhangje/GIT/tax_benchmark/simulation_LTP/ten_fold/", method = "blast")
    #autocheck(finfolder = "/home/zhangje/GIT/tax_benchmark/simulation_LTP/ten_fold/", method = "uclust")
    #autocheck(finfolder = "/home/zhangje/GIT/tax_benchmark/simulation_LTP/ten_fold/", method = "rdp")
    #autocheck(finfolder = "/home/zhangje/GIT/tax_benchmark/simulation_LTP/ten_fold/", method = "blast")
    #autocheck(finfolder = "/panasas/zhangje/epac/tenfold/gg85/", method = "blast")
