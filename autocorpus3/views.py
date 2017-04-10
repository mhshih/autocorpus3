from django import forms
class UploadFileForm(forms.Form):
    file=forms.FileField()

from parse import read_parse
from django.http import HttpResponse
from django.shortcuts import render
def query(request):
    corpus=request.POST['radio']
    DRH=read_parse(corpus)
    dependent=request.POST['word']#.encode('utf8') for python2
    return render(request,'collocation.htm',{'word':dependent,'RH':DRH[dependent]})

def write_RF(RF):
    f=open('autocorpus3/static/'+RF.name,'wb+')
    for chunk in RF.chunks():f.write(chunk)
    f.close()

from os import listdir
from django.shortcuts import render,redirect
from parse import parse
def home(request):
    segmented_corpora=[fn for fn in listdir('autocorpus3/static') if fn.endswith('segmented')]
    parsed_corpora=[fn for fn in listdir('autocorpus3/static') if fn.endswith('parsed')]
    if request.method=='GET':
        return render(request,'template.htm',{'segmented_corpora':segmented_corpora,'parsed_corpora':parsed_corpora,'upload_form':UploadFileForm()})
    elif request.method=='POST':
        RF=request.FILES['file']
        write_RF(RF)
        parse(filename=RF.name)
        return redirect('/')

