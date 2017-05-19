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

#Get parsed feature for word sense
#Read senseval instance and parsed_sents together.
from collections import OrderedDict
def combine_sense_instance_with_parsed_sent(train_instances,train_parsed_sents):
    train=OrderedDict() #d[instance.word]={instance.sense:parsed_sents}
    for i in range(len(train_instances)):
        train_word=train_instances[i].word
        train_sense=train_instances[i].senses[0]
        train_parsed_sent=train_parsed_sents[i]
        if train_word not in train:train[train_word]=OrderedDict({train_sense:[train_parsed_sent]})
        elif train_sense not in train[train_word]:train[train_word][train_sense]=[train_parsed_sent]
        else:train[train_word][train_sense].append(train_parsed_sent)
    for word,sense_sents in train.items():train[word]=OrderedDict(sorted(sense_sents.items()))
    return train

#Print sense,collocation, and sentence.
from collections import defaultdict
def collocate_sense(train,target_word='吃'):#中医'#本'
    rsds=defaultdict(dict)#OrderedDict()#defaultdict(dict)) #rsds[rel][sense]={dep:freq}
    for sense,parsed_sents in train[target_word].items():
        rel_dep_sents=dict()#defaultdict(list)
        for DG in parsed_sents:
            for head_tag,rel,dep_tag in DG.triples():
                head,htag=head_tag
                dep,dtag=dep_tag
                if target_word==head:
                    if rel not in rel_dep_sents:rel_dep_sents[rel]=defaultdict(list)
                    rel_dep_sents[rel][dep].append(' '.join(DG.words))
        for rel,dep_sents in rel_dep_sents.items():
            deps=dep_sents.keys()
            if rel not in rsds:
#               rsds[rel]=defaultdict(dict)#list)
                for s in train[target_word]:rsds[rel][s]=defaultdict(list)#()
#               rsds[rel][sense]+=deps
            for dep,sents in dep_sents.items():rsds[rel][sense][dep]+=sents

    for rel,sense_deps in rsds.items():
        rsds[rel]=OrderedDict(sorted(sense_deps.items()))
    od=OrderedDict()
    for rel,sense_deps in rsds.items():
#       print(rel,end='\t')
        od[rel]=OrderedDict()
        for sense,deps in sorted(sense_deps.items()):
#           print(sense,deps.keys(),end='\t')
            od[rel][sense]=OrderedDict()
            for dep,sents in sorted(deps.items(),key=lambda x:len(x[1]),reverse=True):od[rel][sense][dep]=sents
#       print()
    od.move_to_end('nsubj',last=False)
    od.move_to_end('dobj',last=False)
    for rel,sds in od.items():
        print(rel,end='\t')
        for sense,dep_sents in sds.items():
            print(sense,list(dep_sents.keys()),end='\t')
        print()
    return rsds


from sys import argv
from senseval import SensevalCorpusReader
from conllx import DCR  # DependencyCorpusReader

if __name__=='__main__':
    train_instances=SensevalCorpusReader(root='.',fileids=argv[1]).instances() #Chinese_train_pos.xml.utf8
    train_parsed_sents=DCR(root='.',fileids=argv[2]).parsed_sents() #Chinese_train_pos.xml.utf8.segmented.conllu
    train=combine_sense_instance_with_parsed_sent(train_instances,train_parsed_sents)

    #Print sense,collocation, and sentence.
    collocate_sense(train=train)

    #WSD and Evaluation
    test_instances=SensevalCorpusReader(root='.',fileids=argv[3]).instances()#train_instances       # Testing Senses?
    test_parsed_sents=DCR(root='.',fileids=argv[4]).parsed_sents()#train_parsed_sents   # Testing Sentences.conllu
    keys=open(argv[5]).readlines()

    f_d=OrderedDict() #f_d[word][(instance_id,key_sense)]={sense:intersected_triples}
    word_instance_distributions=OrderedDict()
    for i in range(len(test_instances)):
        test_word=test_instances[i].word
        test_instance_id=test_instances[i].instance
        key_sense=keys[i].split(' ')[2].strip()#test_instances[i].senses[0]
        test_parsed_sent=test_parsed_sents[i]
        if test_word not in word_instance_distributions:word_instance_distributions[test_word]=[Instance_Distribution(test_instances[i],key_sense,train[test_word],test_parsed_sents[i])]
        else:word_instance_distributions[test_word].append(Instance_Distribution(test_instances[i],key_sense,train[test_word],test_parsed_sents[i]))
    for target_word,test_instance_distributions in word_instance_distributions.items():
        m=avg_intersected_triples=0         # m=number of labeled correctly to one specific target word type.
        for test_instance in test_instance_distributions:
            if test_instance.key_sense==test_instance.max_sense:m+=1
            for sense,intersected_triples in list(test_instance.test_sense_triples.items())[:2]:avg_intersected_triples+=len(intersected_triples)
        sense_num=len(test_instance.train_sense_sents)
        training_num=len(list(chain.from_iterable([sents for sense,sents in test_instance.train_sense_sents.items()])))
        n=len(test_instance_distributions)  # n=number of all test instance for this word-type.
        Pmar=m/n

