# Story Generator

Story Generator is an AI powered interactive story game framework, similar to classic choose-your-own-adventure books or text adventure games, but with more potential for player agency. Within the framework, the AI plays the role of author and dungeon master, iteratively planning and generating the story, adapting to the player's choices and actions.

## Predefined Story Structure

In order to pace and structure the overall story, the AI works within a pre-authored 5 component story structure. This is the premise and seed of the game.

1. The central **"Story Problem"**: This is the main conflict that the story is about. It's the stakes, explaining why main character should be personally motivated in solving the story problem, but have some personal hangup that is getting in their way. Through the course of the story, the character will need to change in some way to solve the story problem.
2. The **"Story Paradigm"**: This is the overall situation of the character and the broader world and social environment. This describes the character's normal day-to-day life, obligations, and position within the broader scope of their relationships and society. This covers world building and the character's role in it.
3. The **"Hidden Clues"**: In solving the story problem, the player will need to explore the world of the story and uncover clues that will ultimately help them uncover the story's mystery and solve the story problem. These clues can take the form of puzzles, objects, information, "keys," or story shaping events. They relate and guide the story to one or more of the specific endings.
4. The **"Decoy Resolution"**: This is the obvious resolution to the story problem, which the player believes they are working towards.
5. The **"Surprise Twist/Ultimate Resolution"**: When the player has successfully pieced together the necessary clues to reach a resolution, and is ready to solve the story problem, the story takes a surprising turn that subverts the player's expectations of the true nature of the story problem and its solution. This is the **Surprise Twist**, that leads to an **"Ultimate Resolution"**. With all the clues successfully assembled, what final action and/or challenge will the player need to take to resolve the story problem? How does the story end? What has the character discovered or changed about their world?

This is a choice driven generative game, so it contains multiple possible endings, which is expressed as multiple **Surprise Twist/Ultimate Resolution** pairs. The game tracks the probability of each ending as the story progresses.

## Adaptive Planning

Given the competing parallel storylines, and the player's agency, the path to reaching the end must be malleable and non-deterministic. The story structure is the seed, and the real shape of the story is collaboratively sculpted by the interaction of the player and the AI author. The author continuously plans a few steps ahead and pulls the players attention. The author has to skillfully tread a delicate balance between keeping consistency, making the game open-ended and participatory, and making the story enthralling. This is achieved with the following systems:

### Overall Story Planning

The game is composed of a series of short **Scenes**, which have a scene goal appropriate to the **Stage** of the story. The scene goal is a general question that the scene should answer. The answer is not prematerialized, but is discovered during the scene. Think of scenes more in the sense of scenes in a TV show, rather than chapters: they are short, focused on a place, time, or situation. They achieve their scene goal by answering it with **Scene Utility**. At the interval between scenes, the game brainstorms potential **Story Opportunities**. Using these, it charts multiple possible outlines to reach the various possible endings. The outlines and opportunties are used as resources during scene generation, but ultimately, the scene is improvised to maintain maximum dynamism and player agency. Encountered **Actors** and **Story Events** are summarized to track the game's progress and inform future scene planning.

#### Story Opportunities
The Opportunity Index is a collection of **"Story Opportunities"**. Opportunities are of a few different types:
    - **Hidden Clues**: Initialized from the Hidden Clues section of the story structure, and added to as the story unfolds. For example:
        - A cryptic 19th-century letter found tucked inside a first edition of "Moby Dick," written in invisible ink that only appears when exposed to ultraviolet light. When deciphered, it reveals the existence of a secret global network of influential families who have been manipulating world events for centuries.
        - An intricate, fractal-like symbol carved into the bark of a 500-year-old sequoia tree, which seems to glow faintly under the light of a full moon. When touched during a full moon, it grants the ability to communicate with plant life, unveiling an ancient network of botanical intelligence.
        - A vivid, recurring dream where the protagonist finds themselves in a labyrinthine library, with books whispering secrets in an unknown language, always waking up with a specific set of numbers etched in their mind. These numbers, when decoded, provide access to a hidden database containing classified government secrets and advanced technological blueprints.
    - **New Actors**: New characters, organizations, or systems that could be introduced to the story. For example:
        - Dr. Amelia Blackwood, a brilliant but eccentric quantum physicist who suddenly arrives in the small town of Millbrook, claiming to be researching temporal anomalies in the area
        - The Crimson Veil, a centuries-old secret society dedicated to protecting an ancient artifact said to grant immortality, with members infiltrating key positions in local government and businesses
        - ARIA (Adaptive Reasoning Intelligence Algorithm), an experimental AI system developed by a reclusive tech billionaire, which has begun making unsettling predictions about future events in the town with uncanny accuracy
    - **Story Beats**: Major events or plot points that could happen in the story. For example:
        - The protagonist discovers a betrayal by a close friend when they find a hidden USB drive containing confidential company information in their friend's desk drawer at work
        - A massive sinkhole suddenly opens up in the town square, swallowing the historic clock tower and revealing a network of ancient tunnels beneath the city
        - While cleaning out their late grandmother's attic, the main character uncovers a dusty old journal detailing their family's involvement in a secret society dating back to the 18th century
    - **Promise of the Premise**: Specific details based on the premise that a reader would expect. For example:
        - In a detective story: A tense interrogation where the detective faces off against a charismatic suspect. Every word exchanged feels like a chess move in a high-stakes game of wits.
        - In a fantasy adventure: Discovering an ancient, sentient magical artifact that communicates telepathically, revealing glimpses of a long-lost civilization and hinting at world-altering powers.
        - In a sci-fi thriller: First contact with an alien species that communicates through bioluminescent patterns and pheromones, creating an atmosphere of mounting tension and paranoia.

