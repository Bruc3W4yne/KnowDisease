import streamlit as st
import json
from datetime import datetime

st.set_page_config(page_title="Settings", layout="wide", initial_sidebar_state="collapsed")

st.title("Pipeline Settings")
st.markdown("Configure extraction pipeline parameters and model settings.")

# Initialize session state for settings if not exists
if 'settings' not in st.session_state:
    st.session_state.settings = {
        'extraction_mode': 'Chain-of-Thought (CoT)',
        'model': 'hugging-quants/Meta-Llama-3.1-8B-Instruct-GPTQ-INT4',
        'temperature': 0.4,
        'max_tokens': 2000,
        'top_k': 7,
        'chunk_size': 1090,
        'chunk_overlap': 256,
        'relevance_threshold': 0.8
    }

# Main content area
col1, col2 = st.columns([1.5, 1], gap="large")

with col1:
    st.subheader("Model Configuration")
    
    # Model Selection
    with st.container(border=True):
        st.markdown("**Language Model**")
        model_options = [
            'hugging-quants/Meta-Llama-3.1-8B-Instruct-GPTQ-INT4',
            'arcee-ai/BioMistral-merged-instruct',
            'dmis-lab/meerkat-7b-v1.0',
            'TsinghuaC3I/Llama-3.1-8B-UltraMedical',
            'm42-health/Llama3-Med42-8B',
            'johnsnowlabs/JSL-MedLlama-3-8B-v1.0'
        ]
        
        selected_model = st.selectbox(
            "Select the language model for extraction",
            model_options,
            index=model_options.index(st.session_state.settings['model']),
            label_visibility="collapsed"
        )
        
        model_info = {
            'hugging-quants/Meta-Llama-3.1-8B-Instruct-GPTQ-INT4': 'General-purpose Llama 3.1 model with GPTQ quantization',
            'arcee-ai/BioMistral-merged-instruct': 'Biomedical-focused Mistral variant',
            'dmis-lab/meerkat-7b-v1.0': 'Medical knowledge extraction model',
            'TsinghuaC3I/Llama-3.1-8B-UltraMedical': 'Medical-tuned Llama 3.1',
            'm42-health/Llama3-Med42-8B': 'Healthcare-specific Llama model',
            'johnsnowlabs/JSL-MedLlama-3-8B-v1.0': 'John Snow Labs medical variant'
        }
        
        st.caption(model_info.get(selected_model, ''))
    
    # Extraction Mode
    with st.container(border=True):
        st.markdown("**Extraction Mode**")
        
        mode_col1, mode_col2 = st.columns(2)
        
        extraction_mode = st.radio(
            "Choose extraction approach",
            ['Chain-of-Thought (CoT)', 'Direct Extraction (Non-CoT)'],
            index=0 if st.session_state.settings['extraction_mode'] == 'Chain-of-Thought (CoT)' else 1,
            horizontal=True,
            label_visibility="collapsed"
        )
        
        if extraction_mode == 'Chain-of-Thought (CoT)':
            st.info("CoT mode provides reasoning and evidence for each extraction, improving accuracy for complex relationships.")
        else:
            st.info("Direct extraction mode is faster but may miss nuanced relationships in the text.")
    
    # Generation Parameters
    st.subheader("Generation Parameters")
    
    with st.container(border=True):
        param_col1, param_col2 = st.columns(2)
        
        with param_col1:
            temperature = st.slider(
                "**Temperature**",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.settings['temperature'],
                step=0.1,
                help="Controls randomness in generation. Lower values make output more deterministic."
            )
            
            max_tokens = st.number_input(
                "**Max Tokens**",
                min_value=500,
                max_value=4000,
                value=st.session_state.settings['max_tokens'],
                step=100,
                help="Maximum number of tokens to generate per field."
            )
        
        with param_col2:
            top_k = st.slider(
                "**Top-K Retrieval**",
                min_value=1,
                max_value=10,
                value=st.session_state.settings['top_k'],
                help="Number of document chunks to retrieve for each field."
            )
            
            relevance_threshold = st.slider(
                "**Relevance Threshold**",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.settings['relevance_threshold'],
                step=0.05,
                help="Minimum similarity score for retrieved chunks."
            )

with col2:
    st.subheader("Retrieval Configuration")
    
    with st.container(border=True):
        st.markdown("**Document Chunking**")
        
        chunk_size = st.slider(
            "Chunk Size (tokens)",
            min_value=256,
            max_value=2048,
            value=st.session_state.settings['chunk_size'],
            step=64,
            help="Size of text chunks for retrieval."
        )
        
        chunk_overlap = st.slider(
            "Chunk Overlap (tokens)",
            min_value=0,
            max_value=512,
            value=st.session_state.settings['chunk_overlap'],
            step=32,
            help="Overlap between consecutive chunks."
        )
        
        st.markdown("**Embedding Model**")
        embedding_model = st.selectbox(
            "Select embedding model",
            ['pritamdeka/S-PubMedBert-MS-MARCO', 'sentence-transformers/all-MiniLM-L6-v2'],
            label_visibility="collapsed"
        )
    
    # Current Configuration Summary
    st.subheader("Active Configuration")
    
    with st.container(border=True):
        config_data = {
            "Model": selected_model.split('/')[-1],
            "Mode": extraction_mode,
            "Temperature": temperature,
            "Max Tokens": max_tokens,
            "Top-K": top_k,
            "Chunk Size": chunk_size,
            "Chunk Overlap": chunk_overlap,
            "Relevance Threshold": relevance_threshold
        }
        
        for key, value in config_data.items():
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"**{key}:**")
            with col2:
                st.markdown(f"{value}")

# Action buttons
st.divider()

button_col1, button_col2, button_col3, button_col4 = st.columns([1, 1, 1, 2])

with button_col1:
    if st.button("Save Configuration", type="primary", use_container_width=True):
        # Update session state
        st.session_state.settings.update({
            'extraction_mode': extraction_mode,
            'model': selected_model,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'top_k': top_k,
            'chunk_size': chunk_size,
            'chunk_overlap': chunk_overlap,
            'relevance_threshold': relevance_threshold
        })
        st.success("Configuration saved successfully!")

with button_col2:
    if st.button("Reset to Defaults", use_container_width=True):
        st.session_state.settings = {
            'extraction_mode': 'Chain-of-Thought (CoT)',
            'model': 'hugging-quants/Meta-Llama-3.1-8B-Instruct-GPTQ-INT4',
            'temperature': 0.4,
            'max_tokens': 2000,
            'top_k': 7,
            'chunk_size': 1090,
            'chunk_overlap': 256,
            'relevance_threshold': 0.8
        }
        st.rerun()

with button_col3:
    if st.button("Export Config", use_container_width=True):
        config_json = json.dumps(st.session_state.settings, indent=2)
        st.download_button(
            label="Download",
            data=config_json,
            file_name=f"llmdap_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

# Footer
st.divider()
st.caption("Settings are applied to new extraction runs. Existing results are not affected by configuration changes.")