#!/usr/bin/env python
import string
from Bio import Medline,Entrez
import shutil
#from RNASeq.misc import pp
from jinja2 import Environment,FileSystemLoader,exceptions


templateDir = "templates"
env = Environment(loader=FileSystemLoader([templateDir]))

##########################
#Publication Information
##########################

pmIDs=['22991327',
'22197703',
'20348442',
'19784364',
'19257808',
'18814314',
'18657893',
'18004940',
'17916793',
'17114923',
'15469607',
'23222703',
'22383036',
'21890647',
'23401553',
'23623381',
'24107992',
'24304912',
'24381249',
'24393486',
'24463464',
'24714615',
'24997765',
'25556833',
'26034286',
'26430155',
'26694805',
'27296516',
'27479747',
'27525555',
]

pmIDs.sort(reverse=True)

Entrez.email="loyalgoff@gmail.com"
handle = Entrez.efetch(db="pubmed", id=pmIDs, rettype="medline",
                           retmode="text")

records = Medline.parse(handle)


################
#Pages
################

pages=[
        ('/', 'index', '','Home'),
        ('/', 'research', 'Experimental Biology','Research'),
        ('/', 'people', 'General','People'),
        ('/', 'publications', 'Experimental Biology', 'Publications'),
        #('/', 'courses', 'Teaching', 'Courses'),
        ('/', 'software', 'Computational Biology','Software'),
        ('/', 'contact', 'General','Contact'),
        #('/', 'about', 'General','About'),
        ('/', 'join', 'General','Join'),
        #('/', 'resources', 'General','Resources'),
        ('/', 'links', 'General','Links'),
        ('/', 'news', 'General', 'News')
]


#pp(list(records))

def pubs():
    template=env.get_template('pubs.html')
    outHandle = open(outFile,'w')
    print >>outHandle, template.render(records=list(records))

def renderPage(pageName,**kwargs):
    fname=pageName+'.html'
    template=env.get_template(fname)
    outHandle = open(fname,'w')
    print >>outHandle, template.render(**kwargs)

if __name__ == '__main__':
  for page in pages:
      try:
          if page[1]=='publications':
              renderPage(page[1],activePage=page[1],pages=pages,records=list(records))
          else:
              renderPage(page[1],activePage=page[1],pages=pages)
      except exceptions.TemplateNotFound:
          shutil.copy(templateDir+"/min.template",templateDir+"/"+page[1]+".html")
          renderPage(page[1],activePage=page[1],pages=pages)
