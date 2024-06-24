import json
from typing import Any, List, Optional
import argparse
from os.path import dirname
from texty.prompts import GenZone, activate_game_state, gen_world, gen_world_objective
from texty.models.model import get_chat_response, schema_response, stream_chat_response


class Eval:

    def run(self, test: Optional[str]):
        if test:
            getattr(self, test)()
        else:
            # Accessing the class's __dict__ to find methods starting with "test_"
            methods = [m for m in dir(self) if m.startswith("test_")]
            for method_name in methods:

                method = getattr(self, method_name)
                method()

    def _print_chat(self, prompt: str):
        for chunk in stream_chat_response(prompt):
            print(chunk, end="", flush=True)

    def _load_jsonl_data(self, path: str) -> List[Any]:
        with open(dirname(__file__) + "/../data" + path) as f:
            results = []
            for line in f:
                if line:
                    results.append(json.loads(line))
            return results

    def test_gen_world_puzzle(self):
        description = "A puzzle game set in a labyrinth, where you must use your wits to find your way out."
        self._print_chat(gen_world(description))

    future_detective_summary = "A detective game set in a futuristic city, where you must solve a series of murders."

    def test_gen_world_future_detective(self):
        description = self.future_detective_summary
        self._print_chat(gen_world(description))

    def test_objectives_future_detective(self):
        results = self._load_jsonl_data("/tests/future_detective/world.jsonl")
        self._print_chat(gen_world_objective(self.future_detective_summary, results))

    def test_gen_intro_scene_future_detective(self):
        world = self._load_jsonl_data("/tests/future_detective/world.jsonl")
        objectives = self._load_jsonl_data("/tests/future_detective/objectives.jsonl")
        intro = activate_game_state(self.future_detective_summary, world, objectives)
        print(intro)
        print(schema_response(intro, GenZone))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Eval", description="Runs the evals")
    parser.add_argument("-t", "--test", type=str)
    args = parser.parse_args()
    Eval().run(args.test)
