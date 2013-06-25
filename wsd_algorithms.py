#!/usr/bin/python

import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
import re
import random
import operator
import math

import text_utils


class WsdAlgos:
    def random(self, wordforms):
        sensepreds = {}
        for wf in wordforms:
            if('cmd' in wf.attrib and wf.attrib['cmd'] == 'done'):
                lemma = wf.attrib['lemma'] # may be need to automatically lemmatize here
                try:
                    senseid = random.choice(self.get_sense_keys(lemma)) 
                except(IndexError):
                    print "Error: No senses for %s" % (lemma)
                    senseid = None
                if(senseid):
                    m = re.match("^"+lemma+"\%(\d+:\d+:\d+:(.*))", senseid)
                    sensepreds[wf.attrib['id']] = m.group(1)
                else:
                    sensepreds[wf.attrib['id']] = "gibberish"
        return sensepreds

    def mfs(self, wordforms):
        sensepreds = {}
        for wf in wordforms:
            if('cmd' in wf.attrib and wf.attrib['cmd'] == 'done'):
                lemma = wf.attrib['lemma'] # may be need to automatically lemmatize here
                senseid = self.get_mfs(lemma)
                if(senseid):
                    m = re.match("^"+lemma+"\%(\d+:\d+:\d+:(.*))", senseid)
                    sensepreds[wf.attrib['id']] = m.group(1)
                else:
                    sensepreds[wf.attrib['id']] = "gibberish"
        return sensepreds        

    def get_mfs(self, lemma, sensekeys = None):
        senseid = None
        try:
            if(not sensekeys):
                sensekeys = self.get_sense_keys(lemma)
            sense_freqs = {}
            for i in sensekeys:
                lemma_obj = wn.lemma_from_key(i)
                sense_freqs[i] = lemma_obj.count()
                
            senseid = max(sense_freqs.iteritems(), key=operator.itemgetter(1))[0]
        except(ValueError):
            print "Error: No senses for %s" % (lemma)
        return senseid

    def slesk(self, wordforms):
        sensepreds = {}
        sw_hash = {i:1 for i in stopwords.words('english')}

        open_wfs = [i for i in wordforms if i.tag != 'punc' and not ('cmd' in i.attrib and i.attrib['cmd'] == "ignore")] # remove stop words and punctuation first
#        open_wfs = [i for i in wordforms if i.tag != 'punc'] # remove only punctuation

        for wf in wordforms:
            if('cmd' in wf.attrib and wf.attrib['cmd'] == 'done'):
                lemma = wf.attrib['lemma'] # may be need to automatically lemmatize here
                
                sensekeys = self.get_sense_keys(lemma)
                if(len(sensekeys) == 0):
                    print "Error: No senses for %s" % lemma
                    continue
                synsets = {k: wn.lemma_from_key(k).synset for k in sensekeys}

                idfs = text_utils.get_idfs()

                # get the window now
                window = 2
                idx = [i for i,x in enumerate(open_wfs) if x == wf][0]
                lbound = idx-window if idx-window > 0 else 0 
                ubound = idx+window if idx+window < len(open_wfs) else len(open_wfs)-1

#                all_context = set(text_utils.lemmatize(([i.text.lower() for i in open_wfs[lbound:(ubound+1)] if ('cmd' not in i.attrib or (i.attrib['cmd'] != "ignore" and i.attrib['id'] != wf.attrib['id']))]))) # this one keeps stopwords in window count
                all_context = set(text_utils.lemmatize(([i.text.lower() for i in open_wfs[lbound:(ubound+1)] if (i.attrib['id'] != wf.attrib['id'])]))) # this one keeps stopwords in window count


                jc_th = 0.1
                context = [i for i in all_context if text_utils.compute_jc_sim(i,lemma) > jc_th] # lexical chain selection algorithm

                outstr = "-------------------"
                outstr += "\ncontext: "+str(context)

#                best = self.get_mfs(lemma)
                max = 0
                cands = []

                for k in synsets.keys():
                    synset = synsets[k]
                    wntext = text_utils.lemmatize(nltk.word_tokenize(synset.definition))
                    for ex in synset.examples:
                        wntext += text_utils.lemmatize(nltk.word_tokenize(ex))
                        
#                    wntext += text_utils.lemmatize(text_utils.get_rel_lemmas(k)) # related lemmas from hypernyms etc.

                    wntext = [i.lower() for i in wntext]
                    lenlog = math.log(len(wntext))
                    normalizer = 1/ lenlog if lenlog > 0 else 0
                    outstr += "\n"+k+":"+str(wntext)
                    wn_hash = {i:1 for i in wntext}

                    matches = {}
                    score = 0
                    for i in context:
                        if(i in sw_hash): continue
                        if i in wntext:
                            score += 1
                            # if i in idfs:
                            #     score += idfs[i]
                            # else:
                            #     score += 3
                            matches[i] = 1 #idfs[i]
                    outstr += "\nScore: %s:%f" % (matches,score)
#                    score = score * normalizer
                    outstr += "\nNorm score: %s:%f" % (matches,score)
                    if score > max:
                        cands = [k]
                        max = score
                    elif score == max:
                        cands.append(k)

                if(len(cands) > 1):
                    best = self.get_mfs(lemma, cands)
                else:
                    best = cands[0]
            

                mfs_id = self.get_mfs(lemma)
                true_id = lemma+"%"+wf.attrib['lexsn']
                if mfs_id == true_id and best != mfs_id:
                    print "stat:leskbad"
                    print outstr
                    print "MFS: %s, LESK: %s, CORRECT: %s" % (self.get_mfs(lemma), best, wf.attrib['lexsn'])
                elif mfs_id != true_id and best == true_id:
                    print "stat:leskgood"
                    print outstr
                    print "MFS: %s, LESK: %s, CORRECT: %s" % (self.get_mfs(lemma), best, wf.attrib['lexsn'])
                elif max == 0:
                    print "stat:nolesk"
                else:
                    print "stat:lesksame"

                if(best):
                    m = re.match("^"+lemma+"\%(\d+:\d+:\d+:(.*))", best)
                    sensepreds[wf.attrib['id']] = m.group(1)
                else:
                    sensepreds[wf.attrib['id']] = "gibberish"
                
        return sensepreds
            
    def get_sense_keys(self, lemma):
#        regex = re.compile("^"+lemma+"\%(\d+:\d+:\d+:(.*))")
        synsets = wn.synsets(lemma)
        keys = []
        for syn in synsets:
            # lset = [l for l in syn.lemmas]
            # for i in lset:
            #     m = regex.match(i.key) 
            #     if(m):
            #         keys.append(m.group(1))
            matching_keys = [l.key for l in syn.lemmas if l.name.lower() == lemma.lower()]
            if(len(matching_keys) > 0):
                keys.append(matching_keys[0])
        return keys

if(__name__ == "__main__"):
    wsd = WsdAlgos()                
    print wsd.get_sense_keys('evening')
    print wsd.get_sense_keys('dog')
    print 'done'
