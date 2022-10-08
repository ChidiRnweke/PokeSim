# First, most basic feature: pokémon difference between p1 and p2
# => model
# + sorted list of HP remaining
# => Model
# + base stat totals
# => Model
# Map moves to types (think of a smarter feature)
# => Model
# Additional features: status? active mon speed? Boosts?

import os
import json
from typing import Dict
import pandas as pd


def parsePlayer(playerDict: Dict, player: int):
    """Fills in the game state for a given player

    Args:
        playerDict (Dict): The raw gamestate of both players
        player (int): Index of a given player

    Returns:
        _type_: The parsed gameState updated with the data of the player
    """
    playerState = playerDict[player]
    playerList = playerState["pokemon"]
    gameState = {}
    for idx, pokemon in enumerate(playerList):
        gameState = _parse_nameStatusTypeHp(player, gameState, idx, pokemon)
        gameState = _parse_moves(player, gameState, idx, pokemon)
        gameState = _parse_stats(player, gameState, idx, pokemon)
        gameState = _parse_types(player, gameState, idx, pokemon)

    gameState[f"p{player+1}pkmn{idx+1}pkmLeft"] = playerState["pokemonLeft"]
    return gameState


def _parse_nameStatusTypeHp(
    player: int, gameState: Dict, idx: int, pokemon: Dict
) -> Dict:
    """Helper function that parses the four straightforward variables

    Args:
        player (int): player 1 or 2
        gameState (Dict): The state of the entire game
        idx (int): The number of the pokemon being parsed
        pokemon (Dict): The state of the specific pokemon

    Returns:
        Dict: An updated version of the gameState
    """

    gameState[f"p{player+1}pkmn{idx+1}name"] = pokemon["speciesState"]["id"]
    gameState[f"p{player+1}pkmn{idx+1}status"] = pokemon["status"]
    gameState[f"p{player+1}pkmn{idx+1}type{1}"] = pokemon["types"][0]
    gameState[f"p{player+1}pkmn{idx+1}RemainingHp"] = pokemon["hp"]
    return gameState


def _parse_stats(player: int, gameState: Dict, idx: int, pokemon: Dict) -> Dict:
    """Parses the modified stats of a given pokemon

    Args:
        player (int): player 1 or 2
        gameState (Dict): The state of the entire game
        idx (int): The number of the pokemon being parsed
        pokemon (Dict): The state of the specific pokemon

    Returns:
        Dict: An updated version of the gameState
    """

    for stat, value in pokemon["modifiedStats"].items():
        gameState[f"p{player+1}pkmn{idx+1}{stat}"] = value
    return gameState


def _parse_moves(player: int, gameState: Dict, idx: int, pokemon: Dict) -> Dict:
    """Parses the moves, special care is taken for pokemon with less than 3
    moves like Ditto

    Args:
        player (int): player 1 or 2
        gameState (Dict): The state of the entire game
        idx (int): The number of the pokemon being parsed
        pokemon (Dict): The state of the specific pokemon

    Returns:
        Dict: An updated version of the gameState
    """
    for moveidx, move in enumerate(pokemon["set"]["moves"]):
        gameState[f"p{player+1}pkmn{idx+1}move{moveidx+1}"] = move
    if len(pokemon["set"]["moves"]) < 4:
        movesToFill = 4 - len(pokemon["set"]["moves"])
        for i in range(movesToFill):
            moveidx = movesToFill - i
            gameState[f"p{player+1}pkmn{idx+1}move{moveidx+1}"] = "NoMove"
    return gameState


def _parse_types(player: int, gameState: Dict, idx: int, pokemon: Dict) -> Dict:
    """Parses the types of pokemon. If a pokemon only has one type, the second
    is consired to be the same as the first

    Args:
        player (int): player 1 or 2
        gameState (Dict): The state of the entire game
        idx (int): The number of the pokemon being parsed
        pokemon (Dict): The state of the specific pokemon

    Returns:
        Dict: An updated version of the gameState
    """
    if len(pokemon["types"][0]) == 2:
        gameState[f"p{player+1}pkmn{idx+1}type{2}"] = pokemon["types"][1]
    else:
        gameState[f"p{player+1}pkmn{idx+1}type{2}"] = pokemon["types"][0]
    return gameState


def parseMatchTurns(folderName: str = "data") -> pd.DataFrame:
    """_summary_

    Args:
        folderName (str, optional): The name of the folder that contains
        the data. Defaults to "data".

    Returns:
        DataFrame: A dataframe containing the game state for all the games
        in the folder.
    """
    parsedMatchTurns = []
    dataPath = os.path.join(os.getcwd(), folderName)
    matchTurns = os.listdir(dataPath)

    for matchTurn in matchTurns:
        batlePath = os.path.join(dataPath, matchTurn)
        with open(batlePath) as file:
            sides = json.load(file)["sides"]
        p1Data = parsePlayer(sides, player=0)  # player 1
        p2Data = parsePlayer(sides, player=1)  # player 2
        turnData = {**p1Data, **p2Data}  # 1 big dict for both players
        turnData["match_turn"] = matchTurn  # 'primary key'

        parsedMatchTurns.append(turnData)

    return pd.DataFrame(parsedMatchTurns)


cleanedData = parseMatchTurns("data")
