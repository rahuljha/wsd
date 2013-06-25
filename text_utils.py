#!/usr/bin/python

import nltk
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from utils import flatten_list
from math import log
from nltk.stem.wordnet import WordNetLemmatizer

wordnet_tag ={'NN':'n','JJ':'a','VB':'v','RB':'r'}
lmtzr = WordNetLemmatizer()

def lemmatize(tokens):
    tagged = nltk.pos_tag(tokens)
    result = []

    for t in tagged:
     try:
          result.append(lmtzr.lemmatize(t[0],wordnet_tag[t[1][:2]]))
     except:
          result.append(lmtzr.lemmatize(t[0]))

    return result

def get_rel_lemmas(lemma_str):
    ret_lemmas = []
    syn = wn.lemma_from_key(lemma_str).synset
    ret_lemmas = [i.name.lower() for i in syn.lemmas]
    hyns = set(get_all_hypernyms(syn,3))
    for h in hyns:
        ret_lemmas += [i.name.lower() for i in h.lemmas]
        ret_lemmas += [i.lower() for i in lemmatize(nltk.word_tokenize(h.definition))]
    return ret_lemmas

def get_all_hypernyms(syn, depth):
    
    hyns = syn.hypernyms()
    ret = hyns[:]
    if hyns and syn.max_depth() > depth:
        for h in hyns:
            ret += get_all_hypernyms(h, depth)
    return ret

def compute_jc_sim(lemma1, lemma2):
    syns1 = wn.synsets(lemma1)
    syns2 = wn.synsets(lemma2)

    allsyns1 = syns1[:]
    allsyns2 = syns2[:]

    lemmas1 = []
    lemmas2 = []

    for s in syns1:
        allsyns1 += get_all_hypernyms(s,3)

    for s in allsyns1:
        lemmas1 += [i.name.lower() for i in s.lemmas]
    
    for s in syns2:
        allsyns2 += get_all_hypernyms(s,3)

    for s in allsyns2:
        lemmas2 += [i.name.lower() for i in s.lemmas]

    lemmas1 = set(lemmas1)
    lemmas2 = set(lemmas2)
    
    n = len(lemmas1.intersection(lemmas2))
    return n / float(len(lemmas1) + len(lemmas2) - n)

def compute_idfs():
    dfs = {}
    
    total = 0
    for syn in wn.all_synsets():
        docs = [syn.definition] + syn.examples
        docs = [s.lower() for s in docs]
        for s in docs:
            for w in word_tokenize(s):
                if w not in dfs:
                    dfs[w] = 0
                dfs[w] += 1
                total += 1
    
    return {w:-1*log(dfs[w]/float(total)) for w in dfs.keys()}

def get_idfs():
    idfs = {}
    idfs_file = open("/data0/projects/crossword_clues/wsd_experiments/wn_idfs.txt", "r")

    for line in idfs_file:
        line = line.strip()
        (word, idf) = line.split("\t")
        idfs[word] = float(idf)

    return idfs
    

# idfs = compute_idfs()

# for w in idfs.keys():
#     print "%s\t%.4f" % (w, idfs[w])

if(__name__ == "__main__"):
    print compute_lc_sim('committee', 'legislature')
    print get_rel_lemmas("english%1:10:00::")
    print lemmatize(nltk.word_tokenize("the birds were flying in the airports with change-ringing in their pockets"))
    
