from functools import lru_cache
from typing import Any, Generator, List, TypedDict
import outlines
from outlines import models
from outlines.models.openai import OpenAI, OpenAIConfig
from openai import AsyncOpenAI
import httpx

# from outlines.models.transformers import Transformers
from vllm import LLM, SamplingParams
import torch


@lru_cache(maxsize=None)  # makes it a lazy singleton
def get_local_vllm(model_id="meta-llama/Meta-Llama-3-8B-Instruct") -> LLM:
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


mode = "VLLM_API"

import logging

# Configure logging
logging.basicConfig(
    level=logging.WARN, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
# Create a logger object
logger = logging.getLogger(__name__)


def log_request(request: httpx.Request):
    logger.debug(
        f"Request: {request.method} {request.url} - Headers: {request.headers} - Body: {request.content}"
    )
    return request


@lru_cache(maxsize=None)  # makes it a lazy singleton
def get_outlines(
    model_id=None,
) -> models.VLLM | OpenAI:  # outlines is poorly typed around here
    if mode == "VLLM_API":
        client = AsyncOpenAI(
            base_url="http://localhost:8000/v1",
            http_client=httpx.AsyncClient(event_hooks={"before_send": [log_request]}),
        )
        config = OpenAIConfig(model="./Meta-Llama-3-70B-Instruct-GPTQ-4b", temperature=0.2)
        # tokenizer = Tokenizer() # tiktoken.encoding_for_model("gpt-4")
        return OpenAI(client, config)
    else:
        return models.VLLM(get_local_vllm(model_id=model_id))


class Message(TypedDict):
    role: str
    content: str


def get_chat_response(prompt: str) -> str:
    model = get_outlines()
    txt = ""
    if mode == "VLLM_API":
        txt = prompt
    else:
        txt = (
            get_local_vllm()
            .get_tokenizer()
            .apply_chat_template(
                [
                    {"role": "user", "content": prompt},
                ],
                tokenize=False,
            )
        )
    txt_gen = outlines.generate.text(model)
    return txt_gen(txt)


if __name__ == "__main__":
    get_chat_response("whats the capital of paris?")
