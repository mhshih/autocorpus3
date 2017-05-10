#-*-coding:utf8-*-

from nltk.corpus.reader.util import concat
from nltk.corpus.reader import DependencyCorpusView
from nltk.parse import DependencyGraph
from os import system

def parse(path='/tmp/autocorpus3/autocorpus3/static/',segmented_file='Chinese_train_pos.xml.utf8.Chinese_medicine.segmented'):
    command='''cd /tmp/stanford-corenlp-full-2016-10-31;
               java -mx3g  -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLP -props StanfordCoreNLP-chinese.properties -annotators tokenize,ssplit,pos,depparse -outputFormat conllu -file %s;
               mv /tmp/stanford-corenlp-full-2016-10-31/%s /tmp/autocorpus3/autocorpus3/static
               ''' % (path+segmented_file,segmented_file+'.conllu');#Default output in stanford-cornlp folder;cannot stdout redirect;need to check java output file name and path parameter.
    system(command)

def read_conllx_triples(corpus_file):#='/tmp/autocorpus3/autocorpus3/static/Chinese_train_pos.xml.utf8.Chinese_medicine.segmented.conllx'):
    triples=[]
    sents=concat([DependencyCorpusView(corpus_file,tagged=False,group_by_sent=True,dependencies=True)])
    for sent in sents:
        dg=DependencyGraph(sent,top_relation_label='root')
        triples+=dg.triples()
    return triples

def triples_to_HRD_dict(triples,d):#=read_conllx_triples(corpus_file='/tmp/autocorpus3/autocorpus3/static/Chinese_train_pos.xml.utf8.Chinese_medicine.segmented.conllx'):
    for head,rel,dep in triples:
        head,dep=[word for word,pos in [head,dep]]
        if head not in d:d[head]={rel:[dep]}
        elif rel not in d[head]:d[head][rel]=[dep]
        else:d[head][rel].append(dep)
    return d

def triples_to_DRH_dict(triples,d):#=read_conllx_triples(corpus_file='/tmp/autocorpus3/autocorpus3/static/Chinese_train_pos.xml.utf8.Chinese_medicine.segmented.conllx'):
    for head,rel,dep in triples:
        head,dep=[word for word,pos in [head,dep]]
        if dep not in d:d[dep]={rel:[head]}
        elif rel not in d[dep]:d[dep][rel]=[head]
        else:d[dep][rel].append(head)
    return d

from nltk.corpus.reader.dependency import DependencyCorpusReader
class DCR(DependencyCorpusReader):  # Override DependencyGraph with top_relation_label='root' for conllx format.
    def parsed_sents(self,fileids=None):
        sents=concat([DependencyCorpusView(fileid, False, True, True, encoding=enc) for fileid, enc in self.abspaths(fileids, include_encoding=True)])
        return [DependencyGraph(sent,top_relation_label='root') for sent in sents]

from sys import argv
if __name__=='__main__':
#   parse()
    d=dict()
    dcr=DCR(root='.',fileids=[argv[1]])#'/tmp/autocorpus3/autocorpus3/static/Chinese_train_pos.xml.utf8.Chinese_medicine.segmented.conllu'])
    for parsed_sent in dcr.parsed_sents():
        triples=parsed_sent.triples()#read_conllx_triples()
#       for head,rel,dep in triples:print(head,rel,dep,end='\t')
        d=triples_to_HRD_dict(triples,d)
#   print(d['她'])#,'_')])
    for sent in dcr.sents():
        print(' '.join(sent))
