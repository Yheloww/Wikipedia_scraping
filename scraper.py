import requests

import json

import bs4
from bs4 import BeautifulSoup

import re 

def get_leaders():
    #determining URLS 
    root_url = 'https://country-leaders.onrender.com'
    cookies_url = '/cookie/'
    country_url = '/countries/'
    leaders_url = '/leaders/'
    #creation of a session 
    s = requests.Session()
    #getting the cookies 
    req= s.get(root_url+cookies_url)
    cookies = req.cookies
    #getting the different countries
    countri = s.get( root_url+country_url, cookies=cookies)
    countries = countri.json()
    leaders_per_country = {}
    #creation of the final dictionary
    #looping trough each country to find the different leaders
    for country in countries: 
        leaders_req = s.get( root_url+leaders_url, cookies=cookies, params={ 'country' : country})
        #checking if the cookie is dead or not 
        if leaders_req.status_code == 403 :
            req= s.get(root_url+cookies_url)
            cookies = req.cookies
            leaders_req = s.get( root_url+leaders_url, cookies=cookies, params={ 'country' : country})
        leaders_jsons = leaders_req.json()
        leaders_per_country[country] = leaders_jsons
    #looping trough the different leaders to add the first_paragraph key in the dictionary
        for leader in leaders_jsons :
            wtf = leader['wikipedia_url']
            #using the function to retrieve the first paragraph of each page
            para = get_first_paragraph(wtf,s)
            leader["first_paragraph"] = para
    return leaders_per_country

#creation of a cache decorator
cache = {}
def hashable_cache(f):
    def inner(url, session):
        if url not in cache:
            cache[url] = f(url, session)
        return cache[url]
    return inner

@hashable_cache
#the function that's used to retrieve the first paragraph of a page in Wikipedia
def get_first_paragraph(url,session):
    response = session.get(url)
    okok = bs4.BeautifulSoup(response.text, "html.parser")
    for paragraph in okok.find_all('p'):
        #loop trough the paragraph and find the one were there's bold in the beginning
        if paragraph.find_all('b'):
            texted = paragraph.text
            #cleaning the output using regex yay :D
            cleaned = re.sub(r'\s*<[^>]*>\s*','',texted)
            cleaned_1 = re.sub(r'\[.*?\]','',cleaned)
            cleaned_2= re.sub(r'\(.*?\)','',cleaned_1)
            cleaned_3= re.sub(r'\n','',cleaned_2)

            return cleaned_3
#creating the final file with the content of the scraping
def save(content : dict, name: str) :
    leaders = f"./{name}.json"
    with open(leaders, 'w') as file:
        json.dump(content, file, indent=4)

final = get_leaders()
save(final, "leaders_countries")
