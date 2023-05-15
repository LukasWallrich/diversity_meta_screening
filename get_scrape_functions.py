from pybliometrics.scopus import AbstractRetrieval
from pybliometrics.scopus import CitationOverview
from pybliometrics.scopus import ScopusSearch
from pybliometrics.scopus.exception import Scopus404Error
import pandas as pd

def get_scopus_abstract(ui, id_type="doi"):
  try:
    ab = AbstractRetrieval(ui, id_type = id_type, key = r.scopus_key)
    return [ab.abstract, ab.description]
  except Scopus404Error:
    print("Abstract for " + ui + " not found")
    return ["", ""]

def get_scopus_references(ui, id_type="doi"):
  refs = []
  try:
    ab = AbstractRetrieval(ui, id_type = id_type, view = "REF", startref = 0, refresh = True, key = r.scopus_key)
  except Scopus404Error:
    print("References for " + ui + " not found in Scopus")
    return pd.DataFrame([])
  
  refs.append(ab.references)
   
  if ab.refcount > 40:
     for i in range(41, ab.refcount, 40):
       ab = AbstractRetrieval(ui, view = "REF", startref = i, refcount = min(40, ab.refcount - i), refresh = True)
       refs.append(ab.references)
  
  return pd.DataFrame(sum(refs,[]))

def get_scopus_citing_works(ui, id_type="doi", start = 1700):
  try:
    if id_type == "doi":
      ui = ScopusSearch("DOI("+ ui + ")").results[0].eid
  
    res = ScopusSearch("refeid(" + ui + ")")
    return pd.DataFrame(res.results)  
  except:
    print("References for " + ui + " not found in Scopus")
    return pd.DataFrame([])
  

####Create this to test API access####


def get_scholar_results(q, max_results, serp_key, start = 0, lang = None):
  from serpapi import GoogleSearch
  
  params = {
    "engine": "google_scholar",
    "q": q,
    "api_key": serp_key,
    "num": 20,
 #   "as_vis": 1,
    "start": start
  }
  
  if lang is not None:
    params["lr"] = "lang_" + lang
  
  # as_vis can exclude 'citations' - are of very little use without links or details
  
  max_results = int(max_results)
  all_results = []
  
  params["start"] = int(start)
  search = GoogleSearch(params)
  results = search.get_dict()
  tot = int(results["search_information"]["total_results"])
  print("Total results found: " + str(tot), flush = True)
  all_results += results['organic_results']
  
  for i in range(start + 20, min(tot, max_results + start) - 1, 20): 
    params["start"] = i
    search = GoogleSearch(params)
    results = search.get_dict()
    
    if not "organic_results" in results:
      if "error" in results:
        print("Error occured: " + results['error'], flush = True)
      else:
         print("No results returned - attempting to continue", flush = True)
      results['organic_results'] = []
      
    all_results += results['organic_results']
  
  return pd.DataFrame(all_results)

def parse_pdf_refs(file):
  import requests
  GROBID_URL = 'https://cloud.science-miner.com/grobid'
  url = '%s/api/processReferences' % GROBID_URL
  xml = requests.post(url, files={'input': open(file, 'rb')}, headers = {"Accept": "application/x-bibtex"}, data = {"consolidateCitations": "1"})
  return xml.text
