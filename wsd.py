from sys import argv

from senseval import SensevalCorpusReader
train_instances=SensevalCorpusReader(root='.',fileids=argv[1]).instances() #Training Senses.xml

from conllx import DCR  # DependencyCorpusReader
dcr=DCR(root='.',fileids=argv[2]) #Training Sentences.conllu
train_parsed_sents=dcr.parsed_sents()

#Get parsed feature for word sense
train=dict() #d[instance.word]={instance.sense:parsed_sents}
for i in range(len(train_instances)):
    train_word=train_instances[i].word
    train_sense=train_instances[i].senses[0]
    train_parsed_sent=train_parsed_sents[i]

    if train_word not in train:train[train_word]={train_sense:[train_parsed_sent]}
    elif train_sense not in train[train_word]:train[train_word][train_sense]=[train_parsed_sent]
    else:train[train_word][train_sense].append(train_parsed_sent)


#WSD and Evaluation
from collections import defaultdict,OrderedDict

test_instances=SensevalCorpusReader(root='.',fileids=argv[3]).instances()#train_instances       # Testing Senses?
test_parsed_sents=DCR(root='.',fileids=argv[4]).parsed_sents()#train_parsed_sents   # Testing Sentences.conllu
keys=open(argv[5]).readlines()
for i in range(len(test_instances)):
    test_word=test_instances[i].word
    test_instance_id=test_instances[i].instance
    key_sense=keys[i].split(' ')[2].strip()#test_instances[i].senses[0]
    test_parsed_sent=test_parsed_sents[i]

    dd=defaultdict(list) #d[sense]=test_triples.intersection(train_triples)
    n=0
    test_triples_set=set(test_parsed_sent.triples())
    for train_sense in train[test_word]:
        for train_parsed_sent in train[test_word][train_sense]:
            train_triples_set=set(train_parsed_sent.triples())
            n+=len(train_triples_set)
            dd[train_sense]+=list(test_triples_set.intersection(train_triples_set))
#   print(dd.items())
#   print(sorted(dd.items(),key=lambda x:len(x[1]),reverse=True)) #Replicable to 30 falses.

    od=OrderedDict(sorted(dd.items(),key=lambda x:len(x[1])))#,reverse=True)) #Replicable to 30 falses.
    max_sense,max_triples=od.popitem()
    if key_sense==max_sense:print(1,end='\t')
    else:print(0,end='\t')   # Cut -f 2 | sort | uniq -c

    print(test_word,test_instance_id,key_sense,end='\t')

    print(max_sense,len(max_triples),'/',n,end='\t')
    for sense,triples in od.items():
        print(sense,len(triples),'/',n,end='\t')
        if len(triples)>len(max_triples):
            max_sense,max_triples=sense,triples
            print('hahahahahhahahahahaha')
#   print(max_sense,end='\t')
    print()
