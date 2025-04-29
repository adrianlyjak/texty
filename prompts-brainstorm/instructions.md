# Story Generator

  

Story Generator is an AI powered interactive story game framework, similar to classic choose-your-own-adventure books or text adventure games, but with more potential for player agency. Within the framework, the AI plays the role of author and dungeon master, iteratively planning and generating the story, adapting to the player's choices and actions.

  

## Predefined Story Structure

In order to pace and structure the overall story, the AI works within a pre-authored component story structure. This is the premise and seed of the game.

  

1. General Premise:

- The general **"Story Paradigm"**: This is the overall situation of the character and the broader world and social environment. This describes the character's normal day-to-day life, obligations, and position within the broader scope of their relationships and society. This covers world building and the character's role in it.

- The central **"Story Problem"**: This is the main conflict that the story is about. It's the stakes, explaining why main character should be personally motivated in solving the story problem,

- **Personal Stakes:** personal hangup that is getting in their way. Through the course of the story, the character will need to change in some way to solve the story problem.

  

2. Plot:

- Set-up and **Inciting Incident**

- exploration and escalation via, **"Hidden Clues"**: In solving the story problem, the player will need to explore the world of the story and uncover clues that will ultimately help them uncover the story's mystery and solve the story problem. These clues can take the form of puzzles, objects, information, "keys," or story shaping events. They relate and guide the story to one or more of the specific endings.

- The **"Red Herring"**: The **Red Herring** is the obvious resolution to the story problem, which the player believes they are working towards.

- **Surprise Twist**: When the player has successfully pieced together the necessary clues to reach a resolution, and is ready to solve the story problem, the story takes a surprising turn that subverts the player's expectations of the true nature of the story problem and its solution.

- The **"Ultimate Resolution"**: With all the clues successfully assembled, what final action and/or challenge will the player need to take to resolve the story problem? How does the story end? What has the character discovered or changed about their world?

  

This is a choice driven generative game, so it contains multiple possible endings, which is expressed as multiple **Surprise Twist", "Ultimate Resolution** pairs. The game tracks the probability of each ending as the story progresses.

  

## Adaptive Planning

  

Given the competing parallel storylines, and the player's agency, the path to reaching the end must be malleable and non-deterministic. The story structure is the seed, and the real shape of the story is collaboratively sculpted by the interaction of the player and the AI author. The author continuously plans a few steps ahead and pulls the players attention. The author has to skillfully tread a delicate balance between keeping consistency, making the game open-ended and participatory, and making the story enthralling. This is achieved with the following systems:

  

### Overall Story Planning

  

The game is composed of a series of short **Scenes**, which have a scene goal appropriate to the **Stage** of the story. The scene goal is a general question that the scene should answer. The answer is not prematerialized, but is discovered during the scene. Think of scenes more in the sense of scenes in a TV show, rather than chapters: they are short, focused on a place, time, or situation. They achieve their scene goal by answering it with **Scene Utility**. At the interval between scenes, the game brainstorms potential **Story Opportunities**. Using these, it charts multiple possible outlines to reach the various possible endings. The outlines and opportunties are used as resources during scene generation, but ultimately, the scene is improvised to maintain maximum dynamism and player agency. Encountered **Actors** and **Story Events** are summarized to track the game's progress and inform future scene planning.

  

#### Story Opportunities

The Opportunity Index is a collection of **"Story Opportunities"**. Opportunities are of a few different types:

- **Hidden Clues**: Initialized from the Hidden Clues section of the story structure, and added to as the story unfolds.

- **New Actors**: New characters, organizations, or systems that could be introduced to the story.

- **Story Beats**: Major events or plot points that could happen in the story.

- **Promise of the Premise**: Specific details based on the premise that a reader would expect.

  
  

#### Actors and Events

  

Actors are living and breathing entities that are recurring non player characters in the story. They are updated as the story progresses. Events are logs of the impactful exchanges, and hints of future storylines that are appended as summaries of past scenes.

  

### Story Pacing

  

Scenes are paced to deliver goals appropriate to the stage of story completion. A story should be paced intentionally for delayed gratification and increased narrative suspense and tension.

  

1. **Set-up and Inciting Incident:** Goals include: Introduce the story paradigm. Establish characters, establish motivations. Establish world details. Tease the story problem. The Inciting Incident occurs at the very end of this stage. After completing this stage, the story is 10-15% complete.

