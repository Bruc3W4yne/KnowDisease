# Using BioC api, see https://www.ncbi.nlm.nih.gov/research/bionlp/APIs/BioC-PMC/

import requests
import os
import re

min_size = 10_000
err_regex = re.compile(r"<error>", re.I)

def save_xml(pmid, folder = "./downloaded_papers", encoding="ascii", source = "pmcoa"):
    
    filename = f"{pmid}_{encoding}_{source}.xml"
    if filename in os.listdir(folder): 
        return 1
    
    url = f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/{source}.cgi/BioC_xml/{pmid}/{encoding}"

    try:
        page = requests.get(url)
        page.raise_for_status()
        text = page.text

        if (len(text) < min_size) or err_regex.search(text):
            print(f"{pmid} - no full text available ({len(text)} bytes), skipping...")
            return 0
        
        print(pmid, len(text))
        with open(os.path.join(folder, filename), "w") as f:
            f.write(text)
        return 1
    
    except Exception as e:
        print(f"Error fetching {pmid}: {e}")
        return 0

if __name__ == "__main__":
    for pmid in [33495476, 35810190, 33789117, 35368039]: # nhrf examples
        save_xml(pmid)