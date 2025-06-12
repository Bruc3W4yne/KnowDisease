EVIDENCE_PANEL_STYLES = """
<style>
    /* Toggle button for evidence panel */
    #evidence-panel-toggle-tab {
        position: fixed; 
        top: 50%;
        right: 0px; 
        transform: translateY(-50%);
        width: 28px;
        height: 55px;
        background-color: rgba(240, 242, 245, 0.97);
        border: 1px solid #cccccc;
        border-right: none;
        border-top-left-radius: 6px;
        border-bottom-left-radius: 6px;
        padding: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-size: 16px;
        line-height: 1;
        z-index: 1005; 
        box-shadow: -2px 0 5px rgba(0,0,0,0.1);
        transition: right 0.4s ease-in-out, background-color 0.2s ease-in-out;
    }
    
    #evidence-panel-toggle-tab span {
        color: #333;
        font-size: 20px;
        font-weight: bold;
        display: block;
        line-height: 1;
    }

    /* Main evidence panel */
    #evidence-overlay-panel {
        position: fixed;
        top: 0;
        right: 0;
        width: 30%; 
        height: 100%;
        background-color: rgba(240, 242, 245, 0.97); 
        border-left: 1px solid #cccccc;
        padding: 15px;
        box-sizing: border-box;
        z-index: 1000; 
        overflow-y: auto; 
        overflow-x: hidden;
        transform: translateX(100%);
        transition: transform 0.4s ease-in-out; 
        box-shadow: -2px 0 5px rgba(0,0,0,0.1); 
        font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, sans-serif;
    }
    
    #evidence-overlay-panel.open {
        transform: translateX(0%);
    }

    #evidence-panel-content h4 {
        font-size: 1.4rem;
        font-weight: 600;
        color: #333333;
        margin-top: 25px;
        margin-bottom: 15px;
        padding-left: 15px;
    }
    
    #evidence-panel-content h5 {
        font-size: 1.2rem;
        font-weight: 600;
        color: #444444;
        margin-top: 20px;
        margin-bottom: 12px;
        padding-left: 15px;
    }
    
    #evidence-panel-content p {
        line-height: 1.6;
        color: #555555;
        padding-left: 15px;
        margin-bottom: 8px;
        font-size: 0.9rem;
    }
    
    #evidence-panel-content p strong {
        color: #333333;
        font-weight: 600;
    }
    
    .evidence-item {
        border-top: 1px solid #e0e0e0;
        padding-top: 8px;
        margin-top: 8px;
    }
    
    .evidence-item p {
        margin-bottom: 4px;
    }
    
    .evidence-item p .evidence-context {
        font-style: italic;
        color: #5a5a5a;
    }
    
    #evidence-overlay-panel hr {
        border: none;
        border-top: 1px solid #333333;
        margin-top: 15px;
        margin-bottom: 20px;
    }
</style>
"""

EVIDENCE_PANEL_HTML = """
<button id="evidence-panel-toggle-tab" title="Toggle Evidence Panel"><span>&larr;</span></button>

<div id="evidence-overlay-panel">
    <div id="evidence-panel-content">
        <h4>Evidence Details</h4>
        <p>Select a node to see its details here.</p>
    </div>
</div>
"""