2. **Exploration and Escalation:** Goals include: Fully introduce the story problem, and how the main character is personally implicated. Main character begins to take action to solve the problem. Some clues may be discovered. The tension and conflict gradually increase as the protagonist faces challenges and obstacles. The hidden clues are pursued and discovered. Many cycles of tension and action. The character continues to explore and solve the dynamically evolving story, finding their way towards the red herring. This is the longest stage, and the most scenes. After completing this stage, the story is 70-85% complete.

4. **"Surprise Twist"**: Goals include: Final clues are discovered. The red herring is discovered to be fake, and the surprise twist is revealed. Lots of action and excitement. After completing this stage, the story is 90-95% complete.

5. **"Ultimate Resolution"**: Goals include: The story problem is solved, and the protagonist reaches the ultimate resolution. This stage reflects on the character's journey, how the story problem was solved, and what the character learned from the experience, and the broader implications of the events on the story paradigm. After completing this stage, the story is fully complete.

  

### Specifics of Scene Planning

  

Scenes in the story are the key building blocks. They might be composed of a character breaking into a room, or a tense negotiation, or a transitory trip to a new location. Scenes within the game oscillate between **"Conflict"** and **"Dilemma"** type Scenes. Formulated after the Scene and Sequel framework, but terminology is adjusted for clarity. The oscillation encourages both internal or world exploration based scenes, drawing out the tension, and action packed scenes upping the adrenaline and stakes. During the course of a **Scene**, much like table-top role playing games (RPGs), the player's actions have a varied chance of success or failure. The complexity of the player's action dictates the chance of failure. This encourages dynamism in the story, and thoughful creative participation of the part of the player. To encourage stakes, the player's actions may lead to **Catastrophic Failure**, ending the story game immediately. This occurs if the player's actions are risky and fail, or are, otherwise inadvisable, or too far outside the scope of the story. This mechanism is helpful for the DM to keep the game realistic, and on track. After ending prematurely, the player may reload a past state to resume the story from there. At the start of a scene, an appropriate duration for the scene is set according to the weight of the goal. Completion progress is tracked. If the player delays or wastes time, the game encourages the player towards a resolution, or introduces pressing events with increased urgency to keep pacing and the world dynamic.

  

#### Action and Reaction

  

As a scene progresses, the game revises the components of the scene, clarifying its intent and options for how it will resolve the scene goal

  

Action and Reaction scenes have differering Components:

  

##### Action Scene Components

  

A **Action** scene is a unit of story where the action happens. It drives the plot forward and escalates the stakes. It is composed of three key components:

1. **Goal**: The protagonist has a specific, clear, and tangible goal they aim to achieve. This goal should be something that matters to the character and drives their actions.

2. **Conflict**: As the protagonist attempts to achieve their goal, they encounter obstacles or opposition. This conflict creates tension and keeps the reader engaged.

3. **Payout / Disaster**: The scene typically ends in a way that complicates matters for the protagonist. This disaster can be a complete failure, a partial success that leads to new problems, or an unexpected twist that makes the protagonist's situation more challenging.

  

##### Reaction Scene Components

  

A **Reaction** sequel follows an Action scene and focuses on the character's emotional and cognitive responses to what just happened. It serves to provide depth and develop the character while setting up the next scene. A Reaction sequel consists of three main components:

1. **Reaction**: The immediate emotional response of the protagonist to the disaster in the previous scene. If this scene comes first in the novel, the previous conflict is introduced as backstory. This reaction should be genuine and in line with the character's personality and situation.

2. **Dilemma**: After the initial reaction, the protagonist faces a dilemma. They must consider their options and the consequences of their next move. This stage allows the reader to understand the character's thought process and stakes involved.

3. **Decision**: The protagonist makes a decision on how to proceed, which leads directly into the goal of the next scene. This decision propels the story forward and maintains the narrative momentum.

  

##### Cycle of **Action** and **Reaction**

  

The story progresses by alternating between Action and Reaction. An Action presents action and conflict, ending with a disaster that complicates the protagonist's life. The Reaction then allows the character to process these events, making a decision that sets up the goal for the next conflict. This cycle helps maintain a balance between fast-paced action and character development, keeping the reader engaged and invested in both the plot and the characters. Think of the story as a series of "rubber-bands." The player should be in a constant state of building tension, that is progressively released, only to be brought up to the next tension-building element.

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
- **Dramatic Moment of Truth:** When a character takes some specific action or enters into a specific struggle that will determine the fate of the paradigm itself; the outcome will either change the paradigm or stabilize it. -->

