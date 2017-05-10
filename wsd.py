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
        self.train_sense_sents=train_sense_sents
        self.train_triples=set()
        self.test_parsed_sent=test_parsed_sent
        d=OrderedDict()    # d[sense]=test_triples.intersection(train_triples)
        for sense,train_parsed_sents in train_sense_sents.items():
            train_triples=set(chain.from_iterable([train_parsed_sent.triples() for train_parsed_sent in train_parsed_sents]))
            self.train_triples.union(train_triples)
            test_triples=set(test_parsed_sent.triples())
            intersected_triples=test_triples.intersection(train_triples)
            d[sense]=sorted(intersected_triples)
        self.test_sense_triples=OrderedDict(sorted(d.items(),key=lambda x:len(x[1]),reverse=True))  # Replicable
        self.max_sense=list(self.test_sense_triples.keys())[0]

f_d=OrderedDict() #f_d[word][(instance_id,key_sense)]={sense:intersected_triples}

word_instance_distributions=OrderedDict()
flag=0#n=0
for i in range(len(test_instances)):
    test_word=test_instances[i].word
    test_instance_id=test_instances[i].instance
    key_sense=keys[i].split(' ')[2].strip()#test_instances[i].senses[0]
    test_parsed_sent=test_parsed_sents[i]

    if test_word not in word_instance_distributions:
        word_instance_distributions[test_word]=[Instance_Distribution(test_instances[i],key_sense,train[test_word],test_parsed_sents[i])]
    else:
        word_instance_distributions[test_word].append(Instance_Distribution(test_instances[i],key_sense,train[test_word],test_parsed_sents[i]))
for test_word,test_instance_distributions in word_instance_distributions.items():
    for test_instance in test_instance_distributions:
        if test_instance.key_sense==test_instance.max_sense:print(1,end='\t')
        else:print(0,end='\t')
        print(test_instance.instance_id,test_instance.key_sense,end='\t')
        for sense,intersected_triples in test_instance.test_sense_triples.items():
            print(sense,len(intersected_triples),intersected_triples,end='\t')
        print(len(test_instance.train_triples))

'''
    od=OrderedDict() #d[sense]=test_triples.intersection(train_triples)
    n=0
    test_triples_set=set(test_parsed_sent.triples())
    for sense in train[test_word]:

        for train_parsed_sent in train[test_word][sense]:
            train_triples_set=set(sorted([triple for triple in train_parsed_sent.triples()]))
            n+=len(train_triples_set)
            if sense not in od:od[sense]=list(test_triples_set.intersection(train_triples_set))
            elif sense in od:od[sense]+=list(test_triples_set.intersection(train_triples_set))


    od=OrderedDict(sorted(od.items(),key=lambda x:len(x[1]),reverse=True)) #Replicable to 30 falses.
    for sense,intersected_triples in od.items():
        if test_word not in f_d:
            f_d[test_word]=OrderedDict({(test_instance_id,key_sense):OrderedDict({sense:intersected_triples})})
        elif (test_instance_id,key_sense) not in f_d[test_word]:
            f_d[test_word][(test_instance_id,key_sense)]=OrderedDict({sense:intersected_triples})
        else:
            f_d[test_word][(test_instance_id,key_sense)][sense]=intersected_triples

    max_sense,max_triples=od.popitem()
    second_sense,second_triples=od.popitem()

#   Print Summarized_Feature_Distribution.tsv
    if flag:
        if test_word != previous_word:
#           print(previous_word,previous_top2_triples[0],previous_top2_triples[1],n,sep='\t')   # > Feature_Distribution.tsv
            previous_word=test_word
            previous_top2_triples=[len(max_triples),len(second_triples)] #[max_matched_number,second_matched_number]
        elif test_word == previous_word:
            previous_top2_triples[0]+=len(max_triples)
            previous_top2_triples[1]+=len(second_triples)
    elif not flag:
        previous_word=test_word
        previous_top2_triples=[len(max_triples),len(second_triples)] #[max_matched_number,second_matched_number]
#       print(previous_word,previous_top2_triples[0],previous_top2_triples[1],n,sep='\t')       # > Feature_Distribution.tsv
        flag=1
#print(previous_word,previous_top2_triples[0],previous_top2_triples[1],n,sep='\t')

for test_word in f_d:#.items(): #f_d[word][(instance_id,key_sense)]={sense:intersected_triples}
    for id_key,sense_triples in f_d[test_word].items():
        test_instance_id,key_sense=id_key
        max_sense=list(sense_triples.keys())[0]
        if max_sense==key_sense:    # Micro-average Precision
            print(1,end='\t')  
        else:print(0,end='\t')

        print(test_instance_id,end='\t')
        print(key_sense,end='\t')
        for sense,triples in sense_triples.items():
            print(sense,end='\t')
            print(len(triples),end='\t')
            print(triples,end='\t')
        print()#n)
'''
