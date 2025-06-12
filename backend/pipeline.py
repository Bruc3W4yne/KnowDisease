import os
import json
import nltk

from .data.xml_loader import load_xml
from .profiler.model_init import initialize_llm
from .profiler.form_filling.form_filling import SequentialFormFiller
from .profiler.context_shortening.context_shortening import Retrieval
from .profiler.metadata_schemas.disease_theory_schema_v12 import DiseaseTheorySchema
from .profiler.metadata_schemas.cot_schema import CoTModelSchema
from .profiler.metadata_schemas.noncot_schema import SimpleAnswerSchema
from .graph_builder import GraphBuilder

VERSION = "1.0.0"

def ensure_nltk_punkt():
    try:
        nltk.data.find('tokenizers/punkt')
    except nltk.downloader.DownloadError:
        nltk.download('punkt', quiet=True)

ensure_nltk_punkt()

class DiseaseTheoryPipeline:
    def __init__(self, neo4j_config, verbose=False, use_cot=True, use_json_constraints=None):
        self.verbose = verbose
        self.use_cot = use_cot
        
        # Allow independent control of JSON constraints
        if use_json_constraints is None:
            self.use_json_constraints = use_cot
        else:
            self.use_json_constraints = use_json_constraints

        self.graph_builder = GraphBuilder(neo4j_config)

        self.retriever = Retrieval(
            chunk_info_to_compare = "direct",
            field_info_to_compare = "description",
            include_choice_every = 1,
            embedding_model_id = "pritamdeka/S-PubMedBert-MS-MARCO",
            n_keywords = 13,
            top_k = 5,
            chunk_size = 800,
            chunk_overlap = 96,
            mmr_param = 1.0,
            pydantic_form=DiseaseTheorySchema,
            keyphrase_range = (1, 1),
            relevance_threshold=0.8,
            return_scores=True
        )

        llm, sampler = initialize_llm(deterministic=True)

        self.form_filler = SequentialFormFiller(
            outlines_llm = llm,
            outlines_sampler = sampler,
            pydantic_form=DiseaseTheorySchema,
            max_tokens=2500,
            verbose=self.verbose,
            use_cot=use_cot,
            use_json_constraints=self.use_json_constraints,
            cot_schema=CoTModelSchema if use_cot else None
        )

    def get_context_wrapper(self, **kwargs):
        context_str, _ = self.retriever(**kwargs)
        return context_str

    def _extract_surrounding_sentences(self, evidence_input, field_context_text):
        """Helper to find preceding/succeeding sentences for a given quote within its context."""
        actual_quote_text = ""
        if isinstance(evidence_input, dict) and "quote" in evidence_input:
            actual_quote_text = evidence_input["quote"]
        elif isinstance(evidence_input, str):
            actual_quote_text = evidence_input
        else:
            return {"preceding": "", "quote": str(evidence_input) if evidence_input else "", "succeeding": ""}

        if not actual_quote_text.strip() or not field_context_text.strip():
            return {"preceding": "", "quote": actual_quote_text, "succeeding": ""}

        context_sentences = nltk.sent_tokenize(field_context_text)
        preceding_text = ""
        succeeding_text = ""
        found_quote_sentence_idx = -1

        for i, sentence in enumerate(context_sentences):
            if actual_quote_text in sentence:
                found_quote_sentence_idx = i
                break
        
        if found_quote_sentence_idx != -1:
            if found_quote_sentence_idx > 0:
                preceding_text = context_sentences[found_quote_sentence_idx - 1]
            if found_quote_sentence_idx < len(context_sentences) - 1:
                succeeding_text = context_sentences[found_quote_sentence_idx + 1]
        
        return {
            "preceding": preceding_text,
            "quote": actual_quote_text,
            "succeeding": succeeding_text
        }

    def _extract_reasoning_data(self):
        """Extract reasoning from form filler field fillers (CoT mode)."""
        reasoning_dict = {}
        
        print(f"DEBUG: Extracting reasoning data. CoT mode: {self.use_cot}")
        
        if not self.use_cot or not hasattr(self.form_filler, 'field_fillers'):
            print(f"DEBUG: Skipping reasoning extraction. Has field_fillers: {hasattr(self.form_filler, 'field_fillers') if self.form_filler else False}")
            return reasoning_dict
        
        for field_name, field_filler in self.form_filler.field_fillers.items():
            if hasattr(field_filler, 'last_cot_data') and field_filler.last_cot_data:
                reasoning = field_filler.last_cot_data.get("reasoning", "")
                if reasoning:
                    reasoning_dict[field_name] = reasoning
                    print(f"DEBUG: Found reasoning for {field_name}: {reasoning[:100]}...")
            else:
                print(f"DEBUG: No CoT data for field {field_name}")
        
        print(f"DEBUG: Total fields with reasoning: {len(reasoning_dict)}")
        return reasoning_dict

    def process_document(self, paper_path, progress_callback=None):

        paper = load_xml(paper_path)
        self.retriever.set_document(paper)

        result = self.form_filler.forward(
            get_context=self.get_context_wrapper,
            progress_callback=progress_callback
        )

        
        raw_field_evidence_map = getattr(self.form_filler, "evidence", {})
        field_contexts = getattr(self.form_filler, "contexts", {})
        
        enriched_evidence_for_graph = {}

        for field_name, term_evidence_map in raw_field_evidence_map.items():
            enriched_evidence_for_graph[field_name] = {}
            field_context_text = field_contexts.get(field_name, "")

            if not field_context_text or not isinstance(term_evidence_map, dict):
                if isinstance(term_evidence_map, dict):
                    for term, evidence_detail in term_evidence_map.items():
                        quote_val = evidence_detail.get("quote") if isinstance(evidence_detail, dict) else str(evidence_detail or "")
                        enriched_evidence_for_graph[field_name][term] = {"preceding": "", "quote": quote_val, "succeeding": ""}
                else:
                    enriched_evidence_for_graph[field_name]["unknown_term"] = {"preceding": "", "quote": str(term_evidence_map or ""), "succeeding": ""}
                continue
            
            for term, evidence_item in term_evidence_map.items():
                enriched_evidence_for_graph[field_name][term] = self._extract_surrounding_sentences(
                    evidence_item, 
                    field_context_text
                )
            
        self.last_evidence = enriched_evidence_for_graph
        
        # Extract reasoning data for CoT mode
        reasoning_data = self._extract_reasoning_data()
        self.last_reasoning = reasoning_data
        
        print(f"DEBUG: Process document complete. Reasoning extracted: {len(reasoning_data)} fields")
        if reasoning_data:
            print("DEBUG: Sample reasoning:", list(reasoning_data.keys()))
        
        paper_id = os.path.splitext(os.path.basename(paper_path))[0].split("_")[0]

        return result, paper_id

    def process_and_store(self, paper_path, progress_callback=None):
        """Process document and store in graph database."""
        result, paper_id = self.process_document(paper_path, progress_callback)
        
        # Convert pydantic result to dict for graph builder
        if hasattr(result, 'model_dump'):
            form_dict = result.model_dump()
        elif hasattr(result, 'dict'):
            form_dict = result.dict()
        else:
            form_dict = dict(result)
        
        # Store in graph with evidence and reasoning
        print(f"DEBUG: About to call graph_builder with reasoning: {bool(self.last_reasoning)}, keys: {list(self.last_reasoning.keys()) if self.last_reasoning else []}")
        
        self.graph_builder.populate_graph_from_form(
            form_dict=form_dict,
            paper_id_for_graph=paper_id,
            evidence_dict=self.last_evidence,
            reasoning_dict=self.last_reasoning
        )
        
        return result, paper_id