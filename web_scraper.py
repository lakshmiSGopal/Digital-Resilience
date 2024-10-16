#importing necessary libraries
from newspaper import Article, Config
import pandas as pd
import concurrent.futures
import time
import spacy
import numpy as np
import logging
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from functools import lru_cache
from urllib.parse import urlparse, parse_qs
import urllib.robotparser as r

# Configure global logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Caching geocode function to reduce repeated lookups
@lru_cache(maxsize=100)

# Define a function to check permission for scraping URL
def permission(url):
  """Check if scraping is allowed on the given URL by reading robots.txt.""" 
  # Extract domain and check robots.txt
  url = processing_url(url)
  parsed_url = urlparse(url)
  robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
  rp = r.RobotFileParser()
  rp.set_url(robots_url)
    
  try:
    rp.read()
    return rp.can_fetch("*", url)
  except Exception as e:
    logging.error(f"Error reading robots.txt for {robots_url}: {e}")
    return False
  
def processing_url(url):
  """ Processes a URL to extract the actual target URL if it's a Google redirect. """
  parsed_url = urlparse(url)
  domain = parsed_url.netloc.lower()
  if domain in ["www.google.com", "google.com"]:
        if parsed_url.path == "/url":
            query_params = parse_qs(parsed_url.query)
            target_url = query_params.get('q')
            if target_url:
                return target_url[0]
            else:
                return url
        else:
            return url
  else:
        return url # Non-Google URLs are returned as-is

# identifies location from news title
def title_location(data):
  nlptext = nlp(data) # Process the news title text
  loc = "None" # If no GPE found, set location as 'None'
  for nlpT in nlptext.ents:
    if nlpT.label_ == 'GPE': # Check if the entity is a place (GPE: Geopolitical Entity)
      loc = str(nlpT) # Extract the place name
      break  
  return loc

#identifies the latitude & longitude of the location extracted from title_location()
def geocode(location):
    geolocator = Nominatim(user_agent="digitalresilience")
    if location and location != 'None':
        try:
            location_obj = geolocator.geocode(location, timeout=10)
            if location_obj:
                return location_obj.latitude, location_obj.longitude
        except GeocoderTimedOut:
            pass
    return None, None

# Define a function to download and process the article
def get_article(url,retries = 3):
  processed_url = processing_url(url)
  if not permission(processed_url):
        logging.error(f"Permission denied for {processed_url} based on robots.txt.")
        return None

  # Determine the source
  source = urlparse(processed_url).netloc.lower()
    
  for attempt in range(retries): # Retry downloading the article up to 3 times
    try:
      config = Config()
      config.thread_count = 2  # for threading inside newspaper3k
      article = Article(processed_url, config=config)
      article.download()
      article.parse()

      # Extract location and geocode
      location = title_location(article.title)
      latitude, longitude = geocode(location)

      # Return article information
      return {
        'source': source,
        'title': article.title,
        'publish_date': str(article.publish_date),
        'location': location,
        'latitude': latitude,
        'longitude': longitude,
        'text': article.text,
        'images': list(article.images),
        'Videos': list(article.movies)
        }
    except Exception as e:
            logging.error(f"Error processing {processed_url} on attempt {attempt + 1}: {e}")
            time.sleep(min(2 ** attempt, 60))  # Exponential backoff with max delay of 60s

  logging.error(f"Failed to process {processed_url} after {retries} retries.")
  return None
 
def main(urls, output_file='wayanad_5.xlsx', max_workers=5):
    data = []
    # Create a ThreadPoolExecutor with a specified number of worker threads
    with concurrent.futures.ThreadPoolExecutor(max_workers) as executor:
        # Submit tasks to process each URL concurrently
        futures  = [executor.submit(get_article, url)for url in urls]
        # Iterate over the futures as they complete
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()  # Get the result of the task
                if result:  # If the result is valid (not None)
                    data.append(result)  # Append the result to the data list
            except Exception as e:
                logging.error(f"Error fetching article data: {e}")  # Log any errors that occur

    # Check if data is not empty before saving
    if data:
        # Create a pandas DataFrame from the collected data
        df = pd.DataFrame(data)
        # Optimize DataFrame creation and memory usage
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce', downcast='float')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce', downcast='float')

        # Save the DataFrame to an Excel file
        df.to_excel(output_file, index=False)
        print(f"Data successfully saved to {output_file}")
    else:
        logging.warning("No valid data was collected. Excel file not created.")

links=[]
f=open("wayanad[5th].txt",'r',encoding="utf8")
l = f.read()
f.close
links = l.split("\n")
main(links,'wayanad#1_.xlsx') 