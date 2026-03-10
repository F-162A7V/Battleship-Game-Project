# Battleship-Game-Project
What is the project about?
Basically 11th grade cyber student does his final project.

What is the intended result?
-------------------------------
A two-client pygame naval battle minigame, where every (shortest possible interval) a user sends his ship's state to the server, and recieves full game state from the server (to avoid sync issues)
The ships will have HP bars that can be lowered by firing shells to spots you predict your enemy will be at after impact. The winner will be the first to sink his enemy, or tie if ships collide/mutual death.

Protocol type: async
Protocol field seperator: byte string of: |`|
For more detailed info on protocol, check files.