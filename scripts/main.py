#!/usr/bin/env python
import string
from Bio import Medline,Entrez
import shutil
#from RNASeq.misc import pp
from jinja2 import Environment,FileSystemLoader,exceptions
import urllib.request as request
import json
import re

templateDir = "templates"
env = Environment(loader=FileSystemLoader([templateDir]))

##########################
#Publication Information
##########################
### Fetch publications
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
'27801893',
'27999180',
'28821643',
'28930659',
'29320739',
'29499164',
'30143323',
'30188322',
'30866806',
'30988181',
'31128945',
'31121116',
'31337651',
'32829096',
'32386599',
'32243843',
'32167521',
'31843893',
'31581148',
'31503409',
'31465303',
'33084572',
]

pmIDs.sort(reverse=True)

print(f"Fetching {len(pmIDs)} publication records from Entrez...")
Entrez.email="loyalgoff@gmail.com"
handle = Entrez.efetch(db="pubmed", id=pmIDs, rettype="medline",
                           retmode="text")

records = Medline.parse(handle)
print("\tDone")

##########################
#Preprint Information
##########################
### Fetch Preprints
preprintIDs = [
    '157149',
    '148049',
    '196394',
    '196915',
    '378950',
    '395004',
    '479287',
    '447557',
    '484410',
    '726547',
    '779694',
    '2020.03.13.990549',
    '2020.07.23.218586',
    '2020.08.25.262832',
]

preprintIDs = reversed(preprintIDs)

def fetchBioRxiv(preprintID):
    biorxiv_api_url = f'https://api.biorxiv.org/details/biorxiv/10.1101/{preprintID}'
    response = request.urlopen(biorxiv_api_url)
    data = json.loads(response.read())
    return(data)

#print(fetchBioRxiv(preprintIDs[0]))
print("Fetching Preprints from BioRxiv...")
preprints = [fetchBioRxiv(id)['collection'][0] for id in preprintIDs]
print(f"\t{len(preprints)} found")
#print(preprints[-1]

################
#Pages
################

pages=[
        ('/', 'index', '','Home'),
        #('/', 'research', 'Experimental Biology','Research'),
        ('/', 'people', 'General','People'),
        ('/', 'publications', 'Experimental Biology', 'Publications'),
        ('/', 'preprints', 'Experimental Biology', 'Preprints'),
        ('/', 'teaching', 'Teaching', 'Teaching'),
        ('/', 'software', 'Computational Biology','Software'),
        ('/', 'datasets', 'Computational Biology', 'datasets'),
        ('/', 'contact', 'General','Contact'),
        #('/', 'about', 'General','About'),
        ('/', 'join', 'General','Join'),
        #('/', 'resources', 'General','Resources'),
        #('/', 'links', 'General','Links'),
        #('/', 'news', 'General', 'News')
        ('/', 'blog', 'General', 'Blog'),
]

#pp(list(records))

def pubs():
    template=env.get_template('pubs.html')
    outHandle = open(outFile,'w')
    print >>outHandle, template.render(records=list(records))

#def preprints():
#    template=env.get_template('preprints.html')

def renderPage(pageName,**kwargs):
    fname=pageName+'.html'
    template=env.get_template(fname)
    outHandle = open(fname,'w')
    #print >>outHandle, template.render(**kwargs)
    print(template.render(**kwargs),file=outHandle)

def nameBoldPubs(string):
    return(re.sub('Goff,? L\.?[A]?\.?,?','<span class="font-weight-bold" style="font-size: 1.0rem"><u>Goff LA</u></span>,',string))

env.filters['nameBoldPubs'] = nameBoldPubs

if __name__ == '__main__':
  for page in pages:
      try:
          if page[1]=='publications':
              renderPage(page[1],activePage=page[1],pages=pages,records=list(records))
          elif page[1]=='preprints':
              renderPage(page[1],activePage=page[1],pages=pages,preprints=preprints)
          else:
              renderPage(page[1],activePage=page[1],pages=pages)
      except exceptions.TemplateNotFound:
          print("No good template for %s" % (page[1]))
          #shutil.copy(templateDir+"/min.template",templateDir+"/"+page[1]+".html")
          #renderPage(page[1],activePage=page[1],pages=pages)
