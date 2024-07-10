from posixpath import dirname
from texty.gametypes import Eventuality, GameElement, ProgressLog, TimeNode
from texty.prompts import GamePremise


def parse_time_node(json: str) -> str:
    premise = GamePremise.model_validate_json(json)
    return TimeNode(
        id="",
        summary="(Game not yet begun)",
        premise=premise.premise,
        game_elements=premise.game_elements,
    )


def get_seed(name: str) -> TimeNode:
    with open(dirname(__file__) + f"/seeds/{name}.json") as f:
        return parse_time_node(f.read())


zantar = get_seed("zantar")
lost_expedition = get_seed("lost_expedition")
blackwood_manor = get_seed("blackwood_manor")
time_travelers_dilemma = get_seed("time_travelers_dilemma")

# '''"The Time Traveler's Dilemma": Step into the shoes of Dr. Benjamin Grey, a brilliant scientist who invents a time machine. However, your experiments soon go awry as you inadvertently alter key events in history, leading to catastrophic consequences. Can you set things right before the fabric of reality unravels?'''
# '''"The Haunting of Hollow Hill": As Emily Everly, a paranormal investigator, you are called to the remote town of Hollow Hill to investigate a series of mysterious disappearances. As you delve into the town's dark history and encounter restless spirits, you must uncover the truth behind the haunting before it claims your own soul.'''
# '''"The Arctic Obsidian": Join Captain James Mallory on a perilous expedition to the Arctic Circle in search of a legendary gem known as the Arctic Obsidian. As you traverse treacherous ice fields and fend off rival explorers, you must navigate the harsh terrain and ancient curses that guard the precious stone.'''
# '''"The Witches of Whitewood": In this supernatural mystery, you play as Detective Thomas Hawthorne, who is called to the quaint town of Whitewood to investigate a series of bizarre murders. As you uncover a coven of witches with sinister intentions, you must unravel the dark secrets that shroud the town before it falls prey to evil.'''
# '''"The Castle of Illusions": Join Princess Elara on a quest to rescue her kingdom from the clutches of the malevolent sorcerer, Morathos. As you navigate the enchanted labyrinth of his castle and face deadly traps and illusions, you must outwit the sorcerer and unleash the power of the legendary Crystal Heart to save your people.'''
# '''"The Secret of Serpent's Cove": Dive into a maritime adventure as Captain Benjamin Drake, a notorious pirate seeking redemption. When a mysterious treasure map leads you to the cursed island of Serpent's Cove, you must navigate treacherous waters and face ghostly pirates to uncover the legendary treasure and break the island's curse.'''
# '''"The Enchanted Forest": Embark on a fairy-tale journey as Princess Aurora, who is cursed to sleep for a hundred years by the evil sorceress Maleficent. As you awaken in a magical forest filled with enchanted creatures and hidden dangers, you must navigate the dream-like landscape and gather items to break the curse before time runs out.'''
# '''"The City of Shadows": Set in a dystopian future, you play as Jack Harper, a former detective haunted by his past. When a string of gruesome murders plagues the city of Neo-Paris, you must hunt down the elusive killer known as the Shadow Man while grappling with your own inner demons. Can you solve the mystery and find redemption in a world consumed by darkness?'''


# "In a post-apocalyptic world, the player must navigate a dangerous wasteland filled with mutated creatures and hostile factions in search of a rumored hidden paradise."
# "The player is a detective investigating a series of mysterious disappearances in a small town, uncovering dark secrets and a supernatural presence lurking in the shadows."
# "A group of adventurers must band together to stop an ancient evil from awakening and bringing chaos to the kingdom, using their unique skills and abilities to overcome challenges."
# "In a cyberpunk city controlled by corrupt corporations, the player must join a rebellion and take down the oppressive regime while navigating a web of intrigue and double-crosses."
# "A time-traveling scientist accidentally creates a paradox that threatens to unravel the fabric of reality, and must race against time to fix their mistake before it's too late."
# "A fantasy world is plunged into darkness by a powerful sorcerer, and the player must gather a group of heroes to retrieve the scattered pieces of a legendary artifact and restore light to the land."
# "In a haunted mansion filled with malevolent spirits, the player must solve puzzles and uncover the dark history of the house to free the trapped souls and lift the curse."
# "A group of survivors must navigate a zombie-infested world in search of a safe haven, making tough decisions and facing moral dilemmas along the way."
# "The player is a pirate captain sailing the high seas in search of treasure, facing rival pirates, sea monsters, and the wrath of the navy as they strive to become the most infamous buccaneer."
# "In a dystopian future where emotions are controlled by a totalitarian government, the player must lead a rebellion to overthrow the oppressive regime and restore freedom to society."
