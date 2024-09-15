import json
import csv
from scipy.stats import spearmanr

def clean_url(url):
    """Clean URLs based on provided conditions (remove scheme, www, trailing slashes, and query params)"""
    if url.startswith('http://'):
        url = url[7:]
    elif url.startswith('https://'):
        url = url[8:]
    
    if url.startswith('www.'):
        url = url[4:]
    
    if '/' in url:
        url = url.split('/')[0]
    
    return url

def load_json(file_path):
    """Load JSON file"""
    with open(file_path, 'r') as file:
        return json.load(file)

def calculate_spearman_rank(rank_google, rank_bing):
    # Number of matches (size of rank_google or rank_bing)
    n = len(rank_google)
    
    # Calculate d_i and d_i^2
    di_squared_sum = 0
    for i in range(n):
        di = rank_google[i] - rank_bing[i]
        di_squared_sum += di ** 2
    
    # Calculate the Spearman coefficient
    coefficient = 1 - (6 * di_squared_sum) / (n * (n**2 - 1))
    
    return coefficient


def compute_overlap_and_spearman(google_results, bing_results):
    """Compute overlap percentage and Spearman correlation coefficient for a single query"""
    google_cleaned = [clean_url(url) for url in google_results]
    bing_cleaned = [clean_url(url) for url in bing_results]
    
    overlap_count = 0
    ranks_google = []
    ranks_bing = []
    
    # Count overlap and record ranks
    for i, bing_url in enumerate(bing_cleaned):
        if bing_url in google_cleaned:
            overlap_count += 1
            ranks_google.append(google_cleaned.index(bing_url) + 1)
            ranks_bing.append(i + 1)

    # Compute percent overlap
    percent_overlap = (overlap_count / len(google_cleaned)) * 100

    # Compute Spearman correlation
    if len(ranks_google) > 1:
        # spearman_coefficient, _ = spearmanr(ranks_google, ranks_bing)
        spearman_coefficient = calculate_spearman_rank(ranks_google, ranks_bing)
        
    elif len(ranks_google) == 1:
        if ranks_google[0] == ranks_bing[0]:
            spearman_coefficient = 1
        else:
            spearman_coefficient = 0
    else:
        spearman_coefficient = 0
    
    return overlap_count, percent_overlap, spearman_coefficient

def generate_csv_report(google_data, bing_data, output_file):    
    queries = list(google_data.keys())
    total_overlap = 0
    total_percent_overlap = 0
    total_spearman = 0
    count = len(queries)
    
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['Query', 'Number of Overlapping Results', 'Percent Overlap', 'Spearman Coefficient']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for i, query in enumerate(queries):
            google_results = google_data[query]
            bing_results = bing_data.get(query, [])
            
            overlap_count, percent_overlap, spearman_coefficient = compute_overlap_and_spearman(google_results, bing_results)
            
            total_overlap += overlap_count
            total_percent_overlap += percent_overlap
            total_spearman += spearman_coefficient
            
            writer.writerow({
                'Query': f'Query {i + 1}',
                'Number of Overlapping Results': overlap_count,
                'Percent Overlap': percent_overlap,
                'Spearman Coefficient': spearman_coefficient
            })
        
        # Averages
        writer.writerow({
            'Query': 'Averages',
            'Number of Overlapping Results': total_overlap / count,
            'Percent Overlap': total_percent_overlap / count,
            'Spearman Coefficient': total_spearman / count
        })

def write_summary_txt(average_overlap, average_spearman, output_file):    
    with open(output_file, 'w') as txtfile:
        txtfile.write(f"Average percent overlap: {average_overlap:.2f}%\n")
        txtfile.write(f"Average Spearman coefficient: {average_spearman:.2f}\n")
        if average_spearman > 0:
            txtfile.write("The search engine performed similarly to Google based on the rankings.\n")
        else:
            txtfile.write("The search engine performed worse than Google based on the rankings.\n")

# Load Google and Bing JSON files
google_data = load_json('Google.json')
bing_data = load_json('Bing.json')

# Generate CSV report
generate_csv_report(google_data, bing_data, 'result.csv')

# Compute averages
with open('result.csv', 'r') as file:
    reader = csv.DictReader(file)
    overlaps = []
    spearmans = []
    for row in reader:
        if row['Query'] != 'Averages':
            overlaps.append(float(row['Percent Overlap']))
            spearmans.append(float(row['Spearman Coefficient']))

average_overlap = sum(overlaps) / len(overlaps)
average_spearman = sum(spearmans) / len(spearmans)

# Write summary TXT file
write_summary_txt(average_overlap, average_spearman, 'result.txt')
