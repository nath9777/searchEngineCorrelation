import json
import base64
import requests
import urllib.parse

from bs4 import BeautifulSoup
from random import randint
from time import sleep

USER_AGENT = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.2739.79'}


class SearchEngine:
    @staticmethod
    def search(query, use_sleep=True):
        """Searches DuckDuckGo with the provided query and returns the top 10 results."""
        if use_sleep:
            sleep(randint(5, 7))  # To avoid IP block due to rapid requests
        temp_query = '+'.join(query.split())  # Format query
        
        url = f'https://www.bing.com/search/?q={temp_query}'
        print("URL: " , url)
        
        # headers = get_random_user_agent()
        response = requests.get(url, headers=USER_AGENT)
        soup = BeautifulSoup(response.text, "html.parser")

        results = SearchEngine.scrape_search_result(soup)
        return results

    @staticmethod
    def extract_actual_url(tracking_url):
        """Extract the actual URL from the tracking URL."""
        parsed_url = urllib.parse.urlparse(tracking_url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        if 'u' in query_params:
            actual_url_base64 = query_params['u'][0]
            if actual_url_base64.startswith('a1'):
                actual_url_base64 = actual_url_base64[2:]
            
            # Add padding if necessary
            padding = 4 - (len(actual_url_base64) % 4)
            if padding:
                actual_url_base64 += '=' * padding
            
            try:
                decoded_u = base64.urlsafe_b64decode(actual_url_base64).decode('utf-8')
                print(f"Decoded URL: {decoded_u}")
                
                # Check if the URL is an ad link
                if SearchEngine.is_ad_url(decoded_u):
                    print('Ad link skipped.')
                    return None
                return decoded_u
            except Exception as e:
                print(f"Error decoding URL: {e}")
                return tracking_url
        else:
            return tracking_url

    @staticmethod
    def is_ad_url(url):
        """Check if the URL is an ad link."""
        ad_patterns = [
            'youtube.com/watch',
            'bit.ly/',
            'goo.gl/',
            'shorturl.com/'
        ]
        return any(pattern in url for pattern in ad_patterns)

    # Update the scrape_search_result function
    @staticmethod
    def scrape_search_result(soup):
        """Extracts the top 10 URLs from Bing search result page."""
        raw_results = soup.find_all("li", attrs={"class": "b_algo"})[:20]
        print("suze: ",len(raw_results))
        links = []
        for result in raw_results:
            if len(links) == 10:
                break  # Stop when we have 10 valid URLs
            a_tag = result.find('a')
            if a_tag and a_tag.get('href'):
                tracking_url = a_tag.get('href')
                actual_url = SearchEngine.extract_actual_url(tracking_url)
                if actual_url:
                    links.append(actual_url)
        
        return links


def process_queries(file_path):
    """Reads a file containing queries, fetches the top 10 results for each, and saves them in a JSON file."""
    query_results = {}
    with open(file_path, 'r') as file:
        queries = file.readlines()
    
    for query in queries:
        query = query.strip()  # Clean query
        results = SearchEngine.search(query)
        query_results[query] = results
        
    
    with open('Bing.json', 'w') as output_file:
        json.dump(query_results, output_file, indent=4)
        print("Completed!")

if __name__ == "__main__":
    process_queries('100QueriesSet1.txt')

