from llama_index.core.schema import TextNode
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter

OVERSHOOT_FACTOR = 1.1

def _pseudo_markdown_splitter(text, chunk_size, chunk_overlap, verbose=True):

    header_symbol = [("#", "section_header")]
    markdown_splitter = MarkdownHeaderTextSplitter(header_symbol)
    md_header_splits = markdown_splitter.split_text(text)

    splitter_chunk_size = int(chunk_size)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=splitter_chunk_size, 
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""]
        )
    
    splits = text_splitter.split_documents(md_header_splits)

    if verbose:
        print(f"Found {len(md_header_splits)} top-level sections → {len(splits)} chunks after size splitting (target ~{chunk_size}, splitter max {splitter_chunk_size})")

    return splits

def chunk_by_headers_and_clean(document, chunk_size, chunk_overlap, verbose):
    nodes = []

    splits = _pseudo_markdown_splitter(
        document,
        chunk_size * OVERSHOOT_FACTOR, 
        chunk_overlap,
        verbose=verbose
    )

    MIN_CHUNK_FACTOR = 0.1
    MIN_CHUNK_SIZE = int(chunk_size * MIN_CHUNK_FACTOR)

    filtered_splits = [doc for doc in splits if len(doc.page_content.strip()) >= MIN_CHUNK_SIZE]

    if verbose:
        print(f"Filtered out {len(splits) - len(filtered_splits)} short chunks. Keeping {len(filtered_splits)} chunks.")
        print("-" * 20) 
        print("Chunk Lengths (after filtering):")

    total_chars = 0
    for i, doc in enumerate(filtered_splits):
        chunk_len = len(doc.page_content) 
        total_chars += chunk_len
        if verbose:
            print(f"  Chunk {i}: {chunk_len} chars")

        cleaned_metadata = {k: v for k, v in doc.metadata.items() if v is not None and v != ''}
        nodes.append(TextNode(text=doc.page_content, metadata=cleaned_metadata))

    if verbose and filtered_splits:
        average_len = total_chars / len(filtered_splits)
        print(f"\nAverage Chunk Length: {average_len:.2f} chars")
        print("-" * 20)

    return nodes