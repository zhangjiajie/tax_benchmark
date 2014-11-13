#!/usr/bin/env python
import os
import sys
import random
import math
import time
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


def is_mislabel(orig_ranks, ranks):
    EMPTY_RANK = "-"   # change it if needed
    mislabel_lvl = -1
    min_len = min(len(orig_ranks),len(ranks))
    for rank_lvl in range(min_len):
        if ranks[rank_lvl] != EMPTY_RANK and ranks[rank_lvl] != orig_ranks[rank_lvl]:
            mislabel_lvl = rank_lvl
            break
    
    rk_name = ["Kingdom", "Phylum", "Class", "Order", "Family", "Genus", "Species"]
    
    
    if mislabel_lvl >= 0:
        #       flag  MislabeledLevel       OriginalLabel              ProposedLabel   
        return True, rk_name[mislabel_lvl], orig_ranks[mislabel_lvl], ranks[mislabel_lvl]
    else:
        return False, None, None, None

#;SeqID  MislabeledLevel OriginalLabel   ProposedLabel   Confidence      OriginalTaxonomyPath    ProposedTaxonomyPath    PerRankConfidence


def findmis(refseq, reftax, name, old_tax, method, foutput):
    """
    refseq: full list of sequences, unaligned
    reftax: full list of taxonomy
    name: taxa name you want to check for errors
    old_tax: taxonomy before the test, a list
    """
    basepath = os.path.dirname(os.path.abspath(__file__))
    tmpfolder = basepath + "/tmp/"
    tmpname = tmpfolder + str(time.time())
    
    #below generate tmp files
    fquery = tmpname + "query.fa"
    frefseq = tmpname + "seqs.fa"
    frefrank = tmpname + "ranks.tax"
    
    fq = open(fquery, "w")
    with open(frefseq, "w") as fo:
        for ele in refseq:
            if ele[0] != name:
                fo.write(">" + ele[0] + "\n")
                fo.write(ele[1] + "\n")
            else:
                fq.write(">" + ele[0] + "\n")
                fq.write(ele[1] + "\n")
    
    with open(frefrank, "w") as fo:
        for ele in reftax:
            if ele[0] != name:
                fo.write(ele[0] + "	" + rank2string(ele[1]) + "\n")
    fq.close()
    
    #below do the test
    run(query = fquery , refseq = frefseq, taxonomy = frefrank, method = method, outdir = tmpfolder)
    results = tmpfolder + "query_tax_assignments.txt"
    
    resultss = ""
    with open(results) as fo:
        resultss = fo.readline()
    
    os.remove(fquery)
    os.remove(frefseq)
    os.remove(frefrank)
    os.remove(tmpfolder + "query_tax_assignments.txt")
    
    flag, MislabeledLevel, OriginalLabel, ProposedLabel = is_mislabel(old_tax, resultss.split()[1].split(";"))
    
    if flag:
        #;SeqID  MislabeledLevel OriginalLabel   ProposedLabel   Confidence      OriginalTaxonomyPath    ProposedTaxonomyPath    PerRankConfidence
        with open(foutput, "a+") as fo:
            fo.write(name + "    " + MislabeledLevel + "    " + OriginalLabel + "    " + ProposedLabel  + "    " + "1    " +  rank2string(old_tax) + "    " + resultss.split()[1] + "    ;\n")
    
    return resultss, resultss.split()[1].split(";")
    
    
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
    
    f_uclust = open(testingtax+".uclust", "w")
    f_rdp = open(testingtax+".rdp", "w")
    f_blast = open(testingtax+".blast", "w")
    f_mis = open(testingtax+".misb", "w")
    f_umis = open(testingtax+".umisb", "w")
    
    for test in testings:
        ru, result_uclust = findmis(refseq = seqs, reftax = ranks, name = test[0], method = "uclust", temfolder = tf)
        f_uclust.write(ru)
        rr, result_rdp = findmis(refseq = seqs, reftax = ranks, name = test[0], method = "rdp", temfolder = tf)
        f_rdp.write(rr)
        rb, result_blast = findmis(refseq = seqs, reftax = ranks, name = test[0], method = "blast", temfolder = tf)
        f_blast.write(rb)
        truth = test[1]
        if len(truth) == 8:
            f_mis.write(test[0] + "	" + rank2string(truth[0:-1]) + "\n")
            rank_nr = int(truth[7])
            if len(result_uclust) > rank_nr and result_uclust[rank_nr] == truth[rank_nr]:
                num_corrected_uclust = num_corrected_uclust + 1
            if len(result_rdp) > rank_nr and result_rdp[rank_nr] == truth[rank_nr]:
                num_corrected_rdp = num_corrected_rdp + 1
            if len(result_blast) > rank_nr and result_blast[rank_nr] == truth[rank_nr]:
                num_corrected_blast = num_corrected_blast + 1
        else:
            f_umis.write(test[0] + "	" + rank2string(truth) + "\n")
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
    
    f_uclust.close()
    f_rdp.close()
    f_blast.close()
    f_mis.close()
    f_umis.close()
        
    print("method   corrected   unchanged")
    print("uclust"+ "   " +repr(num_corrected_uclust) + " " + repr(num_unchanged_uclust))
    print("rdp"+ "   " +repr(num_corrected_rdp) + " " + repr(num_unchanged_rdp))
    print("blast"+ "   " +repr(num_corrected_blast) + " " + repr(num_unchanged_blast))
    
    with open(testingtax+".results", "w") as fo:
        fo.write("method   corrected   unchanged \n")
        fo.write("uclust"+ "   " +repr(num_corrected_uclust) + " " + repr(num_unchanged_uclust) + "\n")
        fo.write("rdp"+ "   " +repr(num_corrected_rdp) + " " + repr(num_unchanged_rdp) + "\n")
        fo.write("blast"+ "   " +repr(num_corrected_blast) + " " + repr(num_unchanged_blast) + "\n")


