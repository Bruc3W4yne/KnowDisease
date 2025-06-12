import streamlit as st
from neo4j import GraphDatabase, exceptions as neo4j_exceptions
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import json


from config import graph_styles, node_colors, neo4j_config, graph_html_fix
from utils.graph_components import build_graph_html

st.set_page_config(page_title="Knowledge Graph", layout="wide", initial_sidebar_state="collapsed")

st.title("Disease Theory Knowledge Graph")
st.markdown("Exploring the graph using Neo4j data and dynamic styling.")

def fetch_graph_data_from_neo4j(driver):
    """Fetches nodes (with source count) and edges from Neo4j."""
    nodes_data = []
    edges_data = []
    with driver.session(database="neo4j") as session:
        # Fetch nodes: elementId, name, type, and distinct source count
        nodes_query = """
        MATCH (n)
        // Optional match for relationships having the 'sources' property
        OPTIONAL MATCH (n)-[r]-() WHERE r.sources IS NOT NULL
        // Collect lists of sources from all connected relationships
        WITH n, collect(r.sources) AS sources_lists 
        // Unwind the list of lists. Handle nodes with no relationships/sources
        UNWIND (CASE WHEN size(sources_lists) > 0 THEN sources_lists ELSE [[]] END) AS single_list 
        // Unwind the actual sources list. Handle empty lists
        UNWIND (CASE WHEN size(single_list) > 0 THEN single_list ELSE [null] END) AS source_paper_id 
        // Collect distinct, non-null sources per node
        WITH n, collect(DISTINCT source_paper_id) AS distinct_sources 
        RETURN 
            elementId(n) AS node_id,
            n.name AS name,
            CASE 
                WHEN size(labels(n)) > 0 THEN labels(n)[0]
                ELSE 'Unknown' 
            END AS type,
            // Count distinct non-null sources
            size([s IN distinct_sources WHERE s IS NOT NULL]) AS source_count,
            [s IN distinct_sources WHERE s IS NOT NULL] AS pmids // Added pmids
        """
        nodes_result = session.run(nodes_query)
        for record in nodes_result:
            nodes_data.append(record.data())
        
        # Fetch edges: source elementId, target elementId, relationship type, evidence, and reasoning
        edges_query = """
        MATCH (s)-[r]->(t)
        RETURN 
            elementId(s) AS source_id, 
            elementId(t) AS target_id, 
            type(r) AS type,
            r.evidence AS evidence_payload, // Corrected to fetch r.evidence
            r.reasoning AS reasoning_payload // Added to fetch model reasoning
        """
        relationships_result = list(session.run(edges_query)) # Fetch edges directly
        for record in relationships_result:
             edges_data.append(record.data())
            
    return nodes_data, edges_data
 
driver = None
nodes_result = []
relationships_result = []
counts = None
connection_error = None

try:
    driver = GraphDatabase.driver(neo4j_config["uri"], auth=(neo4j_config["user"], neo4j_config["password"]))
    driver.verify_connectivity()
    
    with driver.session(database="neo4j") as session: 
        count_query = """
        MATCH (n)
        WITH count(n) AS node_count
        MATCH ()-[r]->()
        RETURN node_count, count(r) AS relationship_count
        """
        counts = session.run(count_query).single()
        
        if counts and counts["node_count"] > 0:
             nodes_result, relationships_result = fetch_graph_data_from_neo4j(driver)

except neo4j_exceptions.ServiceUnavailable as e:
    connection_error = f"Neo4j connection failed: {e}. Please ensure Neo4j is running."
    if 'neo4j_config' in locals() and 'uri' in neo4j_config:
        connection_uri = neo4j_config.get('uri', 'Not configured') 
except Exception as e:
    connection_error = f"An unexpected error occurred during data fetching: {e}"
finally:
    if driver:
        driver.close()

if connection_error:
    st.error(connection_error)
    if 'connection_uri' in locals():
         st.info(f"Attempted URI: {connection_uri}")
elif counts and counts["node_count"] > 0:
    st.toast(f"Connected to Neo4j: {counts['node_count']} nodes, {counts['relationship_count']} relationships.")
    col1_m, col2_m = st.columns(2)
    col1_m.metric("Total Nodes in DB", counts["node_count"])
    col2_m.metric("Total Relationships in DB", counts["relationship_count"])
elif counts:
    st.warning(f"Connected to Neo4j, but no nodes found (Node count: {counts['node_count']}).")
else:
     st.warning("Could not retrieve data or counts from Neo4j.")

if nodes_result:
    with st.container(border=True):
        # Search bar (placeholder for now)
        search_query = st.text_input("Search Nodes", placeholder="Search...", label_visibility="collapsed")
        
        st.divider()

        # Graph Rendering
        try:
            selected_style_name = "obsidian"
            style_config = graph_styles[selected_style_name]
            G = nx.DiGraph()
            base_node_size = 20 
            
            # Add nodes
            for record in nodes_result:
                node_id = record["node_id"]
                name = record["name"]
                node_type = record["type"]
                source_count = record["source_count"]
                color = node_colors.get(node_type, node_colors["default"])
                
                # Size based on node type and source count
                current_size = base_node_size
                if node_type == "Disease": 
                    current_size = base_node_size * 1.8  
                elif source_count <= 1: 
                    current_size = base_node_size * 1.0  
                elif source_count == 2: 
                    current_size = base_node_size * 1.25  
                elif source_count == 3: 
                    current_size = base_node_size * 1.5   
                else: 
                    current_size = base_node_size * 1.75  
                    
                G.add_node(node_id, label=name, size=current_size, color=color, 
                          node_type=node_type, source_count=source_count, 
                          pmids=record["pmids"], 
                          title=f"{name} ({node_type}, Sources: {source_count})")
            
            # Add edges
            for record in relationships_result:
                G.add_edge(record["source_id"], record["target_id"], title=record["type"])

            # Create PyVis network
            net = Network(
                height="100vh",
                width="100%", 
                bgcolor="#F8F9FA",
                font_color=style_config["theme"]["font_color"],
                directed=True,
                notebook=False 
            )
            net.from_nx(G) 
            net.set_options(json.dumps(style_config["options"])) 

            html_output = net.generate_html(name="graph_temp.html")
            
            edges_data_json = json.dumps(relationships_result)
            
            html_output = build_graph_html(html_output, edges_data_json, graph_html_fix)
            
            components.html(html_output, height=850, scrolling=False)
            
        except Exception as graph_err:
             st.error(f"Failed to render graph: {graph_err}")
             st.exception(graph_err)

else:
    if not connection_error:
        st.info("No graph data retrieved from the database to display.")