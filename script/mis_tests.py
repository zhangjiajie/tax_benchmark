#!/usr/bin/env python
import os
import sys
import random
import math
from subprocess import call
from ete2 import SeqGroup

def run(query, refseq, taxonomy, method, outdir):
    #assign_taxonomy.py -i repr_set_seqs.fasta -r ref_seq_set.fna -t id_to_taxonomy.txt -m blast/rdp
    #print(["assign_taxonomy.py", "-i", query, "-r", refseq, "-t", taxonomy, "-m", method, "-o", outdir])
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
    
    
def autotest(refseq, reftax, testingtax, tf = "/home/zhangje/GIT/tax_benchmark/script/tmp/"):
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
        result_uclust = findmis(refseq = seqs, reftax = ranks, name = test[0], method = "uclust", temfolder = tf)
        result_rdp = findmis(refseq = seqs, reftax = ranks, name = test[0], method = "rdp", temfolder = tf)
        result_blast = findmis(refseq = seqs, reftax = ranks, name = test[0], method = "blast", temfolder = tf)
        truth = test[1]
        if len(truth) == 8:
            rank_nr = int(truth[7])
            if len(result_uclust) > rank_nr and result_uclust[rank_nr] == truth[rank_nr]:
                num_corrected_uclust = num_corrected_uclust + 1
            if len(result_rdp) > rank_nr and result_rdp[rank_nr] == truth[rank_nr]:
                num_corrected_rdp = num_corrected_rdp + 1
            if len(result_blast) > rank_nr and result_blast[rank_nr] == truth[rank_nr]:
                num_corrected_blast = num_corrected_blast + 1
        else:
            if result_uclust == truth:
                num_unchanged_uclust = num_unchanged_uclust + 1
            if result_rdp == truth:
                num_unchanged_rdp = num_unchanged_rdp + 1
            if result_uclust == truth:
                num_unchanged_blast = num_unchanged_blast + 1
        print("truth:" + repr(truth))
        print("uclust:" + repr(result_uclust))
        print("rdp:"+ repr(result_rdp))
        print("blast:" +repr(result_blast))
        
    print("method   corrected   unchanged")
    print("uclust"+ "   " +num_corrected_uclust + " " + num_unchanged_uclust)
    print("rdp"+ "   " +num_corrected_rdp + " " + num_unchanged_rdp)
    print("blast"+ "   " +num_corrected_blast + " " + num_unchanged_blast)
    
    with open(testingtax+".results", "w") as fo:
        fo.write("method   corrected   unchanged \n")
        fo.write("uclust"+ "   " +num_corrected_uclust + " " + num_unchanged_uclust + "\n")
        fo.write("rdp"+ "   " +num_corrected_rdp + " " + num_unchanged_rdp + "\n")
        fo.write("blast"+ "   " +num_corrected_blast + " " + num_unchanged_blast + "\n")
     
if __name__ == "__main__":
    if len(sys.argv) < 3: 
        print("python mis_test.py /home/zhangje/GIT/tax_benchmark/simulation_LTP/sim.fasta /home/zhangje/GIT/tax_benchmark/simulation_LTP/mislable/5/mLTP1.tax /home/zhangje/GIT/tax_benchmark/simulation_LTP/mislable/5/mLTP1.true.tax  /home/zhangje/GIT/tax_benchmark/script/tmp/")
        sys.exit()
    
    autotest(refseq = sys.argv[1], 
    reftax = sys.argv[2], 
    testingtax = sys.argv[3],
    tf = sys.argv[4])
    
    
    
    