#### Scene Utility

Scene Utilities are a comprehensive set of mechanisms by which a story may progress.

- **Dramatic Obstacle / Problem:** Classic obstable, the story paradigm gives rise to a specific story problem that must be solved or circumnavigated in order for the character to reach their goal.
- **Paradigm Conflict:** An unsolvable complication. The story paradigm gives rise to a systemic conflict (often social or emotional) that cannot be solved directly but works to complicate the actions and relations of the characters. This is a general miasma problem that should be showcased via one or more specific instance(s) of this systemic problem in action.
- **Dramatic Debate:** When 2 or more characters disagree about some aspect of the story trajectory. This will often, but not always, culminate in a **Dramatic Question**, and/or a **Dramatic Statement of Intent**. It might even present characters with an ultimatum, or be a catalyst for a new emergent storyline if/when the dissenting party breaks away from the main to veer off on their own course.
- **Dramatic Statement of Intent:** When a character verbally commits to a specific course of action, allowing the audience to anticipate the story’s direction. Often this will be met with pushback from the other characters involved. Creates a sense of anticipation. This will also present an opportunity for **Dramatic Irony** which occurs any time the audience knows something important that character does not, and, being ignorant, remains blind to the true nature of the story paradigm. 
- **Action:** When a character makes a move to exert some force on the story and it’s trajectory—sometimes successfully, sometimes not. 
- **Consequence and Setback:** When a character suffers some kind of damage that changes his/her capabilities within the realm of the story.
- **Dramatic Mystery:** The story paradigm gives rise to an anomaly, evidence of a hidden element at work—nature and agenda unknown—that must be unveiled through the course of the story. 
- **Clue / Key Acquisition:** When a character uncovers some type of information or object that unlocks a piece of the story or opens an avenue that was perviously blocked or obscure to that character. This acquisition often comes as the successful result of some sort of initiative, or, even more frequently, as the consolation prize or fallout of some other failed intent and action. A *clue* will likely click into a previously established **Dramatic Mystery** while a *key* will help solve a previously established **Dramatic Problem.**
- **Dramatic Question:** When a character asks an important question that serves to: articulate an established paradigm conflict; highlight a dramatic mystery; intimate a new strategy; suggest an unforeseen conflict etc. This will articulate and clarify the story and can serve as a segue. 
- **Crisis and Ultimatum:** When a character finds themselves suddenly cornered into a crisis stemming directly from the story problem or overall story paradigm. A crisis cannot be avoided and must be addressed in the moment. This often presents characters with a seemingly ridged ultimatum, forcing them to make some kind of decision.
- **Strong Thematic Statement or Persuasive Argument:** When a character, or sometimes the narrator, makes a strong statement about the nature of the paradigm. This is the character looking head and shoulders above the rabble and making some kind of salient observation about "what it all means." *South Park* is the king of this. Also *Sex and the City*. A variation is the **Persuasive Antithesis Argument:** Such as a villainous monologue, where a character sees the paradigm but draws a bad conclusion with which he attempts to corrupt others. 
- **Dramatic Moment of Truth:** When a character takes some specific action or enters into a specific struggle that will determine the fate of the paradigm itself; the outcome will either change the paradigm or stabilize it.

#### Actors and Events

Actors are living and breathing entities that are recurring non player characters in the story. They are updated as the story progresses. Events are logs of the impactful exchanges, and hints of future storylines that are appended as summaries of past scenes.

### Story Stages

The game advances through **Stages** with specific story goals to help with pacing. Each stage is composed of many sequential **Scenes**, where each scene is planned to pursue a specific goal appropriate to the stage.

