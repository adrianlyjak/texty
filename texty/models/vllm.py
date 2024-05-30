from functools import lru_cache
from outlines.models import vllm, VLLM

# from outlines.models.transformers import Transformers
from vllm import LLM, SamplingParams
import torch

model_id = "meta-llama/Meta-Llama-3-8B-Instruct"


@lru_cache(maxsize=None)  # makes it a lazy singleton
def get_llm() -> LLM:
    # INFO 04-20 09:28:21 model_runner.py:684] Capturing the model for CUDA graphs. This may lead to unexpected consequences if the model is not static. To run the model in eager mode, set 'enforce_eager=True' or use '--enforce-eager' in the CLI.
    # INFO 04-20 09:28:21 model_runner.py:688] CUDA graphs can take additional 1~3 GiB memory per GPU. If you are running out of memory, consider decreasing `gpu_memory_utilization` or enforcing eager mode. You can also reduce the `max_num_seqs` as needed to decrease memory usage.
    return LLM(
        model_id,
        tensor_parallel_size=max(1, torch.cuda.device_count()),
        # quantization="gptq",
        # max_model_len=1024,
        max_num_seqs=16,
        # gpu_memory_utilization=0.8,
        enforce_eager=True,
    )


@lru_cache(maxsize=None)  # makes it a lazy singleton
def get_outlines() -> VLLM:
    return VLLM(get_llm())

if __name__ == "__main__":
    from outlines import generate
    mod = get_outlines()
    generator = generate.text(mod)
    answer = generator("You are in a small room with a door to the north.")
    print("answer",  answer)
