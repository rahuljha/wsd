#!/usr/bin/python

from __future__ import division

import sys
sys.dont_write_bytecode = True

import xml.etree.ElementTree as ET
import sys
from wsd_algorithms import WsdAlgos

class SenseJudgement:
    def __init__(self, wid, true, predicted):
        self.wid = wid
        self.true = true
        self.predicted = predicted
    def __repr__(self):
        return self.wid+"\t"+self.true+"\t"+self.predicted
    

files = ["/data0/projects/crossword_clues/wsd_experiments/senseval2.semcor/wordnet3.0/d00.semcor.lexsn.fixed.key",
         "/data0/projects/crossword_clues/wsd_experiments/senseval2.semcor/wordnet3.0/d01.semcor.lexsn.fixed.key",
         "/data0/projects/crossword_clues/wsd_experiments/senseval2.semcor/wordnet3.0/d02.semcor.lexsn.fixed.key"]

algos = WsdAlgos()

for f in files:
    judgements = []
    try:
        tree = ET.parse(f)
    except Exception as e:
        print e.position

    root = tree.getroot()

    for sent in root.iter('s'):
#        print "Sent %s" % sent.attrib['snum']

        p_senses = algos.slesk(sent)
        for wf in sent:
            if 'id' in wf.attrib and wf.attrib['id'] in p_senses:
                judgements.append(SenseJudgement(wf.attrib['id'], wf.attrib['lexsn'], p_senses[wf.attrib['id']]))
            

    correct = 0
    provided = 0
    total = 0

    for sj in judgements:
        pred = sj.predicted
        trues = sj.true.split(';')
        total += len(trues)
        provided += 1
        if(pred in trues):
            correct += 1

    print "Total: %d" % total
    print "Precision: %.2f, Recall: %.2f" % (correct/provided, correct/total)
