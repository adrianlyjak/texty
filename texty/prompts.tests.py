import logging
import pytest
from texty.prompts import gen_world
from texty.models.vllm import get_chat_response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gen_world_and_get_chat_response():
    description = "A thrilling adventure in a haunted mansion."
    prompt = gen_world(description)
    response = get_chat_response(prompt)
    logger.info(f"Response: {response}")

