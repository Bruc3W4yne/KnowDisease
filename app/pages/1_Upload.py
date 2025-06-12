import os
import tempfile
from pathlib import Path

import streamlit as st
from Bio import Entrez

from utils.backend_init import get_pipeline, get_graph_builder
from backend.data.paper_fetcher import fetch_papers
from backend.data.xml_loader import extract_metadata

st.set_page_config(layout="wide", page_title="Upload Article")

Entrez.email = os.environ.get("ENTREZ_EMAIL", "isak.w.midtvedt@gmail.com")
pipeline = get_pipeline()
graph_builder = get_graph_builder()

st.session_state.setdefault("search_results", [])
st.session_state.setdefault("selected_paper", None)

st.title("Article Upload")
st.markdown("Search for biomedical articles by disease or upload your own file.")
st.write("---")

col1, _, col2 = st.columns([0.45, 0.1, 0.45])

with col1:
    tab1, tab2 = st.tabs(["Search Papers", "Upload File"])
    
    with tab1:
        st.markdown("**Search by Disease**")
        disease_col, search_col = st.columns([3, 1])
        with disease_col:
            disease = st.text_input("Disease_label", placeholder="e.g., Diabetes, Melanoma", label_visibility="collapsed")
        with search_col:
            search_clicked = st.button("Search", use_container_width=True)
        
        if search_clicked and disease:
            with st.spinner("Searching and downloading papers..."):
                try:
                    pmids = fetch_papers(disease, count=10)
                    if pmids:
                        st.session_state.search_results = pmids
                        st.success(f"Found {len(pmids)} papers with full text")
                    else:
                        st.warning("No papers with full text found")
                except Exception as e:
                    st.error(f"Search failed: {str(e)}")
        
        if st.session_state.search_results:
            papers = []
            for pmid in st.session_state.search_results:
                xml_path = str(Path("backend/data/downloaded_papers") / f"{pmid}_ascii_pmcoa.xml")
                metadata = extract_metadata(xml_path) or {}
                title = f"{metadata.get('title', f'PMID: {pmid}')[:80]}...{f' ({year})' if (year := metadata.get('year')) else ''}"
                papers.append((pmid, title, metadata, xml_path))
            
            selected_idx = st.selectbox(
                "Select a Paper",
                range(len(papers)),
                format_func=lambda x: papers[x][1]
            )
            
            if selected_idx is not None:
                st.session_state.selected_paper = papers[selected_idx]
    
    with tab2:
        uploaded_file = st.file_uploader(
            "Upload PubMed XML file",
            type=["xml"]
        )
        
        if uploaded_file:
            temp_file = tempfile.NamedTemporaryFile(suffix='.xml', delete=False)
            temp_file.write(uploaded_file.getvalue())
            temp_file.close()
            
            metadata = extract_metadata(temp_file.name) or {}
            title = f"{metadata.get('title', uploaded_file.name)[:80]}...{f' ({year})' if (year := metadata.get('year')) else ''}"
            
            st.session_state.selected_paper = ("upload", title, metadata, temp_file.name)
            st.success(f"File '{uploaded_file.name}' ready to process")
    
    if st.session_state.selected_paper:
        progress_col, btn_col = st.columns([3, 1])
        with btn_col:
            run_clicked = st.button("Run Extraction", type="primary", use_container_width=True)
        
        if run_clicked:
            with progress_col:
                progress = st.progress(0, text="Processing...")
            
            try:
                paper_id, display, metadata, source = st.session_state.selected_paper
                
                # source is always a file path now
                file_path = source
                
                result_obj, _ = pipeline.process_document(
                    file_path, 
                    progress_callback=lambda v, text: progress.progress(max(0.0, min(1.0, v)), text=text)
                )
                
                result_dict = result_obj.model_dump() if hasattr(result_obj, "model_dump") else result_obj.dict()
                
                graph_paper_id = paper_id if paper_id != "upload" else Path(display).stem
                graph_builder.populate_graph_from_form(
                    result_dict, 
                    graph_paper_id,
                    getattr(pipeline, "last_evidence", {}),
                    getattr(pipeline, "last_reasoning", {})
                )
                
                progress.progress(1.0, text="Complete!")
                progress.empty()
                st.success(f"Successfully processed paper!")
                
                # Clean up temp file for uploads
                if paper_id == "upload" and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass
                    
            except Exception as e:
                progress.empty()
                st.error(f"Processing failed. {str(e)}")

with col2:
    st.subheader("Metadata Preview")
    
    if st.session_state.selected_paper:
        paper_id, display, metadata, source = st.session_state.selected_paper
        
        if metadata:
            authors = metadata.get('authors', [])
            author_str = f"{authors[0].get('surname', '')}, {authors[0].get('given-names', '')}" + (" et al." if len(authors) > 1 else "") if authors else "N/A"
            
            st.markdown(f"""
            **Title:** {metadata.get('title', 'N/A')}  
            **Authors:** {author_str}  
            **Journal:** {metadata.get('journal', 'N/A')}  
            **Year:** {metadata.get('year', 'N/A')}  
            **DOI:** {metadata.get('doi', 'N/A')}
            """)
            
            if metadata.get('abstract'):
                with st.expander("Abstract", expanded=True):
                    st.write(metadata['abstract'])
        else:
            st.info("Select a paper to see metadata")