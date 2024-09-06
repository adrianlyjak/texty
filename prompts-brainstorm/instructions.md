# Story Generator

Story Generator is an AI powered interactive story game, similar to classic choose-your-own-adventure books, but with more potential for player agency. The AI fills the role of author and dungeon master. Their job is to iteratively plan and generate the story, adapting to the player's choices and actions.

The AI is controlled by piecemeal prompts, to execute the system defined in this document.

## Overall Story Structure

In order to pace and structure the story, the AI author/DM uses a 6 component story planning framework.

Primarily, there is a single story problem that drives the story forward. To reach the end, the player must encounter and solve clues. The player believes they are working towards a resolution. To avoid boring and obvious endings, this resolution, or at least a significant part of it, is a decoy. Right before reaching the obvious resolution, the player instead encounters a Surprise Twist, which subverts their expectations of the true nature of the story problem and its solution.

The overall direction and progress of the story is controlled by these 6 primary components:

1. The central **"Story Problem"**: This is the main conflict that the story is about. It should have stakes, and the the main character should be personally motivated in solving the story problem, but have some personal hangup that is getting in their way. Through the course of the story, the character will need to change in some way to solve the story problem.
2. The **"Story Paradigm"**: This is the overall situation of the character and the broader world and social environment. This describes the characters' normal day to day lives, obligations, and positions within the broader scope of their relationships and society.
3. The **"Hidden Clues"**: In solving the story problem, the player will need to explore the world of the story and uncover clues that will ultimately help them uncover the story's mystery and solve the story problem. These clues can take the form of puzzles, objects, information, or story shaping events. They relate and guide the story to one or more of the specific endings
4. The **"Decoy Resolution"**: This is the obvious resolution to the story problem, which the player believes they are working towards.
5. The **"Surprise Twist/Ultimate Resolution"**: When the player has successfully pieced together the necessary clues to reach a resolution, and is ready to solve the story problem, the story takes a surprising turn that subverts the player's expectations of the true nature of the story problem and its solution. This is the **Surprise Twist**, that leads to an **"Ultimate Resolution"**. With all the clues successfully assembled, what final action and/or challenge will the player need to take to resolve the story problem? How does the story end? What has the character discovered or changed about their world?

This is a choice driven generative game, so it contains multiple possible endings, which is expressed as multiple **Surprise Twist/Ultimate Resolution** pairs. The game tracks the probability of each ending as the story progresses.

## Adaptive Story Planning
- The game keeps an **"Opportunity Index"** of story components that are selected from as needed. The primary component of the Opportunity Index are **Hidden Clues**, but additionally there are **Characters**, **Scene Utilities**, and **Story Beats**. These are generally a grab bag of potentially good ideas to select from when planning each scene.
- The game tracks active **Actors**. These are characters, organizations, systems, etc. Anything that is an active stakeholder with internal motivations in the story problem. The game updates the active actors based on the story's progression.



## Adaptive Scene Planning

Given the competing parallel storylines, the path to reaching the end must be malleable and flexible, able to be morphed between the Ultimate Resolutions based on the character's actions. This is achieved with the following structures:

- The game plot is constructed of sequential **Scenes**, where each scene is paced to pursue an active story goal. 
- The Scenes oscillate between **"Conflict"** and **"Dilemma"** type Scenes (formulated after the Scene and Sequel framework. Terminology is adjusted for clarity).
- Aside from **Ultimate Resolutions**, the player's actions may lead to **Catastrophic Failure**, ending the story game immediately. This occurs if the player's actions are extremely risky, otherwise inadvisable, or too far outside the scope of the story. This mechanism is helpful for the DM to keep the game realistic and on track.
- During the course of a **Scene**, much like table-top role playing games (RPGs), the player's actions have a varied chance of success or failure. The complexity of the player's action dictates the chance of failure. This encourages dynamism in the story, and thoughful creative participation of the part of the player.

For the purpose of this game, a scene is defined as "The progression of a story goal." At the start of a scene, a general goal is set, along with a general size or complexity of the scene. The goal should be malleable enough that it can be solved by multiple potential paths, giving the player the agency to shape their path through the story. The complexity controls the duration, and is proportional to the impact of the goal. The stage of the progression is then plotted out, with larger sizes having longer progression.

### Conflict and Dilemma

#### Conflict 

A **Conflict** scene is a unit of story where the action happens. It drives the plot forward and is composed of three key components: 
1. **Goal**: The protagonist has a specific, clear, and tangible goal they aim to achieve. This goal should be something that matters to the character and drives their actions. 
2. **Conflict**: As the protagonist attempts to achieve their goal, they encounter obstacles or opposition. This conflict creates tension and keeps the reader engaged. 
3. **Disaster**: The scene typically ends in a way that complicates matters for the protagonist. This disaster can be a complete failure, a partial success that leads to new problems, or an unexpected twist that makes the protagonist's situation more challenging. 

#### Dilemma

A **Dilemma** sequel follows a Conflice scene and focuses on the character's emotional and cognitive responses to what just happened. It serves to provide depth and develop the character while setting up the next scene. A sequel consists of three main parts:
1. **Reaction**: The immediate emotional response of the protagonist to the disaster in the previous scene. This reaction should be genuine and in line with the character's personality and situation.
2. **Dilemma**: After the initial reaction, the protagonist faces a dilemma. They must consider their options and the consequences of their next move. This stage allows the reader to understand the character's thought process and stakes involved.
3. **Decision**: The protagonist makes a decision on how to proceed, which leads directly into the goal of the next scene. This decision propels the story forward and maintains the narrative momentum.

#### Cycle of **Conflict** and **Dilemma**

The story progresses by alternating between Conflict and Dilemmas. A conflict presents action and conflict, ending with a disaster that complicates the protagonist's life. The Dilemma then allows the character to process these events, making a decision that sets up the goal for the next conflict. This cycle helps maintain a balance between fast-paced action and character development, keeping the reader engaged and invested in both the plot and the characters.