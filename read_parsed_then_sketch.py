import sys

f=open('train/instanceid_senseid_sentence.tsv')

d={} #d[gov]={rel:{dep:sents}}
grd={} #grd[gov]={rel:dep}
drg={} #drg[dep]={rel:gov}

rgd=[]
word=[]
for line in open(file=sys.argv[1]): #output file from Stanford parser
    if line!='\n':
        rel,gov_dep=line.split('(')
        gov,dep=gov_dep.split()
        gov=gov.split('-')[0]
        dep=dep.split('-')[0]
        rgd.append([rel,gov,dep])   #store in the list rgd all dependencies in a sentence 
        if gov not in grd:grd[gov]={rel:dep}
        else:grd[gov][rel]=dep
        if dep not in drg:drg[dep]={rel:gov}
        else:drg[dep][rel]=gov
        word.append(dep)
    else:
        sent=' '.join(word)
        for rel,gov,dep in rgd:
            if gov not in d:d[gov]={rel:{dep:[sent]}}
            elif rel not in d[gov]:d[gov][rel]={dep:[sent]}
            elif dep not in d[gov][rel]:d[gov][rel][dep]=[sent]
            else:d[gov][rel][dep].append(sent)
#           print(rel,gov,dep,sent)
#       if 'dobj' in d:
#       print(instanceid,senseid,sentence.strip(),d[gov])#['dobj'],sent)
        instanceid,senseid,sentence=f.readline().split('\t')
        lexelt=instanceid.split('.')[0]
        print(instanceid,senseid,sentence.strip(),drg[lexelt],sep='\t',end='\t')#,d)
        if lexelt in grd:print(grd[lexelt],end='\t')
        else:print(' ',end='\t')
        print(grd,drg,d,sep='\t')
        grd={}
        drg={}
        rgd=[]
        word=[]
        d={}

for gov,rel_dep_sents in d.items():
    for rel,dep_sents in rel_dep_sents.items():
        for dep,sents in dep_sents.items():
#           print(gov,rel,dep,sents)
            pass
