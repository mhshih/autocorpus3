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

class CountryForm(forms.Form):
        OPTIONS = (
                ("AUT", "Austria"),
                ("DEU", "Germany"),
                ("NLD", "Neitherlands"),
                )
        Countries = forms.ChoiceField(widget=forms.Select,
                                             choices=OPTIONS)

form=CountryForm

from conllx import DCR  # DependencyCorpusReader
from senseval import SensevalCorpusReader

from os import listdir
from django.shortcuts import render
def home(request):      #Form action=/
    raw_corpora=[Corpus(fn) for fn in sorted(listdir(static_path)) if fn.endswith('txt')]
    segmented_corpora=[Corpus(fn) for fn in sorted(listdir(static_path)) if fn.endswith('segmented')]
    parsed_corpora=[DCR(root=static_path,fileids=[fn]) for fn in sorted(listdir(static_path)) if fn.endswith('conllu')]
    SensevalCorpora=[SensevalCorpusReader(root=static_path,fileids=fn) for fn in sorted(listdir(static_path)) if fn.endswith('xml.utf8')]
    return render(request,'template.htm',{'raw_corpora':raw_corpora,'segmented_corpora':segmented_corpora,'parsed_corpora':parsed_corpora,'SensevalCorpora':SensevalCorpora,'upload_form':UploadFileForm(),'form':form})

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
def build_parsed_dict(fileids='Chinese_train_pos.xml.utf8.segmented.conllu'):
    DRH=dict();HRD=dict()
    dcr=DCR(root='/tmp/autocorpus3/autocorpus3/static',fileids=fileids)
    for parsed_sent in dcr.parsed_sents():
        triples=parsed_sent.triples()
        HRD=triples_to_HRD_dict(triples,HRD)
        DRH=triples_to_DRH_dict(triples,DRH)
    return DRH,HRD

def grammatical_collocation(request):     #Form action=/grammatical_collocation
    word=request.GET['word']#.encode('utf8') for python2
    corpus_file=request.GET['parsed_corpus']
    DRH,HRD=build_parsed_dict(fileids=corpus_file)
    if word not in DRH:DRH[word]={'rel':'head'}
    if word not in HRD:HRD[word]={'rel':'dependent'}
    return render(request,'collocation.htm',{'word':word,'RH':DRH[word],'RD':HRD[word]})

from django.http import HttpResponse
DRH,HRD=build_parsed_dict()
def api(request,word,rel,dep):
    return HttpResponse(HRD[word][rel])#word+rel+dep)

from senseval import SensevalCorpusReader
from conllx import DCR
from wsd import combine_sense_instance_with_parsed_sent,collocate_sense
root='autocorpus3/static'
train_instances=SensevalCorpusReader(root,'Chinese_train_pos.xml.utf8').instances()
train_parsed_sents=DCR(root,'Chinese_train_pos.xml.utf8.segmented.conllu').parsed_sents()
train=combine_sense_instance_with_parsed_sent(train_instances,train_parsed_sents)
def sense_collocation(request):
    form=CountryForm(request.GET)
    if form.is_valid():
        countries=form.cleaned_data.get('Countries')
    return HttpResponse(countries)
    rsd=collocate_sense(train)
    return render(request,'sense_collocation.htm',{'rsd':rsd,'senses':rsd.popitem()[1].keys()})
