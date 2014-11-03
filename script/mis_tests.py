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
    call(["assign_taxonomy.py", "-i", query, "-r", refseq, "-t", taxonomy, "-m", method, "-o", outdir, "--rdp_max_memory", "7500"])

def rank2string(l):
    s = ""
    for e in l:
        s = s + e + ";"
    s = s[0:-1]
    return s

def findmis(refseq, reftax, name, method, temfolder):
    fq = open(temfolder + "query.fa", "w")
    
    with open(temfolder + "seqs.fa", "w") as fo:
        for ele in refseq:
            if ele[0] != name:
                fo.write(">" + ele[0] + "\n")
                fo.write(ele[1] + "\n")
            else:
                fq.write(">" + ele[0] + "\n")
                fq.write(ele[1] + "\n")
    
    with open(temfolder + "ranks.tax", "w") as fo:
        for ele in reftax:
            if ele[0] != name:
                fo.write(ele[0] + "	" + rank2string(ele[1]) + "\n")
    
    fq.close()
    
    run(query = temfolder + "query.fa" , refseq = temfolder + "seqs.fa", taxonomy = temfolder + "ranks.tax", method = method, outdir = temfolder)
    results = temfolder + "query_tax_assignments.txt"
    
    resultss = ""
    with open(results) as fo:
        resultss = fo.readline()
    
    os.remove(temfolder + "query.fa")
    os.remove(temfolder + "seqs.fa")
    os.remove(temfolder + "ranks.tax")
    os.remove(temfolder + "query_tax_assignments.txt")
    
    return resultss.split()[1].split(";")
    
    
def autotest(refseq, reftax, testingtax):
    testings = []
    with open(testingtax) as fo:
        for line in fo:
            ll = line.split()
            ele = [ll[0], ll[1].split(";")]
            testings.append(ele)
    
    seqs = SeqGroup(refseq)
    ranks = []
    with open(reftax) as fo:
        for line in fo:
            ll = line.split()
            ele = [ll[0], ll[1].split(";")]
            ranks.append(ele)
    
    num_corrected_uclust = 0
    num_unchanged_uclust = 0
    
    num_corrected_rdp = 0
    num_unchanged_rdp = 0
    
    num_corrected_blast = 0
    num_unchanged_blast = 0
    
    for test in testings:
        result_uclust = findmis(refseq = seqs, reftax = ranks, name = test[0], method = "uclust", temfolder = "/home/zhangje/GIT/tax_benchmark/script/tmp/")
        result_rdp = findmis(refseq = seqs, reftax = ranks, name = test[0], method = "rdp", temfolder = "/home/zhangje/GIT/tax_benchmark/script/tmp/")
        result_blast = findmis(refseq = seqs, reftax = ranks, name = test[0], method = "blast", temfolder = "/home/zhangje/GIT/tax_benchmark/script/tmp/")
        truth = test[1]
        if len(truth) == 8:
            rank_nr = int(truth[7])
            if result_uclust[rank_nr] == truth[rank_nr]:
                num_corrected_uclust = num_corrected_uclust + 1
            if result_rdp[rank_nr] == truth[rank_nr]:
                num_corrected_rdp = num_corrected_rdp + 1
            if result_blast[rank_nr] == truth[rank_nr]:
                num_corrected_blast = num_corrected_blast + 1
        else:
            if result_uclust == truth:
                num_unchanged_uclust = num_unchanged_uclust + 1
            if result_rdp == truth:
                num_unchanged_rdp = num_unchanged_rdp + 1
            if result_uclust == truth:
                num_unchanged_blast = num_unchanged_blast + 1
        print("T:" + repr(truth))
        print(repr(result_uclust))
        print(repr(result_rdp))
        print(repr(result_blast))
        
    print("method   corrected   unchanged")
    print("uclust"+ "   " +num_corrected_uclust + " " + num_unchanged_uclust)
    print("rdp"+ "   " +num_corrected_rdp + " " + num_unchanged_rdp)
    print("blast"+ "   " +num_corrected_blast + " " + num_unchanged_blast)
     
    
    
if __name__ == "__main__":
    autotest(refseq = "/home/zhangje/GIT/tax_benchmark/simulation_LTP/sim.fasta", reftax = "/home/zhangje/GIT/tax_benchmark/simulation_LTP/mislable/mLTP1.tax", testingtax = "/home/zhangje/GIT/tax_benchmark/simulation_LTP/mislable/mLTP1.true.tax")
    
    
    
    
