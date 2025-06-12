import streamlit as st

st.set_page_config(page_title="About KnowDisease", layout="wide")

st.title("About KnowDisease")

st.markdown("""
KnowDisease is an AI-assisted application for identification and analysis of disease theories from biomedical literature. 
This project was developed as part of the UPCAST initiative at SINTEF to investigate the potential of AI-based data 
enrichment and analysis technologies in biomedical research.
""")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("## Project Overview")
    st.markdown("""
    KnowDisease leverages Large Language Models (LLMs) and knowledge graph technologies to:
    
    - **Extract disease theories** from scientific papers automatically
    - **Build knowledge graphs** representing relationships between diseases, causes, diagnostics, and treatments
    - **Visualize causal diagrams** showing disease pathways and treatment strategies
    - **Provide evidence-based explanations** by linking back to source publications
    
    The system processes biomedical literature to create a comprehensive understanding of disease mechanisms, 
    helping researchers and medical practitioners navigate the complex landscape of disease research.
    """)
    
    st.markdown("## Key Features")
    st.markdown("""
    - **Automated extraction** of six key disease theory components:
        - Disease names and characteristics
        - Etiology factors (genetic, environmental, behavioral, infectious)
        - Diagnostic methods and biomarkers
        - Treatment interventions
        - Prognostic indicators
    - **Chain-of-thought reasoning** for explainable AI insights
    - **Interactive visualizations** including knowledge graphs and causal diagrams
    - **Evidence tracking** linking all extracted information to source papers
    - **Neo4j graph database** for scalable knowledge storage and querying
    """)
    
    st.markdown("## Technical Architecture")
    st.markdown("""
    The application is built on:
    - **Backend**: Python with DSPy/Outlines for structured LLM output
    - **Frontend**: Streamlit for interactive web interface
    - **Database**: Neo4j for graph-based knowledge storage
    - **Embeddings**: S-PubMedBert-MS-MARCO for biomedical text understanding
    - **Pipeline**: Adapted from LLMDAP (LLM-based Data Asset Profiling)
    """)

with col2:
    st.markdown("## Links & Resources")
    st.markdown("""
    ### GitHub Repository
    [github.com/bruc3w4yne/KnowDisease](https://github.com/bruc3w4yne/KnowDisease)
    
    ### Organizations
    - [SINTEF Digital](https://www.sintef.no/en/digital/)
    - [UPCAST Project](http://www.upcast-project.eu/)
    
    ### Technologies Used
    - [Streamlit](https://streamlit.io/)
    - [Neo4j](https://neo4j.com/)
    - [DSPy](https://github.com/stanfordnlp/dspy)
    - [PubMed](https://pubmed.ncbi.nlm.nih.gov/)
    """)
    
    st.info("""
    **Note**: This is a research prototype developed 
    as part of the UPCAST project to explore AI-assisted 
    biomedical knowledge extraction and analysis.
    """)

st.markdown("---")

st.markdown("## Research Context")
st.markdown("""
This work addresses the challenge of systematically understanding disease theories scattered across vast biomedical 
literature. By automatically extracting and organizing disease-related information, KnowDisease helps researchers:

1. **Discover patterns** in disease causation and treatment approaches
2. **Identify knowledge gaps** in current disease understanding
3. **Facilitate hypothesis generation** through visual exploration of causal relationships
4. **Support evidence-based medicine** by providing traceable sources for all claims

The project demonstrates how modern AI technologies can augment biomedical research by transforming 
unstructured scientific text into structured, queryable knowledge graphs.
""")

st.markdown("---")
st.markdown("*KnowDisease - Transforming biomedical literature into actionable disease knowledge*")