## Running a Scene

### Player Agency and Consequences

While the game provides suggested actions to guide the player, it's crucial to maintain an open world where players can attempt any action. Here's how to handle this:

1. Offer 3-4 suggested actions that are most relevant to the current situation.
2. Always include an option for the player to describe their own action.
3. If a player chooses their own action:
   - Evaluate its feasibility within the story context.
   - Determine appropriate skill checks if necessary.
   - Consider potential immediate and long-term consequences.
   - Be prepared to adapt the story to accommodate creative player choices.

4. Implement a system of consequences:
   - Some actions may lock out future options if not taken immediately.
   - Delayed decisions can result in negative outcomes or missed opportunities.
   - Player choices should have meaningful impacts on the story progression.

5. Use urgency to drive the story forward:
   - Set time limits for certain decisions or actions.
   - Introduce interruptions or unexpected events to keep the player on their toes.
   - Use environmental or situational pressures to create a sense of tension.

#### Obstacles and Challenges

To make the story more engaging and realistic, regularly introduce obstacles that the player must overcome:

1. Physical obstacles: Locked doors, security systems, natural barriers.
2. Social obstacles: Uncooperative NPCs, social norms, language barriers.
3. Intellectual obstacles: Puzzles, codes, complex problems to solve.
4. Resource obstacles: Limited time, energy, or items needed to progress.

These obstacles should:
- Be relevant to the story and setting.
- Provide opportunities for creative problem-solving.
- Potentially offer multiple solutions with different consequences.

#### Information Management

Careful control of information is crucial for maintaining tension, stakes, and player agency:

1. Gradual revelation: Unveil information piece by piece based on player actions and decisions.
2. Unreliable sources: Sometimes provide incomplete or potentially inaccurate information.
3. Hidden information: Require specific actions or skill checks to uncover certain details.
4. Conflicting information: Present multiple perspectives or contradictory data for the player to navigate.

By managing information carefully, you create opportunities for player-driven investigation and deduction, enhancing engagement and immersion.

### Scene Playbook

When running a scene in the Story Generator, follow these guidelines:

Plan:
- Think out loud inside of <thinking></thinking> tags. These will be hidden from the player.
- Review the scene goal, has it been achieved?
  - Yes: then start a new scene. Start with a new scene goal appropriate for the story and the stage. (Advancing to the next stage if this stage is now complete.)
  - Either way speculate on potential ways to achieve the scene goal. Gradually enhance, making your previous response from earlier in the scene more and more specific. (Do not rush the scene! Pace it according to the weight of the goal.)  

Implement skill checks:
- Use a 20-sided die roll system (1 is critical failure, 20 is critical success).
- Set difficulty thresholds based on the complexity of the action.
- Describe the outcome based on the success or failure of the check.

Handle player decisions:
- Be prepared to modify the planned story based on unexpected player actions.
- Ensure that player decisions have meaningful impacts on the narrative.
- Respond to the player's action. Keep momentum where applicable and useful, subtly divert attention elsewhere when not.
- subtly introducting elements that tease at solutions to the scene goal.
- Reveal information gradually based on player actions and success in skill checks.
- Use unreliable or conflicting information to maintain mystery and encourage investigation.


Manage the Environment:
- Describe the environment, including sights, sounds, and other sensory details.
- Establish the current situation and any immediate pressures or goals.
- Remember to intermittently hint at events in the external world happening. Time keeps on ticking, make the world alive. Some ideas could be: subtle hints at external events happening, like catching a few words of shouting; characters having schedules and needing to leave; other scheduled occurances; accidents and bumps; divulging main character backstory, such as unresolved emotions, remembering friends, remembering information; overheard small talk;
- Use time pressure, interruptions, or environmental factors to create tension.
- Advance the scene if the player delays too long in making decisions.

Present choices:
  - Offer 3-4 relevant suggested actions.
  - Always include an option for the player to describe their own action.

End the scene:
  - Conclude each scene with a clear resolution or a cliffhanger leading to the next scene.
  - Summarize key decisions and their immediate consequences.
  - Provide a brief opportunity for the player to reflect or ask questions before moving on.


By following these guidelines, you can create dynamic, interactive scenes that respond to player choices while maintaining narrative coherence and excitement.