#!/usr/bin/env python
import string
from Bio import Medline,Entrez
import shutil
#from RNASeq.misc import pp
from jinja2 import Environment,FileSystemLoader,exceptions
import urllib.request as request
import json
import re
import sys

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
'33113347',
'33277430',
'33446502', 
'34266896',
'35148175',
'35101061',
'35263579', # Potter mosquito AgOr2
'35463747', # MacFarlane Smad3 heart
'35998637', # Kolodkin Tbx5 Direction selectivity
'37316665', # Psychadelics reopen the social critical period
'37585461', # HSCR PNAS paper
'37812717', # Sjogren's syndrome
'37989764', # CoGAPS Notebooks
'37885016', # RNA velocity Genome Biology Paper
'38108810', # eLife MENS paper
'38969603', # CFTR paper with Cutting Lab
'39271675', # BRN1/2 paper with Uli Nat Comm.
'39495936', # RGC paper with Kolodkin lab
'40164771', # Bergles OPC scRNA-Seq
'40457480', # MNSF paper with Kasper
'40844876', # L6 Consensus cell types (w/ Brown lab)
]

pmIDs.sort(reverse=True)

print(f"Fetching {len(pmIDs)} publication records from Entrez...")
Entrez.email="loyalgoff@gmail.com"
handle = Entrez.efetch(db="pubmed", id=pmIDs, rettype="medline",
                           retmode="text")

records = Medline.parse(handle)
print("\tDone")

##########Hannah################
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
    '2020.12.09.417931',
    '2021.04.06.438463',
    '2021.08.25.457650',
    '2021.12.27.473694', # Lindsay Hayes
    '2021.12.28.474390', # HSCR Manuscript
    '2022.10.07.511381', # Pantr2 study
    '2022.06.19.494717', # RNA Velocity Study
    '2022.07.09.499398', # Genevieve GenePattern Notebooks
    '2023.11.18.567662', # Sema6a with A.Kolodkin
    '2023.11.02.565322', # Uli Brn1/2
    '2024.07.01.599554', # mNSF
    '2023.01.28.526051', # Fovea preprint from Johnston lab
    '2024.10.27.620502', # Bergles OPC preprint
    '2024.11.04.621933',
    '2024.07.01.599554',
    
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
        ('/', 'lab_resources', 'General', 'Lab Resources'),
        ('/', 'octopus', 'General', 'Octopus Genome'),
        ('/', 'octopus_genome', 'General', 'Octopus Genome'),
]

#pp(list(records))

# def pubs():
#     template=env.get_template('pubs.html')
#     outHandle = open(outFile,'w')
#     print(template.render(records=list(records)),file=outHandle)

#def preprints():
#    template=env.get_template('preprints.html')

def renderPage(pageName,**kwargs):
    fname=pageName+'.html'
    template=env.get_template(fname)
    outHandle = open(fname,'w')
    #print >>outHandle, template.render(**kwargs)
    print(template.render(**kwargs),file=outHandle)

def nameBoldPubs(string):
    return(re.sub('Goff,? L\\.? ?[A]?\\.?,?','<span class="font-weight-bold" style="font-size: 1.0rem"><u>Goff LA</u></span>,',string))

env.filters['nameBoldPubs'] = nameBoldPubs

def split_doi(string):
    if(' [pii] ' in string):
        return string.split(" [pii] ")[1]
    else:
        return(string)

env.filters['split_doi'] = split_doi

def biorxiv_logo(string):
    if string == 'biorxiv':
        return 'bio<span style="color: red">R</span><sub><em>&Chi;</em></sub>iv'
    else:
        return string

env.filters['biorxiv_logo'] = biorxiv_logo

if __name__ == '__main__':
#   if sys.argv[1] == '-v':
#       verbose=True
#  if verbose:
#      #pp(list(records))
#  print(next(records).keys())
  for page in pages:
      try:
          if page[1]=='publications':
              renderPage(page[1],activePage=page[1],pages=pages,records=list(records))
          elif page[1]=='preprints':
              try:
                  renderPage(page[1],activePage=page[1],pages=pages,preprints=preprints)
              except:
                  print("Could not update preprints page")
          else:
              renderPage(page[1],activePage=page[1],pages=pages)
      except exceptions.TemplateNotFound:
          print("No good template for %s" % (page[1]))
          #shutil.copy(templateDir+"/min.template",templateDir+"/"+page[1]+".html")
          #renderPage(page[1],activePage=page[1],pages=pages)
