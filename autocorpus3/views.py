from django import forms
class UploadFileForm(forms.Form):
    file=forms.FileField()

static_path='autocorpus3/static/'
class Corpus:
    def __init__(self,fn):
        f=open(static_path+fn).read()
        self.filename=fn
        self.words=len(f.split())
        self.sentences=len(f.split('\n'))

from os import listdir
from django.shortcuts import render
def home(request):      #Form action=/
    raw_corpora=[Corpus(fn) for fn in listdir(static_path) if fn.endswith('txt')]
    segmented_corpora=[Corpus(fn) for fn in listdir(static_path) if fn.endswith('segmented')]
    parsed_corpora=[Corpus(fn) for fn in listdir(static_path) if fn.endswith('parsed')]
    SE7_corpora=[Corpus(fn) for fn in listdir(static_path) if fn.find('xml')>-1]
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

from parse import parse
def parser(request):     #Form action=/parser
    segmented_corpus=request.GET['segmented_corpus']
    parse(filename=segmented_corpus)
    return redirect('/')

from parse import read_parse
def grammatical_collocation(request):     #Form action=/grammatical_collocation
    dependent=request.GET['word']#.encode('utf8') for python2
    parsed_corpus=request.GET['parsed_corpus']
    DRH=read_parse(parsed_corpus)
    return render(request,'collocation.htm',{'word':dependent,'RH':DRH[dependent]})

def sense_collocation(request):
    pass
