import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
import json
from neo4j import exceptions as neo4j_exceptions

st.set_page_config(page_title="Causal Diagram Explorer", layout="wide")

from app.utils.backend_init import get_graph_builder
from app.config import (
    node_colors, 
    CAUSAL_NODE_ABBREVIATIONS,
    CAUSAL_LEVEL_MAPPING,
    CAUSAL_EDGE_STYLES,
    PRECISION_BIOMARKERS,
    PRECISION_THERAPY_TERMS
)

graph_builder = get_graph_builder()

@st.cache_data(show_spinner=False)
def get_disease_names():
    if not graph_builder or not graph_builder.driver:
        return ["No connection available"]
    
    try:
        with graph_builder.driver.session(database="neo4j") as session:
            results = session.run("MATCH (d:Disease) RETURN d.name AS name ORDER BY d.name")
            names = [record["name"] for record in results]
            return names if names else ["No diseases found"]
    except Exception as e:
        return [f"Error: {str(e)[:30]}..."]

def get_edge_style(node_type, node_name=""):
    node_name_upper = node_name.upper()
    
    if node_type == "TreatmentIntervention":
        if any(marker in node_name_upper for marker in PRECISION_BIOMARKERS):
            return CAUSAL_EDGE_STYLES["precision_medicine"]
        if any(term in node_name_upper for term in PRECISION_THERAPY_TERMS):
            return CAUSAL_EDGE_STYLES["precision_medicine"]
    
    if node_type == "Biomarker" and any(marker in node_name_upper for marker in PRECISION_BIOMARKERS):
        return CAUSAL_EDGE_STYLES["precision_medicine"]
    
    if node_type == "DiagnosticMethod":
        return CAUSAL_EDGE_STYLES["diagnostic"]
    
    if node_type in ["EtiologyFactor", "PrognosticIndicator"]:
        return CAUSAL_EDGE_STYLES["causal"]
    
    return CAUSAL_EDGE_STYLES["default"]

def format_evidence_display(edge_data):
    sections = []
    
    if edge_data.get('evidence'):
        evidence_items = []
        for i, ev in enumerate(edge_data['evidence'][:3]):
            if ev:
                try:
                    if isinstance(ev, str) and ev.startswith('{'):
                        ev_dict = json.loads(ev)
                        text = ev_dict.get('quote', ev)
                    else:
                        text = str(ev)
                    evidence_items.append(f"{i+1}. {text[:200]}...")
                except:
                    evidence_items.append(f"{i+1}. {str(ev)[:200]}...")
        if evidence_items:
            sections.append(("Evidence", evidence_items))
    
    if edge_data.get('reasoning'):
        reasoning = edge_data['reasoning'][0] if edge_data['reasoning'] else ""
        if reasoning:
            sections.append(("Reasoning", [reasoning[:300] + "..." if len(reasoning) > 300 else reasoning]))
    
    if edge_data.get('sources'):
        sections.append(("Sources", [', '.join(edge_data['sources'][:3])]))
    
    return sections

def fetch_causal_relationships(disease_name):
    query = """
    MATCH (d:Disease {name: $disease_name})-[r]->(o)
    RETURN d, elementId(d) as d_id, type(r) as rel_type, o, elementId(o) as o_id,
           r.evidence as evidence, r.reasoning as reasoning, r.sources as sources
    """
    
    try:
        with graph_builder.driver.session(database="neo4j") as session:
            results = session.run(query, disease_name=disease_name)
            return list(results)
    except Exception:
        return []

def build_causal_graph(disease_name, relationships):
    nodes_data = []
    edges_data = []
    seen_nodes = set()
    
    treatment_nodes = set()
    response_nodes = set()
    biomarker_nodes = set()
    
    disease_id = f"disease_{disease_name.lower().replace(' ', '_')}"
    nodes_data.append({
        "id": disease_id,
        "label": f"{disease_name.upper()}\n(D)",
        "type": "Disease",
        "color": node_colors["Disease"],
        "size": 80,
        "font": {"size": 36, "face": "Arial Black", "bold": True},
        "level": CAUSAL_LEVEL_MAPPING["Disease"],
        "title": f"{disease_name} - Central disease node"
    })
    seen_nodes.add(disease_id)
    
    for record in relationships:
        other_node = record["o"]
        other_id = f"node_{record['o_id']}"
        rel_type = record["rel_type"]
        
        labels = list(other_node.labels)
        node_type = labels[0] if labels else "Unknown"
        node_name = other_node.get("name", "Unknown")
        
        if other_id not in seen_nodes:
            abbreviation = CAUSAL_NODE_ABBREVIATIONS.get(node_type, "")
            label = f"{node_name}\n({abbreviation})" if abbreviation else node_name
            
            size = 60 if node_type in ["EtiologyFactor", "TreatmentIntervention", "PrognosticIndicator"] else 55
            font_size = 28 if node_type in ["EtiologyFactor", "TreatmentIntervention"] else 26
            
            nodes_data.append({
                "id": other_id,
                "label": label,
                "type": node_type,
                "color": node_colors.get(node_type, node_colors["default"]),
                "size": size,
                "font": {"size": font_size, "face": "Arial", "bold": True},
                "level": CAUSAL_LEVEL_MAPPING.get(node_type, 2),
                "title": f"{node_type}: {node_name}"
            })
            seen_nodes.add(other_id)
            
            if node_type == "TreatmentIntervention":
                treatment_nodes.add(other_id)
            elif node_type == "PrognosticIndicator" and "response" in node_name.lower():
                response_nodes.add(other_id)
            elif node_type == "Biomarker":
                biomarker_nodes.add(other_id)
        
        if node_type in ["EtiologyFactor", "DiagnosticMethod", "TreatmentIntervention"]:
            from_id, to_id = other_id, disease_id
        else:
            from_id, to_id = disease_id, other_id
        
        edge_style = get_edge_style(node_type, node_name)
        
        edges_data.append({
            "from": from_id,
            "to": to_id,
            "rel_type": rel_type.replace("HAS_", "").replace("_", " ").title(),
            "evidence": record.get("evidence", []),
            "reasoning": record.get("reasoning", []),
            "sources": record.get("sources", []),
            **edge_style
        })
    
    if response_nodes and treatment_nodes:
        for resp in response_nodes:
            for treat in treatment_nodes:
                edges_data.append({
                    "from": resp,
                    "to": treat,
                    "rel_type": "Treatment Adaptation",
                    "evidence": [],
                    "reasoning": ["Feedback: Treatment response influences adaptation"],
                    "sources": [],
                    **CAUSAL_EDGE_STYLES["feedback_response"],
                    "smooth": {"type": "curvedCW", "roundness": 0.3}
                })
    
    return nodes_data, edges_data

