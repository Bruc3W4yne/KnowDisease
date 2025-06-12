import streamlit as st
import time
import os
import logging # Use standard logging

import importlib
import sys


# Force reload modules to avoid cache
modules_to_reload = [
    'backend.profiler.form_filling.regex_handling',
    'backend.profiler.form_filling.form_filling',
    'backend.profiler.form_filling.dspy_x_outlines'
]

for module_name in modules_to_reload:
    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])

# Configure basic logging 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Direct imports - will raise ImportError if backend not found or path is wrong
from backend.pipeline import DiseaseTheoryPipeline
from backend.graph_builder import GraphBuilder
from app.config import neo4j_config

# --- Cached Backend Initialization ---
@st.cache_resource
def get_pipeline():
    logging.info("Initializing DiseaseTheoryPipeline...")
    # Initialize with neo4j config
    pipeline_instance = DiseaseTheoryPipeline(neo4j_config=neo4j_config, verbose=True, use_cot=True, use_json_constraints=None)
    logging.info("DiseaseTheoryPipeline initialized.")
    return pipeline_instance

@st.cache_resource
def get_graph_builder():
    logging.info("Initializing GraphBuilder...")
    # Initialize with neo4j config
    graph_builder_instance = GraphBuilder(neo4j_config)
    logging.info("GraphBuilder initialized.")
    return graph_builder_instance 