def get_evidence_panel_javascript(edges_data_json: str) -> str:
    return f"""
<script>
if (typeof network !== 'undefined') {{
    const evidencePanel = document.getElementById('evidence-overlay-panel');
    const panelContent = document.getElementById('evidence-panel-content');
    const toggleTabButton = document.getElementById('evidence-panel-toggle-tab');
    const tabArrowSpan = toggleTabButton ? toggleTabButton.querySelector('span') : null;
    const allEdgesData = JSON.parse(document.getElementById('graphEdgesData').textContent);
    let contentResetTimeout = null;

    function formatCamelCase(text) {{
        if (!text) return 'N/A';
        const result = text.replace(/([A-Z])/g, ' $1');
        return result.charAt(0).toUpperCase() + result.slice(1).trim();
    }}

    function openEvidencePanel() {{
        evidencePanel.classList.add('open');
        toggleTabButton.style.right = '30%';
        if (tabArrowSpan) tabArrowSpan.innerHTML = '&gt;';
    }}

    function closeEvidencePanel(resetContent = true) {{
        evidencePanel.classList.remove('open');
        toggleTabButton.style.right = '0px';
        if (tabArrowSpan) tabArrowSpan.innerHTML = '&lt;';
        if (resetContent) {{
            if (contentResetTimeout) {{
                clearTimeout(contentResetTimeout);
            }}
            contentResetTimeout = setTimeout(() => {{
                if (panelContent) {{
                    panelContent.innerHTML = '<h4>Evidence Details</h4><p>Select a node to see its details here.</p>';
                }}
                contentResetTimeout = null;
            }}, 400);
        }}
    }}

    closeEvidencePanel(false); 

    network.on('selectNode', function(params) {{
        network.stopSimulation();
        
        if (contentResetTimeout) {{
            clearTimeout(contentResetTimeout);
            contentResetTimeout = null;
        }}
        
        if (evidencePanel && panelContent) {{
            const nodeId = params.nodes[0];
            if (nodeId !== undefined) {{ 
                const nodeObject = network.body.data.nodes.get(nodeId);
                if (nodeObject) {{
                    let pmidsText = 'N/A';
                    if (nodeObject.pmids && nodeObject.pmids.length > 0) {{
                        pmidsText = nodeObject.pmids.join(', ');
                    }}
                    let evidenceHTML = '<h5>Associated Evidence (from Edges):</h5>';
                    let foundEvidence = false;
                    let reasoningHTML = '<h5>Model Reasoning:</h5>';
                    let foundReasoning = false;
                    
                    allEdgesData.forEach(edge => {{
                        if (edge.source_id === nodeId || edge.target_id === nodeId) {{
                            if (edge.evidence_payload && Array.isArray(edge.evidence_payload) && edge.evidence_payload.length > 0) {{
                                foundEvidence = true;
                                edge.evidence_payload.forEach(item_payload => {{
                                    if (item_payload) {{
                                        let itemHtml = "";
                                        try {{
                                            const structured = JSON.parse(item_payload);
                                            if (structured && typeof structured === 'object' && 'quote' in structured) {{
                                                const preceding = structured.preceding || "";
                                                const quote = structured.quote || "Quote not available";
                                                const succeeding = structured.succeeding || "";
                                                
                                                itemHtml = `<p>`;
                                                if (preceding) itemHtml += `<span class="evidence-context">${{preceding}}</span> `;
                                                itemHtml += `<strong>${{quote}}</strong>`;
                                                if (succeeding) itemHtml += ` <span class="evidence-context">${{succeeding}}</span>`;
                                                itemHtml += `</p>`;
                                            }} else {{
                                                itemHtml = `<p>${{item_payload}}</p>`;
                                            }}
                                        }} catch (e) {{
                                            itemHtml = `<p>${{item_payload}}</p>`;
                                        }}
                                        evidenceHTML += `<div class="evidence-item">${{itemHtml}}</div>`;
                                    }}
                                }});
                            }}
                            
                            if (edge.reasoning_payload && Array.isArray(edge.reasoning_payload) && edge.reasoning_payload.length > 0) {{
                                foundReasoning = true;
                                const uniqueReasonings = [...new Set(edge.reasoning_payload.filter(r => r && r.trim()))];
                                uniqueReasonings.forEach(reasoning => {{
                                    reasoningHTML += `<div class="evidence-item"><p>${{reasoning}}</p></div>`;
                                }});
                            }}
                        }}
                    }});
                    
                    if (!foundEvidence) {{
                        evidenceHTML += '<p>No specific evidence details found for edges connected to this node.</p>';
                    }}
                    if (!foundReasoning) {{
                        reasoningHTML += '<p>No model reasoning available for this node.</p>';
                    }}
                    panelContent.innerHTML = `<h4>${{nodeObject.label || 'Node'}} Details</h4>
                                              <p><strong>Type:</strong> ${{formatCamelCase(nodeObject.node_type || 'N/A')}}</p>
                                              <p><strong>Associated PMIDs:</strong> ${{pmidsText}}</p>
                                              <hr>
                                              ${{evidenceHTML}}
                                              <hr>
                                              ${{reasoningHTML}}`;
                    openEvidencePanel();
                }} else {{
                    panelContent.innerHTML = '<h4>Node Details</h4><p>Could not retrieve details for the selected node.</p>';
                    openEvidencePanel(); 
                }}
            }}
        }}
    }});

    network.on('deselectNode', function() {{
        network.startSimulation();
    }});
    
    network.on('click', function(params) {{
        if (params.nodes.length === 0 && params.edges.length === 0) {{
            network.unselectAll();
            network.startSimulation();
            closeEvidencePanel();
        }}
    }});

    if (toggleTabButton) {{
        toggleTabButton.onclick = function() {{
            if (evidencePanel.classList.contains('open')) {{
                closeEvidencePanel();
            }} else {{
                if (!panelContent.querySelector('.evidence-item')) {{
                     panelContent.innerHTML = '<h4>Evidence Details</h4><p>Select a node to see its details. Or click again to close.</p>';
                }}
                openEvidencePanel();
            }}
        }};
    }}

    setTimeout(function() {{ 
        network.moveTo({{ scale: 0.3, animation: false }}); 
    }}, 250);

    setTimeout(function() {{
        var loadingBar = document.querySelector('.vis-network-loading-bar');
        if (loadingBar) loadingBar.style.display = 'none';
        var loadingScreen = document.querySelector('.vis-loading-screen');
        if (loadingScreen) loadingScreen.style.display = 'none';
        var genericLoading = document.querySelector('div[id*="loadingBar"], div[class*="loading-bar"]');
        if (genericLoading) genericLoading.style.display = 'none';
    }}, 500); 
}}
</script></body>
"""

def build_graph_html(html_output: str, edges_data_json: str, graph_html_fix: str) -> str:
    full_injection = (
        f'<script id="graphEdgesData" type="application/json">{edges_data_json}</script>' +
        EVIDENCE_PANEL_STYLES +
        EVIDENCE_PANEL_HTML +
        get_evidence_panel_javascript(edges_data_json)
    )
    
    html_output = html_output.replace("</body>", full_injection)
    html_output = html_output.replace("</head>", f"{graph_html_fix}</head>")
    
    return html_output