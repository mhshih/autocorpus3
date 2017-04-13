from nltk.corpus.reader.util import concat
from nltk.corpus.reader import DependencyCorpusView
from nltk.parse import DependencyGraph

def read_conll_triples(corpus_file='Chinese_train_pos.xml.utf8.txt.conll'):
    triples=[]
    sents=concat([DependencyCorpusView(corpus_file,tagged=False,group_by_sent=True,dependencies=True)])
    for sent in sents:
        dg=DependencyGraph(sent)#,top_level_label='root')
        triples+=dg.triples()
    return triples

def extract_collocations(triples=read_conll_triples()):
    d=dict()
    for head,rel,dep in triples:
        if head not in d:d[head]={rel:[dep]}
        elif rel not in d[head]:d[head][rel]=[dep]
        else:d[head][rel].append(dep)
    return d

if __name__=='__main__':
    triples=read_conll_triples()
#   for head,rel,dep in triples:print(head,rel,dep)
    for head,rel_deps in extract_collocations().items():
        print(head)
        for rel,deps in rel_deps.items():
            print(rel,deps)
        print()

