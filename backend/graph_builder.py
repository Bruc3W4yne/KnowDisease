from neo4j import GraphDatabase, exceptions as neo4j_exceptions
from typing import Dict, List, Optional
import logging
import json

NOT_MENTIONED_VARIATIONS = {"not present", "not mentioned", "not mentioned in the paper", "n/a", "", None}

class GraphBuilder:
    def __init__(self, neo4j_config):
        """Initialize with config dict containing uri, user, password"""
        try:
            self.driver = GraphDatabase.driver(
                neo4j_config["uri"], 
                auth=(neo4j_config["user"], neo4j_config["password"])
            )
        except Exception as e:
            print(f"GraphBuilder: Failed to connect to Neo4j - {e}") 
            self.driver = None 

    def close(self):
        if self.driver:
            self.driver.close()
            self.driver = None

    def _normalize_and_split_values(self, value_input):
        """Accept a raw string or a python list of strings and return a list of
        lowercase, de-duplicated terms suitable for KG nodes."""
        if value_input is None:
            return []
        if isinstance(value_input, list):
            raw_items = value_input
        else:
            raw_items = value_input.split(",")

        items = [item.strip().lower() for item in raw_items if isinstance(item, str) and item.strip()]
        cleaned_items = [itm for itm in items if itm not in NOT_MENTIONED_VARIATIONS]
        return list(dict.fromkeys(cleaned_items))

    def populate_graph_from_form(self, form_dict, paper_id_for_graph, evidence_dict=None, reasoning_dict=None):
        """
        Enhanced version that stores evidence AND reasoning on relationships.
        
        Args:
            form_dict: Extracted disease theory data
            paper_id_for_graph: Paper identifier
            evidence_dict: Field -> {term -> evidence_quote} mapping
            reasoning_dict: Field -> reasoning_text mapping (from CoT)
        """
        print(f"DEBUG GraphBuilder: Called with reasoning_dict: {bool(reasoning_dict)}, fields: {list(reasoning_dict.keys()) if reasoning_dict else []}")
        
        if not self.driver:
            print("GraphBuilder: Neo4j driver not available.")
            return
        if not form_dict:
            print(f"GraphBuilder: Empty form_dict for paper_id {paper_id_for_graph}. Skipping.")
            return

        with self.driver.session(database="neo4j") as session:
            disease_name_str = form_dict.get("disease_name")
            processed_disease_names = self._normalize_and_split_values(disease_name_str)
            if not processed_disease_names:
                print(f"GraphBuilder: No valid disease_name for paper {paper_id_for_graph}.")
                return
            
            # Handle multiple diseases and merge duplicates
            for disease_name in processed_disease_names:
                session.run("MERGE (d:Disease {name: $disease_name})", disease_name=disease_name)
            
            primary_disease_name = processed_disease_names[0]

            field_to_graph_mapping = {
                "etiology_factor":      ("EtiologyFactor",      "HAS_ETIOLOGY_FACTOR"),
                "diagnostic_method":    ("DiagnosticMethod",    "HAS_DIAGNOSTIC_METHOD"),
                "biomarker":            ("Biomarker",           "HAS_BIOMARKER"),
                "treatment_intervention": ("TreatmentIntervention", "HAS_TREATMENT"),
                "prognostic_indicator": ("PrognosticIndicator", "HAS_PROGNOSTIC_INDICATOR"),
            }
            
            print(f"DEBUG GraphBuilder: reasoning_dict keys: {list(reasoning_dict.keys()) if reasoning_dict else 'None'}")
            print(f"DEBUG GraphBuilder: field_mapping keys: {list(field_to_graph_mapping.keys())}")

            for field_key, (node_label, rel_type) in field_to_graph_mapping.items():
                value_string = form_dict.get(field_key)
                items = self._normalize_and_split_values(value_string)

                field_evidence = {}
                if evidence_dict and field_key in evidence_dict:
                    field_evidence = {k.lower(): v for k, v in evidence_dict[field_key].items()}

                field_reasoning = ""
                if reasoning_dict and field_key in reasoning_dict:
                    field_reasoning = reasoning_dict[field_key]
                    print(f"DEBUG GraphBuilder: Found reasoning for {field_key}: {field_reasoning[:100]}...")
                else:
                    print(f"DEBUG GraphBuilder: No reasoning for {field_key}")

                for item_name in items:
                    item_lower = item_name.lower()
                    raw_evidence_detail = field_evidence.get(item_lower)
                    
                    evidence_to_store = None
                    if isinstance(raw_evidence_detail, dict):
                        evidence_to_store = json.dumps(raw_evidence_detail)
                    elif isinstance(raw_evidence_detail, str):
                        evidence_to_store = raw_evidence_detail

                    reasoning_to_store = field_reasoning if field_reasoning else None
                    
                    if reasoning_to_store:
                        print(f"DEBUG GraphBuilder: Storing reasoning for {item_name} ({field_key}): {reasoning_to_store[:50]}...")

                    cypher_rel = f"""
                    MATCH (d:Disease {{name: $disease_name}})
                    MERGE (item_node:{node_label} {{name: $item_name}})
                    MERGE (d)-[r:{rel_type}]->(item_node)
                    ON CREATE SET
                        r.sources  = [$paper_id_for_graph],
                        r.evidence = CASE WHEN $evidence_quote IS NULL THEN [] ELSE [$evidence_quote] END,
                        r.reasoning = CASE WHEN $reasoning_text IS NULL THEN [] ELSE [$reasoning_text] END
                    ON MATCH SET
                        r.sources  = CASE WHEN $paper_id_for_graph IN r.sources THEN r.sources
                                          ELSE r.sources + $paper_id_for_graph END,
                        r.evidence = CASE WHEN $evidence_quote IS NULL OR $evidence_quote IN r.evidence THEN r.evidence
                                          ELSE r.evidence + $evidence_quote END,
                        r.reasoning = CASE WHEN $reasoning_text IS NULL OR $reasoning_text IN r.reasoning THEN r.reasoning
                                          ELSE r.reasoning + $reasoning_text END
                    """
                    try:
                        session.run(cypher_rel,
                                    disease_name=primary_disease_name,
                                    item_name=item_name,
                                    paper_id_for_graph=paper_id_for_graph,
                                    evidence_quote=evidence_to_store,
                                    reasoning_text=reasoning_to_store)
                    except Exception as e:
                        print(f"ERROR running Cypher for item '{item_name}' (field: {field_key}, paper: {paper_id_for_graph}): {e}")

            print(f"GraphBuilder: Finished processing data for paper_id {paper_id_for_graph}")