import os
import time
import argparse
from Bio import Entrez
from .xml_fetcher import save_xml

SUBHEADINGS = [
    "etiology[sh]", "pathology[sh]", "genetics[sh]", "complications[sh]",
    "diagnosis[sh]", "therapy[sh]", "pathogenesis[sh]", "physiopathology[sh]"
]

def build_query(disease, full_text=True, pubtypes=None):
    """Build PubMed query for disease theories."""
    parts = [
        f"{disease}[majr]",
        f"({' OR '.join(SUBHEADINGS)})",
        "(pathogenesis OR mechanism OR pathway OR model OR theory OR framework OR biomarker OR prognosis OR outcome)"
    ]
    
    if pubtypes:
        parts.append(f"({' OR '.join(f'{pt}[pt]' for pt in pubtypes)})")
    
    if full_text:
        parts.append("(free full text[Filter])")
    
    return " AND ".join(parts)

def fetch_papers(disease, count=10, out_dir="backend/data/downloaded_papers"):
    os.makedirs(out_dir, exist_ok=True)
    
    # Build query
    query = build_query(
        disease,
        full_text=True,
        pubtypes=["Review", "Systematic Review"]
    )
    print(f"Query: {query}")
    
    # Search for a large batch
    handle = Entrez.esearch(db="pubmed", term=query, retmax=100, sort="relevance")
    pmids = Entrez.read(handle)["IdList"]
    handle.close()
    print(f"Found {len(pmids)} PMIDs")
    
    if not pmids:
        print("No papers found")
        return []
    
    # Download until we have given count papers
    downloaded = []
    for pmid in pmids:
        if len(downloaded) >= count:
            break
            
        fname = os.path.join(out_dir, f"{pmid}_ascii_pmcoa.xml")
        
        # Skip if already exists
        if os.path.exists(fname):
            downloaded.append(pmid)
            print(f"[{len(downloaded)}/{count}] {pmid} - already exists")
            continue
        
        # Try to download
        if save_xml(pmid, folder=out_dir, source="pmcoa") == 1:
            downloaded.append(pmid)
            print(f"[{len(downloaded)}/{count}] {pmid} - downloaded")
        
        time.sleep(0.5)
        
    print(f"\nSuccessfully downloaded {len(downloaded)} papers")
    return downloaded

def main():
    parser = argparse.ArgumentParser(description="Fetch disease theory papers from PubMed")
    parser.add_argument("disease", help="Disease name to search for")
    parser.add_argument("-n", "--count", type=int, default=10, help="Number of papers to download")
    parser.add_argument("-o", "--output", default="backend/data/downloaded_papers", help="Output directory")
    parser.add_argument("-e", "--email", help="Entrez email (or set ENTREZ_EMAIL env var)")
    
    args = parser.parse_args()
    
    # Set Entrez email
    email = args.email or os.environ.get("ENTREZ_EMAIL")
    if not email:
        print("Error: Email required. Use -e or set ENTREZ_EMAIL env var")
        return
    Entrez.email = email
    
    # Fetch papers
    pmids = fetch_papers(args.disease, args.count, args.output)
    
    if len(pmids) < args.count:
        print(f"Warning: Only found {len(pmids)} downloadable papers out of {args.count} requested")

if __name__ == "__main__":
    main()