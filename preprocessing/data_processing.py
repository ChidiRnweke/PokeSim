import os
import json
from typing import Dict
import pandas as pd


def parsePlayer(playerDict: Dict, playerNumber: int):
    """Fills in the game state for a given playerNumber

    Args:
        playerDict (Dict): The raw gamestate of both players
        playerNumber (int): Index of a given playerNumber

    Returns:
        _type_: The parsed gameState updated with the data of the playerNumber
    """
    playerState = playerDict[playerNumber]
    pokemonState = playerState["pokemon"]
    gameState = {}
    for idx, pokemon in enumerate(pokemonState):
        gameState = _parseNameStatusHP(playerNumber, gameState, idx, pokemon)
        gameState = _parse_moves(playerNumber, gameState, idx, pokemon)
        gameState = _parse_stats(playerNumber, gameState, idx, pokemon)
        gameState = _parse_types(playerNumber, gameState, idx, pokemon)
        if pokemon["isActive"]:
            gameState[f"p{playerNumber+1}activeSpeed"] = pokemon["modifiedStats"]["spe"]
            gameState[f"p{playerNumber+1}activeHP"] = pokemon["hp"] / pokemon["maxhp"]

    gameState[f"p{playerNumber+1}pkmLeft"] = playerState["pokemonLeft"]
    gameState = _sumBST(playerNumber, gameState)
    gameState = _HPorder(playerNumber, gameState)
    return gameState


def _parseNameStatusHP(
    playerNumber: int, gameState: Dict, idx: int, pokemon: Dict
) -> Dict:
    """Helper function that parses the four straightforward variables

    Args:
        playerNumber (int): playerNumber 1 or 2
        gameState (Dict): The state of the entire game
        idx (int): The number of the pokemon being parsed
        pokemon (Dict): The state of the specific pokemon

    Returns:
        Dict: An updated version of the gameState
    """

    gameState[f"p{playerNumber+1}pkmn{idx+1}name"] = pokemon["speciesState"]["id"]
    if pokemon["status"] == "":
        gameState[f"p{playerNumber+1}pkmn{idx+1}status"] = "healthy"
    else:
        gameState[f"p{playerNumber+1}pkmn{idx+1}status"] = pokemon["status"]
    if pokemon["hp"] == 0:
        gameState[f"p{playerNumber+1}pkmn{idx+1}status"] = "fnt"
    gameState[f"p{playerNumber+1}pkmn{idx+1}RemainingHp"] = (
        pokemon["hp"] / pokemon["maxhp"]
    )

    return gameState


def _parse_stats(playerNumber: int, gameState: Dict, idx: int, pokemon: Dict) -> Dict:
    """Parses the modified stats of a given pokemon

    Args:
        playerNumber (int): playerNumber 1 or 2
        gameState (Dict): The state of the entire game
        idx (int): The number of the pokemon being parsed
        pokemon (Dict): The state of the specific pokemon

    Returns:
        Dict: An updated version of the gameState
    """

    for stat, value in pokemon["modifiedStats"].items():
        gameState[f"p{playerNumber+1}pkmn{idx+1}{stat}"] = value
    gameState[f"p{playerNumber+1}pkmn{idx+1}hp"] = pokemon["maxhp"]
    return gameState


def _parse_moves(playerNumber: int, gameState: Dict, idx: int, pokemon: Dict) -> Dict:
    """Parses the moves, special care is taken for pokemon with less than 3
    moves like Ditto

    Args:
        playerNumber (int): playerNumber 1 or 2
        gameState (Dict): The state of the entire game
        idx (int): The number of the pokemon being parsed
        pokemon (Dict): The state of the specific pokemon

    Returns:
        Dict: An updated version of the gameState
    """
    for moveidx, move in enumerate(pokemon["set"]["moves"]):
        gameState[f"p{playerNumber+1}pkmn{idx+1}move{moveidx+1}"] = move
    if len(pokemon["set"]["moves"]) < 4:
        movesToFill = 4 - len(pokemon["set"]["moves"])
        for i in range(movesToFill):
            moveidx = movesToFill - i
            gameState[f"p{playerNumber+1}pkmn{idx+1}move{moveidx+1}"] = "NoMove"
    return gameState


def _parse_types(playerNumber: int, gameState: Dict, idx: int, pokemon: Dict) -> Dict:
    """Parses the types of pokemon. If a pokemon only has one type, the second
    is consired to be the same as the first

    Args:
        playerNumber (int): playerNumber 1 or 2
        gameState (Dict): The state of the entire game
        idx (int): The number of the pokemon being parsed
        pokemon (Dict): The state of the specific pokemon

    Returns:
        Dict: An updated version of the gameState
    """
    gameState[f"p{playerNumber+1}pkmn{idx+1}type{1}"] = pokemon["types"][0]
    if len(pokemon["types"][0]) == 2:
        gameState[f"p{playerNumber+1}pkmn{idx+1}type{2}"] = pokemon["types"][1]
    else:
        gameState[f"p{playerNumber+1}pkmn{idx+1}type{2}"] = pokemon["types"][0]
    return gameState


def _sumBST(playerNumber: int, gameState: Dict) -> Dict:
    stats = ["atk", "def", "spa", "def", "spd", "spe", "hp"]
    gameState[f"p{playerNumber+1}sumBST"] = 0  # initialize
    for idx in range(6):
        if gameState[f"p{playerNumber+1}pkmn{idx+1}status"] == "fnt":
            pass
        else:
            for stat in stats:
                gameState[f"p{playerNumber+1}sumBST"] += gameState[
                    f"p{playerNumber+1}pkmn{idx+1}{stat}"
                ]
    return gameState


def _HPorder(playerNumber: int, gameState: Dict) -> Dict:
    hitpoints = []
    for idx in range(6):
        hitpoints.append(gameState[f"p{playerNumber+1}pkmn{idx+1}RemainingHp"])
    hitpoints = sorted(hitpoints)
    for idx, hp in enumerate(hitpoints):
        gameState[f"p{playerNumber+1}sortedHP{idx+1}"] = hp
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
        battlePath = os.path.join(dataPath, matchTurn)
        with open(battlePath) as file:

            sides = json.load(file)["sides"]
        p1Data = parsePlayer(sides, playerNumber=0)  # playerNumber 1
        p2Data = parsePlayer(sides, playerNumber=1)  # playerNumber 2
        turnData = {**p1Data, **p2Data}  # 1 big dict for both players
        turnData["pokemonLeftDiff"] = turnData[f"p1pkmLeft"] - turnData[f"p2pkmLeft"]
        turnData["match_turn"] = matchTurn  # 'primary key'

        parsedMatchTurns.append(turnData)

    return pd.DataFrame(parsedMatchTurns)
