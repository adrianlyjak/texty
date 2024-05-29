from transformers import AutoModelForCausalLM, AutoTokenizer, GPTQConfig

model_id = "meta-llama/Meta-Llama-3-70B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
gptq_config = GPTQConfig(bits=4, dataset="c4", tokenizer=tokenizer)
quantized_model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto", quantization_config=gptq_config)