#!/usr/bin/env python
import os
import sys
import random
import math
import copy

class rd_generator:
    def __init__(self, seed):
        self.rand_nr = random.Random()
        self.rand_nr.seed(seed)

def map2string(m):
    outs = ""
    for key in m:
        v = m[key]
        #print(key)
        #print(v)
        vv = ""
        for vi in v:
            vv = vv + vi + ";"
        vv = vv[0:-1]
        outs = outs + key + "	" + vv + "\n"
    return outs

def rank2string(l):
    s = ""
    for e in l:
        s = s + e + ";"
    s = s[0:-1]
    return s
 
class rd_mislable:
    def __init__(self, tax_input, seed, num_mis = 100):
        self.num_mis = num_mis
        self.prob = [0.05, 0.05, 0.1, 0.3, 0.5] #p, c, o, f ,g 
        self.num = [int(x*100) for x in self.prob]
        self.tax = {}
        self.names = []
        with open(tax_input) as fin:
            for line in fin:
                ll = line.strip().split("	")
                taxonomy = ll[1].split("; ")
                self.tax[ll[0]] = taxonomy
                self.names.append(ll[0])
        self.rd = rd_generator(seed = seed)
        self.truetax = {}
        self.mistax = {}
        self.remaintax = {}
        self.testingtax = {}
        
    def find_all_taxs(self, rank_idx, rank_name_exclude):
        rks = []
        for key in self.tax:
            rank = self.tax[key]
            if rank[rank_idx] != rank_name_exclude:
                rks.append(rank)
        return rks
    
    def mis_lable(self, names, rank_idx):
        for name in names:
            remain_ranks = self.find_all_taxs(rank_idx, name)
            idx = self.rd.rand_nr.randint(0, len(remain_ranks))
            
            tk1 = self.tax[name]
            
            tk2 = copy.copy(tk1)
            
            tk2.append(str(rank_idx))
            self.truetax[name] = tk2
            self.mistax[name] = remain_ranks[idx]
    
    def simulate(self, fout):
        idx = range(len(self.names))
        self.rd.rand_nr.shuffle(idx)
        names1 = []
        names2 = []
        names3 = []
        names4 = []
        names5 = []
        names_unchanged = []
        names_rest = []
        cnt = 0 
        for i in range(self.num[0]):
            names1.append(self.names[idx[cnt]])
            cnt = cnt + 1
        
        for i in range(self.num[1]):
            names2.append(self.names[idx[cnt]])
            cnt = cnt + 1        

        for i in range(self.num[2]):
            names3.append(self.names[idx[cnt]])
            cnt = cnt + 1
        
        for i in range(self.num[3]):
            names4.append(self.names[idx[cnt]])
            cnt = cnt + 1

        for i in range(self.num[4]):
            names5.append(self.names[idx[cnt]])
            cnt = cnt + 1
            
        for i in range(self.num_mis):
            names_unchanged.append(self.names[idx[cnt]])
            cnt = cnt + 1
        
        while cnt < len(self.names):
            names_rest.append(self.names[idx[cnt]])
            cnt = cnt + 1

        self.mis_lable(names1, rank_idx = 1)
        self.mis_lable(names2, rank_idx = 2)
        self.mis_lable(names3, rank_idx = 3)
        self.mis_lable(names4, rank_idx = 4)
        self.mis_lable(names5, rank_idx = 5)
        
        for name in names_unchanged:
            self.testingtax[name] = self.tax[name]
        
        for name in names_rest:
            self.remaintax[name] = self.tax[name]
            
        print("1")
        s_mis = map2string(self.mistax)
        print("2")
        s_mis_true = map2string(self.truetax)
        print("3")
        s_testing = map2string(self.testingtax)
        print("4")
        s_remain = map2string(self.remaintax)
        
        with open(fout+".tax", "w") as fo:
            fo.write(s_mis + s_testing + s_remain)
        
        with open(fout+".testing.tax", "w") as fo:
            fo.write(s_mis + s_testing)
            
        with open(fout+".true.tax", "w") as fo:
            fo.write(s_mis_true + s_testing)
        

if __name__ == "__main__":
    rm = rd_mislable(tax_input = "/home/zhangje/GIT/tax_benchmark/simulation_LTP/LTP.tax", seed = "22222222222")
    rm.simulate(fout = "/home/zhangje/GIT/tax_benchmark/simulator/mLTP10")