1. **"Set Up"**: after completing this stage, the story is 5-15% complete. Goals include: Introduce the story paradigm. Establish characters, establish motivations. Establish world details. Tease the story problem.
2. **"Rising Action"**: after completing this stage, the story is 15-30% complete. Goals include: Fully introduce the story problem, and how the main character is personally implicated. Main character begins to take action to solve the problem. Some clues may be discovered. The tension and conflict gradually increase as the protagonist faces challenges and obstacles.
3. **Quest**: after completing this stage, the story is 70-85% complete. Goals include: The hidden clues are pursued and discovered. Many cycles of tension and action. The character continues to explore and solve the dynamically evolving story, finding their way towards the decoy resolution. This is the longest stage, and the most scenes.
4. **"Climax"**: after completing this stage, the story is 90-95% complete. Goals include: Final clues are discovered. The decoy resolution is discovered to be fake, and the surprise twist is revealed. Lots of action and excitement.
5. **"Falling Action"**: after completing this stage, the story is fully complete. Goals include: The story problem is solved, and the protagonist reaches the ultimate resolution. This stage reflects on the character's journey, how the story problem was solved, and what the character learned from the experience, and the broader implications of the events on the story paradigm.

### Specifics of Scene Planning

Scenes in the story are the key building blocks. They might be composed of a character breaking into a room, or a tense negotiation, or a transitory trip to a new location. Scenes within the game oscillate between **"Conflict"** and **"Dilemma"** type Scenes. Formulated after the Scene and Sequel framework, but terminology is adjusted for clarity. The oscillation encourages both internal or world exploration based scenes, drawing out the tension, and action packed scenes upping the adrenaline and stakes. During the course of a **Scene**, much like table-top role playing games (RPGs), the player's actions have a varied chance of success or failure. The complexity of the player's action dictates the chance of failure. This encourages dynamism in the story, and thoughful creative participation of the part of the player. To encourage stakes, the player's actions may lead to **Catastrophic Failure**, ending the story game immediately. This occurs if the player's actions are risky and fail, or are, otherwise inadvisable, or too far outside the scope of the story. This mechanism is helpful for the DM to keep the game realistic, and on track. After ending prematurely, the player may reload a past state to resume the story from there. At the start of a scene, an appropriate duration for the scene is set according to the weight of the goal. Completion progress is tracked. If the player delays or wastes time, the game encourages the player towards a resolution, or introduces pressing events with increased urgency to keep pacing and the world dynamic.

#### Conflict and Dilemma

As a scene progresses, the game revises the components of the scene like a diffusion model, gradually unblurring the specific details. The initial components are deblurred first, and the final components are only fully deblurred as the scene ends.

Conflict and Dilemma scenes have differering Components:

##### Conflict Scene Components

A **Conflict** scene is a unit of story where the action happens. It drives the plot forward and escalates the stakes. It is composed of three key components: 
1. **Goal**: The protagonist has a specific, clear, and tangible goal they aim to achieve. This goal should be something that matters to the character and drives their actions. 
2. **Conflict**: As the protagonist attempts to achieve their goal, they encounter obstacles or opposition. This conflict creates tension and keeps the reader engaged. 
3. **Disaster**: The scene typically ends in a way that complicates matters for the protagonist. This disaster can be a complete failure, a partial success that leads to new problems, or an unexpected twist that makes the protagonist's situation more challenging. 

##### Dilemma Scene Components

A **Dilemma** sequel follows a Conflice scene and focuses on the character's emotional and cognitive responses to what just happened. It serves to provide depth and develop the character while setting up the next scene. A Dilemma sequel consists of three main components:
1. **Reaction**: The immediate emotional response of the protagonist to the disaster in the previous scene. If this scene comes first in the novel, the previous conflict is introduced as backstory. This reaction should be genuine and in line with the character's personality and situation.
2. **Dilemma**: After the initial reaction, the protagonist faces a dilemma. They must consider their options and the consequences of their next move. This stage allows the reader to understand the character's thought process and stakes involved.
3. **Decision**: The protagonist makes a decision on how to proceed, which leads directly into the goal of the next scene. This decision propels the story forward and maintains the narrative momentum.

##### Cycle of **Conflict** and **Dilemma**

The story progresses by alternating between Conflict and Dilemmas. A conflict presents action and conflict, ending with a disaster that complicates the protagonist's life. The Dilemma then allows the character to process these events, making a decision that sets up the goal for the next conflict. This cycle helps maintain a balance between fast-paced action and character development, keeping the reader engaged and invested in both the plot and the characters. Think of the story as a series of "rubber-bands." The player should be in a constant state of building tension, that is progressively released, only to be brought up to the next tension-building element.