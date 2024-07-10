from texty.gametypes import GameElementUpdate, TimeNode


def test_parse_game_element():
    input = """
    {
      "response_plan": "Zantar steps into the bustling streets of Neo-Angeles. The sky is a murky grey, a result of the constant smog from the industrial district. His AR glasses flash notifications about recent crimes in the area.\\n\\nAs he walks, he sees his partner Jimbo leaning against a holographic billboard advertising the latest in cybernetic enhancements. Jimbo waves him over, looking around suspiciously.\\n\\n\\"Hey Zantar, I've got something for you,\\" Jimbo mutters, pulling out a small data chip. \\"This might lead us to the Oatmeal Killer.\\"\\n\\nZantar takes the chip, feeling the weight of his responsibilities. The streets are filled with people, but the sense of unease is palpable. The Oatmeal Killer's presence is felt everywhere, and the police force seems helpless against the mysterious threat.",
      "events": [
        {
          "type": "update_game_element",
          "element_id": "zantar",
          "add": {
            "present": [
              "Zantar steps into the bustling streets of Neo-Angeles, greeted by the murky grey sky and constant smog.",
              "Jimbo hands Zantar a data chip, hinting it might lead to the Oatmeal Killer.",
              "The streets are filled with people, but there's a palpable sense of unease."
            ]
          },
          "replace": {
            "past": [],
            "present": [],
            "future": []
          }
        },
        {
          "type": "update_game_element",
          "element_id": "oatmeal-killer",
          "add": {
            "present": [
              "Jimbo provides Zantar with a data chip that might lead to clues about the Oatmeal Killer."
            ]
          },
          "replace": {
            "past": [],
            "present": [],
            "future": []
          }
        }
      ],
      "summary": "Zantar receives a lead on the Oatmeal Killer"
    }"""

    parsed = GameElementUpdate.model_validate_json(input)
    assert len(parsed.events) == 2


def test_parse_time_node():
    input = """
{"id":"f9f9f2b9-1119-472e-987a-cccea67dc7fc","timestep":2,"premise":"A futuristic detective mystery in Neo-Angeles about Zantar, a junior detective","summary":"Zantar's aggressive dismissal of Jimbo creates tension and potential future complications.","response_plan":null,"previous":["3f33a37a-8d42-4aeb-a9db-e376972a9b6d","c98805dd-3ee4-49d7-b333-e726f9f5e517","22d57283-7697-49e6-a6b3-da136ffdb56b"],"event_log":[{"role":"game","type":"game-response","text":"The rain taps gently against the grime-streaked window of Zantar's office, each droplet a reminder of the relentless gray that blankets Neo-Angeles. The dim light from the single, flickering bulb casts long shadows across the room, highlighting the piles of disorganized files that have accumulated over countless late nights.\\n\\nZantar sits behind his cluttered desk, the weight of junior detective duties evident in his weary eyes. His mind drifts momentarily to how he landed this job in the first place—his uncle, a prominent figure on the force, had pulled some strings. It’s not something Zantar is particularly proud of, but it’s a truth he’s come to accept.\\n\\nA familiar voice crackles through the silence, breaking his reverie. It's Jimbo, his partner since day one. \\"Hey Zantar, got some leads on making a little extra money,\\" he had said earlier. The words linger in the air, hinting at paths both perilous and potentially rewarding.\\n\\nBeyond the confines of his office, the city pulses with its own dark energy. Strange killings have been occurring, victims found dead with eyes fixed on oatmeal commercials playing on their AR glasses. Despite efforts to stop the ad, it keeps appearing, a sinister enigma within the neon-lit labyrinth of Neo-Angeles.\\n\\nAs the rain continues its steady rhythm, Zantar knows that the city holds its secrets close. Whether through the grime-streaked corridors of power or the shadowy underworld of cybernetic enhancements, his journey is just beginning.","timestep":1},{"role":"player","type":"ambiguous","text":"tell jimbo that I've got real work to do, and look through the recent case files on my computer","timestep":1},{"role":"game","type":"game-response","text":"Could you clarify if you want to tell Jimbo something first or look through the recent case files on your computer?","timestep":1},{"role":"player","type":"act","text":"tell jimbo to fuck right off","timestep":2},{"role":"game","type":"game-response","text":"Jimbo's expression sours as Zantar's harsh words cut through the musty air of the office. A silence hangs between them, heavy and uncomfortable. Jimbo's eyes narrow, and without another word, he turns and storms out of the room, slamming the door behind him. The sound reverberates, leaving an uneasy echo.\\n\\nThe tension is palpable, and Zantar knows he may have just burned a valuable bridge. Jimbo, feeling disrespected, is likely to withhold information about the extra money leads and potentially useful contacts. This rift in their partnership could have far-reaching consequences, not just for their current cases but for Zantar's future ambitions within the force.\\n\\nAs the rain outside continues its relentless drumming, Zantar is left alone with his thoughts and the flickering light. The city’s secrets won't reveal themselves easily, and with Jimbo now estranged, the path ahead just became even more uncertain.","timestep":2}],"last_update":{"response_plan":"Zantar's aggressive dismissal of Jimbo creates tension between them. Jimbo, feeling disrespected, decides to withhold information about the extra money leads and potentially useful contacts. This causes a shift in their partnership dynamic and affects Zantar's chances of climbing the corrupt ranks.","events":[{"type":"update_game_element","element_id":"chief-of-police","add":{"past":null,"present":["Jimbo, feeling disrespected, decides to withhold information from Zantar about the extra money leads and useful contacts. This causes a strain in their partnership."],"future":null},"replace":{"past":null,"present":null,"future":null}},{"type":"update_game_element","element_id":"cybernetic-underworld","add":{"past":null,"present":null,"future":["Zantar's strained relationship with Jimbo may push him to seek alternative, possibly illicit, means of gaining an edge in his investigations."]},"replace":{"past":null,"present":null,"future":null}}],"summary":"Zantar's aggressive dismissal of Jimbo creates tension and potential future complications."},"game_elements":[{"element_id":"chief-of-police","name":"Chief of Police","element_type":"eventuality","past":["Zantar got the job in the first place because his uncle is on the force"],"present":["Zantar's parter Jimbo told him he has some leads on making a little extra money"],"future":["Through whatever means, Zantar climbs the corrupt ranks, becoming chief of police"]},{"element_id":"oatmeal-killer","name":"Oatmeal Killer","element_type":"eventuality","past":["Strange killings have been occurring where residents of neo-angeles are found dead, watching oatmeal commercials on their AR glasses"],"present":["The killings continue. The ad-networks have been notified to stop running the ad, but it continues to pop up without explanation"],"future":[]},{"element_id":"ai-overlord-exposed","name":"AI Overlord","element_type":"eventuality","past":[],"present":[],"future":["Zantar uncovers a massive AI conspiracy controlling Neo-Angeles"]},{"element_id":"cybernetic-underworld","name":"Cybernetic Underworld","element_type":"eventuality","past":[],"present":[],"future":["Zantar becomes entangled in an underground cybernetic enhancement ring"]},{"element_id":"zantar","name":"Zantar","element_type":"character","past":[],"present":["This is the player character. All player actions are performed as Zantar","Zantar is a junior detective"],"future":[]}],"retired_game_elements":[]}
"""
    result = TimeNode.model_validate_json(input)
    assert len(result.game_elements) == 5