def get_graph_config():
    return Config(
        width="100%",
        height=1000,
        directed=True,
        physics={
            "enabled": True,
            "solver": "hierarchicalRepulsion",
            "hierarchicalRepulsion": {
                "nodeDistance": 400,
                "springLength": 350,
                "damping": 0.09
            },
            "stabilization": {"enabled": True, "iterations": 2000}
        },
        layout={
            "hierarchical": {
                "enabled": True,
                "direction": "LR",
                "sortMethod": "directed",
                "levelSeparation": 500,
                "nodeSpacing": 300
            }
        },
        interaction={"hover": True, "tooltipDelay": 300},
        edges={"smooth": {"type": "continuous", "roundness": 0.5}},
        nodes={"shape": "circle", "borderWidth": 1.5}
    )

st.title("Disease Theory Causal Model")
st.markdown("Interactive causal diagram showing disease pathways extracted from biomedical literature.")

if not graph_builder or not graph_builder.driver:
    st.error("Neo4j connection failed. Please check database status.")
    st.stop()

disease_names = get_disease_names()
if disease_names and disease_names[0].startswith(("No ", "Error")):
    st.warning(disease_names[0])
    st.stop()

selected_disease = st.selectbox("Select a Disease:", disease_names)

if selected_disease:
    relationships = fetch_causal_relationships(selected_disease)
    
    if relationships:
        nodes_data, edges_data = build_causal_graph(selected_disease, relationships)
        
        nodes = [Node(
            id=n["id"],
            label=n["label"],
            size=n["size"],
            color=n["color"],
            font=n["font"],
            level=n["level"],
            title=n["title"]
        ) for n in nodes_data]
        
        edges = [Edge(
            source=e["from"],
            target=e["to"],
            color=e.get("color"),
            width=e.get("width"),
            dashes=e.get("dashes"),
            smooth=e.get("smooth", {"type": "continuous"})
        ) for e in edges_data]
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.subheader(f"Causal Network: {selected_disease}")
            clicked = agraph(nodes=nodes, edges=edges, config=get_graph_config())
            
            if clicked:
                st.session_state.clicked_node = clicked
        
        with col2:
            st.markdown("### Components")
            for node_type, abbr in CAUSAL_NODE_ABBREVIATIONS.items():
                color = node_colors.get(node_type, node_colors["default"])
                st.markdown(
                    f"<div style='display: flex; align-items: center; margin: 8px 0;'>"
                    f"<div style='width: 30px; height: 30px; background-color: {color}; "
                    f"border-radius: 50%; margin-right: 8px;'></div>"
                    f"<span><b>{abbr}:</b> {node_type.replace('Factor', '').replace('Indicator', '')}</span></div>",
                    unsafe_allow_html=True
                )
            
            st.markdown("### Edge Types")
            st.markdown("**→** Direct causal")
            st.markdown("**⇢** Diagnostic")
            st.markdown("<span style='color: #4488CC'>**→**</span> Precision medicine", unsafe_allow_html=True)
            st.markdown("<span style='color: #CC66CC'>**↺**</span> Feedback", unsafe_allow_html=True)
        
        st.session_state.nodes_data = nodes_data
        st.session_state.edges_data = edges_data
    else:
        st.info(f"No causal data found for {selected_disease}")

if 'clicked_node' in st.session_state and st.session_state.clicked_node:
    if 'nodes_data' in st.session_state and 'edges_data' in st.session_state:
        with st.sidebar:
            clicked_id = st.session_state.clicked_node
            nodes_data = st.session_state.nodes_data
            edges_data = st.session_state.edges_data
            
            node_info = next((n for n in nodes_data if n["id"] == clicked_id), None)
            if node_info:
                st.subheader(f"Details: {node_info['label']}")
                st.write(f"Type: {node_info['type']}")
                
                st.subheader("Relationships")
                for edge in edges_data:
                    if edge['from'] == clicked_id or edge['to'] == clicked_id:
                        st.markdown(f"**{edge['rel_type']}**")
                        
                        evidence_sections = format_evidence_display(edge)
                        for title, items in evidence_sections:
                            with st.expander(title):
                                for item in items:
                                    st.write(item)
                        st.markdown("---")