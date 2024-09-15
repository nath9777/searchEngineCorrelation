# searchEngineCorrelation
This project compares web scraping results for Bing.com and Google.com, for a set of 100 queries, using spearman's rank correlation coefficient to determine correlation between the 2 search engines, using google as benchmark.


Flow:
1. We have a set of 100 queries in 100QueriesSet1.txt.
2. Google.json contains at most 10 urls scrapped for each of the 100 queries on google.com.
3. scrape.py is run to scrape bing for the same 100 queries, and results are stored in Bing.json
   a. We may not have 10 urls for each query, we are skipping over advertisements. (bit.ly links, youtube.com links etc)
   b. One the url's are scrapped using beauftiful soup, we must decode a 'u' parameter from the returned url, which is base-64 encoded. That will give us 
   the actual url
4. spearman.py is run to calcualte spearman's rank correlation coefficient for each of the 100 queries, between Google and Bing.
5. We store the reults in a csv file, while also calcualting avergae % overlap and average spearman's coefficient.
-> You can find the analysis of results in result.txt