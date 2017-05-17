from sys import argv

from senseval import SensevalCorpusReader
train_instances=SensevalCorpusReader(root='.',fileids=argv[1]).instances() #Training Senses.xml

from conllx import DCR  # DependencyCorpusReader
dcr=DCR(root='.',fileids=argv[2]) #Training Sentences.conllu
train_parsed_sents=dcr.parsed_sents()

#Get parsed feature for word sense
from collections import OrderedDict
train=OrderedDict() #d[instance.word]={instance.sense:parsed_sents}
for i in range(len(train_instances)):
    train_word=train_instances[i].word
    train_sense=train_instances[i].senses[0]
    train_parsed_sent=train_parsed_sents[i]

    if train_word not in train:train[train_word]=OrderedDict({train_sense:[train_parsed_sent]})
    elif train_sense not in train[train_word]:train[train_word][train_sense]=[train_parsed_sent]
    else:train[train_word][train_sense].append(train_parsed_sent)

#WSD and Evaluation
test_instances=SensevalCorpusReader(root='.',fileids=argv[3]).instances()#train_instances       # Testing Senses?
test_parsed_sents=DCR(root='.',fileids=argv[4]).parsed_sents()#train_parsed_sents   # Testing Sentences.conllu
keys=open(argv[5]).readlines()

from itertools import chain
class Instance_Distribution:            # Consider inherit from SensevalCorpusReader in the future version.
    def __init__(self,test_instance,key_sense,train_sense_sents,test_parsed_sent):
        self.word=test_instance.word    # Consider inherit from SensevalCorpusReader in the future version.
        self.instance_id=test_instance.instance
        self.key_sense=key_sense
        self.train_sense_sents=train_sense_sents    # train[test_word]={sense:train_parsed_sents}
        self.train_triples=set()
        self.test_parsed_sent=test_parsed_sent
        d=OrderedDict()    # d[sense]=test_triples.intersection(train_triples)
        for sense,train_parsed_sents in train_sense_sents.items():
            train_triples=set(chain.from_iterable([train_parsed_sent.triples() for train_parsed_sent in train_parsed_sents]))
            self.train_triples=self.train_triples.union(train_triples)
            test_triples=set(test_parsed_sent.triples())
            intersected_triples=test_triples.intersection(train_triples)
            d[sense]=sorted(intersected_triples)
        self.test_sense_triples=OrderedDict(sorted(d.items(),key=lambda x:len(x[1]),reverse=True))  # Replicable
        self.max_sense=list(self.test_sense_triples.keys())[0]


f_d=OrderedDict() #f_d[word][(instance_id,key_sense)]={sense:intersected_triples}

word_instance_distributions=OrderedDict()
flag=0#n=0
print('target_word','sense_num','training_num','n','Pmar','avg_intersected_triples/n','len(test_instance.train_triples','m',sep='\t')
for i in range(len(test_instances)):
    test_word=test_instances[i].word
    test_instance_id=test_instances[i].instance
    key_sense=keys[i].split(' ')[2].strip()#test_instances[i].senses[0]
    test_parsed_sent=test_parsed_sents[i]

    if test_word not in word_instance_distributions:
        word_instance_distributions[test_word]=[Instance_Distribution(test_instances[i],key_sense,train[test_word],test_parsed_sents[i])]
    else:
        word_instance_distributions[test_word].append(Instance_Distribution(test_instances[i],key_sense,train[test_word],test_parsed_sents[i]))

for target_word,test_instance_distributions in word_instance_distributions.items():
    m=avg_intersected_triples=0         # m=number of labeled correctly to one specific target word type.
    for test_instance in test_instance_distributions:
        if test_instance.key_sense==test_instance.max_sense:
            m+=1
#           print(1,end='\t')
#       else:print(0,end='\t')
#       print(test_instance.instance_id,test_instance.key_sense,sep='\t',end='\t')
        for sense,intersected_triples in list(test_instance.test_sense_triples.items())[:2]:
            avg_intersected_triples+=len(intersected_triples)
#           print(sense,len(intersected_triples),intersected_triples,sep='\t',end='\t')
#       print(len(test_instance.train_triples))
    sense_num=len(test_instance.train_sense_sents)
    training_num=len(list(chain.from_iterable([sents for sense,sents in test_instance.train_sense_sents.items()])))
    n=len(test_instance_distributions)  # n=number of all test instance for this word-type.
    Pmar=m/n
    print(target_word,sense_num,training_num,n,round(Pmar,3),round(avg_intersected_triples/n,1),len(test_instance.train_triples),m,sep='\t')

