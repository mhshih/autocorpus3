from django import forms
class UploadFileForm(forms.Form):
    file=forms.FileField()

static_path='autocorpus3/static/'
class Corpus:
    def __init__(self,fn):
        f=open(static_path+fn).read()
        self.filename=fn
        self.words=len(f.split())
        self.sentences=len(f.strip().split('\n'))

from os import listdir
from django.shortcuts import render
def home(request):      #Form action=/
    raw_corpora=[Corpus(fn) for fn in listdir(static_path) if fn.endswith('txt')]
    segmented_corpora=[Corpus(fn) for fn in listdir(static_path) if fn.endswith('segmented')]
    parsed_corpora=[Corpus(fn) for fn in listdir(static_path) if fn.endswith('conllu')]
    SE7_corpora=[Corpus(fn) for fn in listdir(static_path) if fn.endswith('xml.utf8.segmented.parsed')]
    return render(request,'template.htm',{'raw_corpora':raw_corpora,'segmented_corpora':segmented_corpora,'parsed_corpora':parsed_corpora,'SE7_corpora':SE7_corpora,'upload_form':UploadFileForm()})

from django.shortcuts import redirect
def upload(request):    #Form action=/upload
    RF=request.FILES['file']
    f=open('autocorpus3/static/'+RF.name,'wb+')
    for chunk in RF.chunks():f.write(chunk)
    f.close()
    return redirect('/')

from os import system
def segmenter(request):
    raw_corpus=request.GET['raw_corpus']
    command='cd ../stanford-segmenter-2016-10-31; bash segment.sh ctb ../autocorpus3/autocorpus3/static/%s UTF-8 0 > ../autocorpus3/autocorpus3/static/%s.segmented' % (raw_corpus,raw_corpus)
    system(command)
    return redirect('/')

from conllx import parse
def parser(request):     #Form action=/parser
    parse(segmented_file=request.GET['segmented_corpus'])
    return redirect('/')

from conllx import DCR,triples_to_HRD_dict,triples_to_DRH_dict
#from collections import defaultdict
def grammatical_collocation(request):     #Form action=/grammatical_collocation
    word=request.GET['word']#.encode('utf8') for python2
    corpus_file=request.GET['parsed_corpus']
#   triples=read_conllx_triples('/tmp/autocorpus3/autocorpus3/static/'+corpus_file)
    DRH=dict();HRD=dict()
    dcr=DCR(root='/tmp/autocorpus3/autocorpus3/static',fileids=[corpus_file])
    for parsed_sent in dcr.parsed_sents():
        triples=parsed_sent.triples()
        HRD=triples_to_HRD_dict(triples,HRD)
        DRH=triples_to_DRH_dict(triples,DRH)
    if word not in DRH:DRH[word]={'rel':'head'}
    if word not in HRD:HRD[word]={'rel':'dependent'}
    return render(request,'collocation.htm',{'word':word,'RH':DRH[word],'RD':HRD[word]})

def sense_collocation(request):
    pass
