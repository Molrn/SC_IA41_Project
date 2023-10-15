# Chess Sequence Recognition Module
## About the Project
This project is a module which intends to find the shortest sequence of moves from an initial chess position to a final position. In the final position, the pieces types aren't recognized, all that is known is their color.  
The module finds its usage when digitalizing chess games using image recognition, as intended in the project SharlyChess. It is an alternative to using shape recognition for pieces, which can be a heavy computation with a low success rate.  
This project is a [UTBM](https://www.utbm.fr/) student project realized as a part of the UV [IA41](https://guideuv.utbm.fr/#!/Fr/2021/GI/IA41). It also is a part of the project SharlyChess.  

## Getting started
This project is written in python, and requires the module chess. 
```
pip install chess
```
To run it, execute the [main.py](main.py) file.
```
python main.py
```
As it is a proof of concept, the module uses a console based interface. It could be implemented as a command line interface for other usages.

## Module description
The module takes as input 2 chess boards in [FEN](https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation) format, one for the initial board and one for the target. The target is then converted into a ColorBoard, which is a mapping of the squares and the piece colors of the position.  
To go from the initial position to the target, the [search alogrithm A*](https://en.wikipedia.org/wiki/A*_search_algorithm) is used. A* uses nodes to build a search tree, and heuristic to determine which node to explore first. In our case the nodes are chess positions, and going from one node to its child consists in playing a chess move. The heuristic is the sum of the number of different squares and the piece difference from the node position to the target position.
