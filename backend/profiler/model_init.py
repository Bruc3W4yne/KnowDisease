from transformers import AutoModelForCausalLM, AutoTokenizer
import outlines

def initialize_llm(deterministic: bool = False):
    model_id = "hugging-quants/Meta-Llama-3.1-8B-Instruct-GPTQ-INT4"
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="cuda:0",
        torch_dtype="auto",
        trust_remote_code=True
    )

    outlines_llm = outlines.models.Transformers(model=model, tokenizer=tokenizer)
    if deterministic:
        outlines_sampler = outlines.samplers.greedy()
    else:
        outlines_sampler = outlines.samplers.multinomial(top_p=0.9, temperature=0.4)

    return outlines_llm, outlines_sampler