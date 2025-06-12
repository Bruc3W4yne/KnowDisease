import os
import re
import xml.etree.ElementTree as ET

exclude_sections = {
    "REF", "REFERENCE", "REFERENCES", "BIBLIO", "ACK", "FIG", "TABLE", "SUPPL",
    "SUPPLEMENT", "AUTHOR_NOTES", "LICENSE", "GLOSSARY", "AUTH_CONT", "COMP_INT", "FRONT",
    "FIG_CAPTION", "TABLE_FOOTNOTE", "TABLE_CAPTION", "ACK_FUND", "ABBR", "FOOTNOTE",
    "CONCLUSION", "CONCLUSIONS"
}

def _infon(p, key):
    for inf in p.findall("infon"):
        if inf.get("key") == key:
            return (inf.text or "").strip()
    return ""

def parse_xml(xml_path):
    if not os.path.exists(xml_path):
        return None
    try:
        root = ET.parse(xml_path).getroot()
    except ET.ParseError:
        return None
    
    document = root.find("document")
    if document is None:
        return None
    
    metadata = {
        "title": None,
        "authors": [],
        "journal": None,
        "year": None,
        "doi": None,
        "pmid": None,
        "abstract": None
    }
    
    text_parts = []
    
    for passage in document.findall("passage"):
        passage_type = _infon(passage, "type")
        passage_type_upper = passage_type.upper()
        section_type = _infon(passage, "section_type").upper()
        text_content = (passage.findtext("text") or "").strip()
        
        if passage_type == "front":
            metadata["title"] = text_content
            metadata["doi"] = _infon(passage, "article-id_doi")
            metadata["pmid"] = _infon(passage, "article-id_pmid")
            metadata["year"] = _infon(passage, "year")
            metadata["journal"] = _infon(passage, "journal")
            
            for infon in passage.findall("infon"):
                key = infon.get("key", "")
                if key.startswith("name_"):
                    author_text = (infon.text or "").strip()
                    if author_text:
                        parts = author_text.split(";")
                        author_dict = {}
                        for part in parts:
                            if ":" in part:
                                k, v = part.split(":", 1)
                                author_dict[k] = v
                        if "surname" in author_dict:
                            metadata["authors"].append(author_dict)
        
        elif passage_type == "abstract":
            metadata["abstract"] = text_content
            if text_content:
                text_parts.append("# ABSTRACT")
                text_parts.append(text_content)
        
        elif passage_type_upper not in exclude_sections and section_type not in exclude_sections:
            if not text_content:
                continue
                
            if passage_type_upper.startswith("TITLE"):
                level_match = re.search(r"TITLE[_\s]*([0-9]+)", passage_type, re.IGNORECASE)
                level = int(level_match.group(1)) if level_match else 1
                if level <= 2:
                    text_parts.append("#" * level + " " + text_content.upper())
                else:
                    text_parts.append(text_content.upper())
            else:
                text_parts.append(text_content)
    
    return {
        "metadata": metadata,
        "text": "\n\n".join(text_parts) if text_parts else None
    }

def extract_metadata(xml_path):
    result = parse_xml(xml_path)
    return result["metadata"] if result else None

def load_xml(xml_path):
    result = parse_xml(xml_path)
    return result["text"] if result else None

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("xml")
    ap.add_argument("--print-output", action="store_true")
    args = ap.parse_args()
    txt = load_xml(args.xml)
    if txt and args.print_output:
        print(txt)