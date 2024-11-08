# Taiwan Tourist Monopoly
## Video Demo: https://youtu.be/1OMiORdSuYQ
## Description: 

This version of Monopoly is designed with simplicity in mind and is primarily based on Pygame. It features popular tourist attractions in Taiwan and offers a fun and engaging experience for players.

## Game Setup

1. **Player Selection**: At the start of the game, players can choose the number of participants, ranging from two to four. The players are represented by different colors.
2. **Game Rules**: The rules of the game are displayed on the player selection page.
3. **Automatic Start**: Once the number of players is chosen, the game begins automatically.

## Game Board

The game board consists of blocks representing famous tourist attractions in Taiwan, divided into four regions:
- **North**: Located at the top of the board.
- **East**: Located on the left side.
- **Central**: Located on the right side.
- **South**: Located at the bottom.

### Special Blocks

- **Fate and Chance Blocks**: Each region has a Fate and Chance block. When a player lands on one of these blocks, they draw a card and follow the instructions.
- **Corners**:
  - **Top Left**: The starting point for all players.
  - **Top Right**: High-Speed Rail Station, connected to the bottom left. Players landing on one of these will be transported to the other.
  - **Bottom Right**: Jail. Players landing here miss one round. However, they can roll the dice during their suspended round; rolling a six allows them to escape immediately.

## Gameplay

- **Block Information**: Hovering the mouse over any block displays a window with information about that block.
- **Winning Condition**: The game ends when a player loses all their money. The winner is the player with the most money remaining.

## File Description

### Monopoly.py
This is the main program that runs the game.

### dice
This folder contains images of the six faces of a die.

### properties.csv
This CSV file contains information about the tourist attractions displayed on the blocks. You can easily update the block information by replacing this file.

### pictures
This folder contains images of the attractions that are shown in a window when you hover over a block.

## Fate and Chance Cards

Here are the Fate and Chance cards included in the game:

1. The Queen's Head at Yehliu has broken, toll fees in the northern region are halved.

2. The government is issuing travel subsidies; players with properties in the north, center, south, and east regions will receive $500.

3. A power outage on the high-speed rail causes the player to skip the next turn.

4. Due to excess government tax revenue, everyone receives $300.

5. A typhoon devastates the south, destroying all properties in the southern region.

6. A strong earthquake hits the east, destroying all constructions. All properties in the eastern region disappear. Players with affected properties receive a $1000 government consolation fund.

7. Rent increases in the central region, doubling the toll fees.

8. In celebration of National Taiwan University's global ranking improvement, toll fees in the northern region are doubled.

9. Use an attack card, causing the next player to skip a turn. Players already in jail are unaffected.

10. Gain a teleportation door, allowing the player to go directly back to the start.

11. Use an attack card to steal $500 from the previous player.

12. You encounter a robber, and your money decreases by $500.

## Code Description

### Classes

#### boardattr
At the beginning, the program opens the `properties.csv` file to read all the information about the blocks. This class stores all the information for each block read from the CSV file and creates an array to store the sequence of the blocks.

#### Button
To create a button, we instantiate the Button class, which stores all the attributes of a button. This class includes functions for checking hover status, checking clicks, and drawing the button. The check_hover function checks if the mouse is hovering over the button, changing its color when it does. The check_click function determines if the button has been clicked. Finally, the draw function renders the button in the assigned location.

#### People
This class primarily stores information about a player, including attributes related to Fate and Chance cards.

### Functions

#### draw_text and wrap_text
The wrap_text function separates a string into an array of strings based on the maximum width. The draw_text function calls wrap_text and prints the text in order.

#### draw_board
This function renders the game board, ensuring the text on each side of the blocks is displayed in the correct orientation.

#### draw_player
This function prints the symbol of each player on the block where they are currently located.

#### draw_current_player_message
This function displays the current player to notify all players whose turn it is.

#### draw_player_money
This function shows the balance of each player on the board.

### Main Gaming Code

The main gaming logic is encapsulated in a large for loop that detects events. When the roll dice button is clicked, the player's turn begins. The player rolls a dice, and the program calculates where the player will land. If the player passes the start block, they receive $500.

If the player lands on an unowned block and has sufficient funds, they can choose to buy the block. If the block is owned by another player, the player must pay a toll to the owner. If the player lands on a Chance or Fate block, a random number between 0 and 11 is drawn to determine the card they receive, which is then immediately implemented.

Landing on the Jail block changes the player's status to 1, suspending them for one turn unless they roll a 6. Landing on a High-Speed Rail (HSR) Station transports the player to the other HSR Station. If the move passes the start block, the player receives $500.

After the turn ends, the program checks if the current player's balance is positive. If not, the game ends.
