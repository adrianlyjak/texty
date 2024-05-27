import outlines
from typing import List

@outlines.prompt
def few_shots(game_description: str, objectives: List[str]):
    """
    You are emulating an old school text adventure game.

    The game: {{game_description}}

    The users current objects: 
    {% for objective in objectives %}- {{objective}}
    {% endfor %}
    """


prompt = few_shots('a fun fun time', ['ice cream', 'chocolate', 'cake'])
print(prompt)