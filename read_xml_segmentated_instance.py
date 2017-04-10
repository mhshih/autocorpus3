from sys import argv
from xml.dom.minidom import parse

p=parse(open(argv[1]))#'Chinese_train_pos.xml.utf8'))

for lexelt in p.getElementsByTagName('lexelt'):
    item=lexelt.getAttribute('item')
    for instance in lexelt.getElementsByTagName('instance'):
#       print(item,end='\t')
        for token in instance.getElementsByTagName('token'):
            ChildNode=token.firstChild
            if ChildNode:#==None:
                if ChildNode.nodeValue=='．':print('，',end=' ') #avoid parser's sentence boundary symble
                else:print(ChildNode.nodeValue.strip(),end=' ')  
        if ChildNode.nodeValue.strip() != '。':print('。')       #keep parser parse on the right boundary
        else:print()