def curator(refseq, reftax, method, output, testingtax = ""):
    seqs = SeqGroup(refseq)
    ranks = []
    with open(reftax) as fo:
        for line in fo:
            ll = line.split()
            ele = [ll[0], ll[1].split(";")]
            ranks.append(ele)
    testings = []
    if testingtax!="":
        with open(testingtax) as fo:
            for line in fo:
                ll = line.split()
                ele = [ll[0], ll[1].split(";")]
                testings.append(ele)
    else:
        testings = ranks
    
    for test in testings:
        #refseq, reftax, name, old_tax, method, foutput
        ru, result_string = findmis(refseq = seqs, reftax = ranks, name = test[0], method = method, foutput = output)
        print(result_string)
    


if __name__ == "__main__":
    if len(sys.argv) < 3: 
        print("""python mis_tests.py 
        /home/zhangje/GIT/tax_benchmark/simulation_LTP/sim.fasta 
        /home/zhangje/GIT/tax_benchmark/simulation_LTP/mislable/5/mLTP1.tax  
        uclust blast rdp
        /home/zhangje/GIT/tax_benchmark/simulation_LTP/mislable/5/mLTP1.tax.uclust.out
        """)
        
        print("seqs taxonomy method output [testtax]")
        
        sys.exit()
    
    if len(sys.argv) > 4:
        curator(refseq = sys.argv[1], reftax = sys.argv[2], method = sys.argv[3], output = sys.argv[4], testingtax = sys.argv[5])
    else:
        curator(refseq = sys.argv[1], reftax = sys.argv[2], method = sys.argv[3], output = sys.argv[4])
    
    #autotest(refseq = sys.argv[1], 
    #reftax = sys.argv[2], 
    #testingtax = sys.argv[3],
    #tf = sys.argv[4])
    
    
    
    
