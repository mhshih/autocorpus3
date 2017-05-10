#-*-coding:utf8-*-

#nltk 3.2.1
# Natural Language Toolkit: Senseval 2 Corpus Reader
#
# Copyright (C) 2001-2016 NLTK Project
# Author: Trevor Cohn <tacohn@cs.mu.oz.au>
#         Steven Bird <stevenbird1@gmail.com> (modifications)
# URL: <http://nltk.org/>
# For license information, see LICENSE.TXT

"""
Read from the Senseval 2 Corpus.

SENSEVAL [http://www.senseval.org/]
Evaluation exercises for Word Sense Disambiguation.
Organized by ACL-SIGLEX [http://www.siglex.org/]

Prepared by Ted Pedersen <tpederse@umn.edu>, University of Minnesota,
http://www.d.umn.edu/~tpederse/data.html
Distributed with permission.

The NLTK version of the Senseval 2 files uses well-formed XML.
Each instance of the ambiguous words "hard", "interest", "line", and "serve"
is tagged with a sense identifier, and supplied with context.
"""
from __future__ import print_function, unicode_literals

import re
from xml.etree import ElementTree

from nltk import compat
from nltk.tokenize import *

from nltk.corpus.reader.util import *
from nltk.corpus.reader.api import *

@compat.python_2_unicode_compatible
class SensevalInstance(object):
    def __init__(self, word, position, context, senses,instance):
        self.word = word
        self.senses = tuple(senses)
        self.position = position
        self.context = context
        self.instance=instance

    def __repr__(self):
        return ('SensevalInstance(word=%r, position=%r, '
                'context=%r, senses=%r,instance=%r)' %
                (self.word, self.position, self.context, self.senses,self.instance))


class SensevalCorpusReader(CorpusReader):
    def instances(self, fileids=None):
        return concat([SensevalCorpusView(fileid, enc) for (fileid, enc) in self.abspaths(fileids, True)])

    def raw(self, fileids=None):
        """
        :return: the text contents of the given fileids, as a single string.
        """
        if fileids is None: fileids = self._fileids
        elif isinstance(fileids, compat.string_types): fileids = [fileids]
        return concat([self.open(f).read() for f in fileids])

    def _entry(self, tree):
        elts = []
        for lexelt in tree.findall('lexelt'):
            for inst in lexelt.findall('instance'):
                sense = inst[0].attrib['senseid']
                context = [(w.text, w.attrib['pos'])
                           for w in inst[1]]
                elts.append( (sense, context) )
        return elts


class SensevalCorpusView(StreamBackedCorpusView):
    def __init__(self, fileid, encoding):
        StreamBackedCorpusView.__init__(self, fileid, encoding=encoding)

        self._word_tokenizer = WhitespaceTokenizer()
        self._lexelt_starts = [0] # list of streampos
        self._lexelts = [None] # list of lexelt names

    def read_block(self, stream):
        # Decide which lexical element we're in.
        lexelt_num = bisect.bisect_right(self._lexelt_starts, stream.tell())-1
        lexelt = self._lexelts[lexelt_num]

        instance_lines = []
        in_instance = False
        i=0
        while True:
            line = stream.readline()
            i+=1
#           print(i,line.strip())
            if line == '':
#               print('empty',line)
                assert instance_lines == []
                return []

            # Start of a lexical element?
            if line.lstrip().startswith('<lexelt'):
                lexelt_num += 1
                m = re.search('item=("[^"]+"|\'[^\']+\')', line)
                assert m is not None # <lexelt> has no 'item=...'
                lexelt = m.group(1)[1:-1]
                if lexelt_num < len(self._lexelts):
                    assert lexelt == self._lexelts[lexelt_num]
                else:
                    self._lexelts.append(lexelt)
                    self._lexelt_starts.append(stream.tell())

            # Start of an instance?
            if line.lstrip().startswith('<instance'):
                assert instance_lines == []
                in_instance = True

            # Body of an instance?
            if in_instance:
                instance_lines.append(line)

            # End of an instance?
            if line.rstrip().endswith('</instance>'):  # for SemEval-2007
#           if line.lstrip().startswith('</instance'):
                xml_block = '\n'.join(instance_lines)
#               xml_block = _fixXML(xml_block)
                inst = ElementTree.fromstring(xml_block)
                return [self._parse_instance(inst, lexelt)]

    def _parse_instance(self, instance, lexelt):
        inst=''
        senses = []
        context = []
        position = None
        for child in instance:
            if child.tag == 'answer':
                senses.append(child.attrib['senseid'])
                inst=child.attrib['instance']
            elif child.tag=='context':pass
            elif child.tag=='postagging':
                for cword in child:
                    context.append((cword[0].text,cword.attrib['pos']))
            else:
                assert False, 'unexpected tag %s' % child.tag
        return SensevalInstance(lexelt, position, context, senses,inst)


from sys import argv

if __name__=='__main__':
    #print(SensevalCorpusReader(root='/usr/share/nltk_data/corpora/senseval',fileids=['hard.pos']).instances())
    for instance in SensevalCorpusReader(root='.',fileids=[argv[1]]).instances():#'/tmp/Chinese_train_pos.xml.utf8.Chinese_medicine']).instances():
        words=[w.strip() for w,tag in instance.context if w!=None]#,instance.senses,instance.word) #233['千', '寻', '铁锁', '沉', '江底', '，', '一', '片', '降', None, '出', '石头', '。']
        if words[-1] not in ['。','？','！']:words.append('。') #For parser
        print(instance.word,instance.senses,' '.join(words),sep='\t') #Cut -f 3 > Chinese_test_pos.xml.utf8.segmented.

