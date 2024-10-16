import requests
from bs4 import BeautifulSoup as bs4
from urllib.parse import urljoin, urlparse, parse_qs
import time
import pandas as pd

def check(url):
    #Checks if a given URL contains keywords or HTML elements that suggest it is a news article
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        return False

    soup = bs4(response.content, "html.parser")
    
    keywords = ["news", "article", "report", "journalism"]
    
    meta_tags = soup.find_all('meta')
    for meta in meta_tags:
        if meta.get('name') == 'keywords' or meta.get('property') == 'og:type':
            content = meta.get('content', '').lower()
            if any(keyword in content for keyword in keywords):
                return True
    
    sections = ['h1', 'h2', 'time', 'article', 'header', 'footer']
    if any(soup.find(section) for section in sections):
        return True
    
    content = soup.get_text().lower()
    words = ["news", "breaking news", "latest news", "reporting by", "reported by", "journalist"]
    if any(phrase in content for phrase in words):
        return True
    
    return False

def is_valid_google_redirect(url):
    #Determines whether the URL is a redirect or a valid URL
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return "url" in query_params and "q" in query_params

def is_google_section(url):
    #Determines whether a URL is part of a non-news section on Google (shopping or other non-news categories)
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
  
    if parsed_url.netloc == 'www.google.com':
        # Check for news specific parameter
        if "tbm" in query_params and query_params["tbm"][0] == "nws":
            return False  # Not a non-news section if tbm=nws
        # Check for other unwanted parameters
        if any(param in query_params for param in ['tbm', 'tbs', 'source']):
            return True  
    return False

def save_links_to_file(links, filename="found_links.txt"):
    #Saves a list of URLs to a text file
    formatted_links = [f"'{link}'" for link in links]
    with open(filename, "w", encoding="utf-8") as file:
        file.write(f"[{', '.join(formatted_links)}]")
    print(f"Found links saved to {filename}")

def crawl(max_links):
    #Crawls URLs starting from an initial URL and collects up to `max_links` news article URLs, saves URLs to an excel file, calculates hit ratio and time taken to execute the program.
    found_links = []
    pages_crawled = 0
    success_crawled = 0    

    while success_crawled < max_links and links_to_visit:
        current_link = links_to_visit.pop(0)
        if current_link in visited_links:
            continue
        
        visited_links.add(current_link)
        
        try:
            response = requests.get(current_link, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error accessing {current_link}: {e}")
            continue
        
        soup = bs4(response.content, "html.parser")
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            full_url = urljoin(current_link, href)
            lower_url = full_url.lower()
            pages_crawled +=1
            
            parsed_url = urlparse(full_url)
            if parsed_url.scheme not in ['http', 'https']:
                continue
            if is_google_section(full_url):
                continue
            if is_valid_google_redirect(full_url):
                full_url = parse_qs(parsed_url.query)['url'][0]
            if any(keyword in lower_url for keyword in keywords):
                if full_url not in visited_links and full_url not in links_to_visit:
                    if check(full_url) and not is_google_section(full_url):
                        if len(found_links) < max_links:
                            if 'https://www.google.com/search?' in full_url or '/topic/' in full_url or '/about/' in full_url or '/home/' in full_url or '/tags/' in full_url or '/tag/' in full_url or '/section/' in full_url :
                                links_to_visit.append(full_url)
                            elif full_url == 'https://www.google.com/search?q=wayanad+landslide+news&sca_esv=12268370a69439db&ie=UTF-8&tbm=shop&source=lnms&ved=1t:200713&ictx=111':
                                continue
                            elif full_url == 'https://www.google.com/url?q=https://accounts.google.com/ServiceLogin%3Fcontinue%3Dhttps://www.google.com/search%253Fq%253Dwayanad%252Blandslide%252Bnews%2526sca_esv%253D12268370a69439db%2526sca_upv%253D1%2526gbv%253D2%2526ie%253DUTF-8%2526ei%253DG02rZp_3HI2P4-EP96Oz6AU%2526start%253D10%2526sa%253DN%26hl%3Den&opi=89978449&sa=U&ved=0ahUKEwjw7NKlttOHAxXtrpUCHfZ5AvA4ChDGzwIISQ&usg=AOvVaw0zSVU-Mq9jGNF4qtkjLZR' or 'Service' in full_url or 'login' in full_url or 'ServiceLogin' in full_url or 'servicelogin' in full_url or 'Login' in full_url:
                                continue
                            elif 'signup' in full_url or 'sign in' in full_url or 'https://www.google.com/url?q=https://accounts.google.com/ServiceLogin' in full_url:
                                continue
                            elif 'https://www.google.com/url?q=/search' in full_url or 'https://web.whatsapp.com' in full_url or 'https://www.facebook.com' in full_url or 'https://api.whatsapp.com' in full_url or '/news/' in full_url or 'https://www.linkedin.com' in full_url or 'https://www.instagram.com' in full_url or 'youtube.com' in full_url:
                                continue
                            elif 'election' in full_url or 'poll' in full_url:
                                continue

                            else:
                                links_to_visit.append(full_url)
                                found_links.append(full_url)
                                success_crawled += 1



        #print("Processed:", current_link)
        #print(success_crawled)

    #hit ratio = success_crawled/pages_crawled    
    print("----------------------crawling done----------------------")
    print("Total pages crawled : ",pages_crawled)
    print("Hits : ",success_crawled)
    print("Hit Ratio : ",success_crawled/pages_crawled)
    print(found_links)

    '''df = pd.DataFrame(found_links, columns=["Links"])
    df.to_excel("wayanad_news8.xlsx", index=False)'''

    '''save_links_to_file(found_links, "crawled_links_9.txt")'''

visited_links = set()    
links_to_visit = []
x = input("Link to crawl : ")
links_to_visit.append(x)
    
y = input("Enter keywords separated by commas: ")
keywords = [kw.strip().lower() for kw in y.split(",")]
    
z = int(input("How many links do you want ? : "))
if __name__ == "__main__":
    start_time = time.time()
    
    crawl(z)
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    elapsed_minutes = elapsed_time / 60
    print(f"Total execution time: {elapsed_minutes:.2f} minutes")

    

