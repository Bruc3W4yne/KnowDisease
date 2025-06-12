# Configuration for the LLMDap application

# Neo4j connection settings
neo4j_config = {
    "uri": "neo4j+ssc://94a9f783.databases.neo4j.io", 
    "user": "neo4j",                                
    "password": "8H2loqcAY1U-aIcv-TrlQujd0-JPm0va9IQIH9WV6Wg" 
}

node_colors = {
    "Disease": "#E67E80",              
    "EtiologyFactor": "#DE8F6E",       
    "TreatmentIntervention": "#6ABD9D", 
    "Biomarker": "#78A1D1",
    "DiagnosticMethod": "#9B8CC4",      
    "PrognosticIndicator": "#F0C880",   

    "Symptoms": "#D16666",         
    "Riskfactors": "#F39C12",      
    "BodyParts": "#C4A484",        
    "Systems": "#9B59B6",          
    "Mechanisms": "#2ECC71",       
    
    # Fallback
    "default": "#B0BEC5",          
}

graph_styles = {
    "obsidian": {
        "theme": {
            "background": "#FFFFFF",
            "font_color": "#333333"
        },
        "options": {
            "nodes": {
                "borderWidth": 2,
                "borderWidthSelected": 3,
                "size": 25,
                "font": {"color": "#333333", "size": 14, "face": "Arial"},
                "color": {
                    "border": "rgba(255,255,255,0.8)",
                    "highlight": {"border": "#ffffff", "background": "#D3D3D3"}
                },
                "shape": "dot",
                "shadow": {
                    "enabled": True,
                    "color": "rgba(0,0,0,0.2)",
                    "size": 10,
                    "x": 2,
                    "y": 2
                }
            },
            "edges": {
                "color": {"color": "rgba(120,120,120,0.3)", "highlight": "#666666"},
                "width": 1.5,
                "smooth": {"enabled": True, "type": "continuous", "roundness": 0.5},
                "arrows": {"to": {"enabled": True, "scaleFactor": 0.4}},
                "shadow": {
                    "enabled": True,
                    "color": "rgba(0,0,0,0.1)",
                    "size": 3,
                    "x": 1,
                    "y": 1
                }
            },
            "physics": { 
                "forceAtlas2Based": {
                    "gravitationalConstant": -800,
                    "springLength": 100,
                    "springConstant": 0.04,
                    "avoidOverlap": 0.5,
                    "damping": 0.4
                },
                "maxVelocity": 50,
                "minVelocity": 0.1,
                "solver": "forceAtlas2Based",
                "timestep": 0.5,
                "adaptiveTimestep": True,
                "stabilization": {
                    "enabled": True,
                    "iterations": 100,
                    "updateInterval": 50
                }
            },
            "layout": {
                "improvedLayout": True,
                "clusterThreshold": 150
            },
            "interaction": {
                "hover": True,
                "multiselect": True, 
                "navigationButtons": False
            }
        }
    }
}

# graph_html_fix - Minimal CSS for graph iframe
graph_html_fix = """
<style>
/* Basic reset for iframe content */
html, body {
    margin: 0 !important;
    padding: 0 !important;
}

/* Hide the vis.js loading bar */
.vis-network-loading-bar {
    display: none !important;
}
</style>
"""

# Causal diagram configuration
CAUSAL_NODE_ABBREVIATIONS = {
    "EtiologyFactor": "E",
    "DiagnosticMethod": "Dx",
    "Disease": "D",
    "Biomarker": "B",
    "TreatmentIntervention": "T",
    "PrognosticIndicator": "P"
}

CAUSAL_LEVEL_MAPPING = {
    "EtiologyFactor": 0,          # Root causes
    "Disease": 1,                 # Disease node
    "DiagnosticMethod": 2,        # Diagnostics
    "Biomarker": 2,              # Biomarkers (same level as diagnostics)
    "TreatmentIntervention": 3,   # Treatments
    "PrognosticIndicator": 4      # Outcomes
}

# Precision medicine biomarkers
PRECISION_BIOMARKERS = [
    "BRAF", "MEK", "EGFR", "ALK", "ROS1", "PD1", "PDL1", 
    "PD-1", "PD-L1", "HER2", "KRAS", "BRCA", "BCR-ABL"
]

PRECISION_THERAPY_TERMS = [
    "TARGETED", "INHIBITOR", "ANTIBODY", "MAB", "MONOCLONAL"
]

# Edge styling configuration
CAUSAL_EDGE_STYLES = {
    "precision_medicine": {"color": "#4488CC", "width": 6, "dashes": False},
    "diagnostic": {"color": "#999999", "width": 3.5, "dashes": True},
    "causal": {"color": "#444444", "width": 5, "dashes": False},
    "feedback_response": {"color": "#CC66CC", "width": 3.5, "dashes": [5, 5]},
    "feedback_biomarker": {"color": "#66CCCC", "width": 3, "dashes": [5, 5]},
    "default": {"color": "#666666", "width": 4, "dashes": False}
}
