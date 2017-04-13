from nltk.corpus.reader.util import concat
from nltk.corpus.reader import DependencyCorpusView
from nltk.parse import DependencyGraph

corpus_file='Chinese_train_pos.xml.utf8.Chinese_medicine.segmented.conllx'

def read_conllx_triples(corpus_file='Chinese_train_pos.xml.utf8.Chinese_medicine.segmented.conllx'):
    triples=[]
    sents=concat([DependencyCorpusView(corpus_file,tagged=False,group_by_sent=True,dependencies=True)])
    for sent in sents:
        dg=DependencyGraph(sent,top_relation_label='root')
        triples+=dg.triples()
    return triples

def extract_collocations(triples=read_conllx_triples()):
    d=dict()
    for head,rel,dep in triples:
        if head not in d:d[head]={rel:[dep]}
        elif rel not in d[head]:d[head][rel]=[dep]
        else:d[head][rel].append(dep)
    return d


from nltk.corpus.reader.dependency import DependencyCorpusReader

class DCR(DependencyCorpusReader):
    def parsed_sents(self,fileids=None):
        sents=concat([DependencyCorpusView(fileid, False, True, True, encoding=enc) for fileid, enc in self.abspaths(fileids, include_encoding=True)])
        return [DependencyGraph(sent,top_relation_label='root') for sent in sents]

if __name__=='__main__':
    dcr=DCR(root='.',fileids=[corpus_file])
    for parsed_sent in dcr.parsed_sents():
        triples=parsed_sent.triples()#read_conllx_triples()
        for head,rel,dep in triples:print(head,rel,dep)
'''
    for head,rel_deps in extract_collocations().items():
        print(head)
        for rel,deps in rel_deps.items():
            print(rel,deps)
        print()
        '''
