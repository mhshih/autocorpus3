from os import system

def append2DRH(dep,rel,head,DRH):
    if dep not in DRH:DRH[dep]={rel:[head]}
    elif rel not in DRH[dep]:DRH[dep][rel]=[head]
    else:DRH[dep][rel].append(head)

def parse(filename):#='chinese-onesent-utf8.txt'):
    command='cd /home/simon/stanford-parser-full-2016-10-31; java -mx1500m -cp "*:" edu.stanford.nlp.parser.lexparser.LexicalizedParser -outputFormat "typedDependencies" edu/stanford/nlp/models/lexparser/chinesePCFG.ser.gz /tmp/autocorpus3/autocorpus3/static/%s > /tmp/autocorpus3/autocorpus3/static/%s.parsed' % (filename,filename)
    system(command)

def read_parse(filename):
    DRH=dict() #DRH[dep]={rel:heads}
    for line in open('/tmp/autocorpus3/autocorpus3/static/'+filename).readlines()[:-1]:
        if len(line)==1:continue
        rel,dep_head=line.split('(')[:2]
        dep,head=[w.split('-')[0] for w in dep_head.split()]
        append2DRH(dep,rel,head,DRH)
    return DRH

