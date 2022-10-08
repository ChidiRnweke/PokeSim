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
import pandas as pd


def parsePlayer(pokemonList, side):
    player = pokemonList[side]
    playerList = player["pokemon"]
    pokeState = {}
    for idx, pokemon in enumerate(playerList):
        pokeState = _parse_nameStatusTypeHp(side, pokeState, idx, pokemon)
        pokeState = _parse_moves(side, pokeState, idx, pokemon)
        pokeState = _parse_stats(side, pokeState, idx, pokemon)
        pokeState = _parse_types(side, pokeState, idx, pokemon)

    pokeState[f"p{side+1}pkmn{idx+1}pkmLeft"] = player["pokemonLeft"]
    return pokeState


def _parse_nameStatusTypeHp(side, pokeState, idx, pokemon):
    pokeState[f"p{side+1}pkmn{idx+1}name"] = pokemon["speciesState"]["id"]
    pokeState[f"p{side+1}pkmn{idx+1}status"] = pokemon["status"]
    pokeState[f"p{side+1}pkmn{idx+1}type{1}"] = pokemon["types"][0]
    pokeState[f"p{side+1}pkmn{idx+1}RemainingHp"] = pokemon["hp"]
    return pokeState


def _parse_stats(side, pokeState, idx, pokemon):
    for stat, value in pokemon["modifiedStats"].items():
        pokeState[f"p{side+1}pkmn{idx+1}{stat}"] = value
    return pokeState


def _parse_moves(side, pokeState, idx, pokemon):
    for moveidx, move in enumerate(pokemon["set"]["moves"]):
        pokeState[f"p{side+1}pkmn{idx+1}move{moveidx+1}"] = move
    if len(pokemon["set"]["moves"]) < 4:
        movesToFill = 4 - len(pokemon["set"]["moves"])
        for i in range(movesToFill):
            moveidx = movesToFill - i
            pokeState[f"p{side+1}pkmn{idx+1}move{moveidx+1}"] = "NoMove"
    return pokeState


def _parse_types(side, pokeState, idx, pokemon):
    if len(pokemon["types"][0]) == 2:
        pokeState[f"p{side+1}pkmn{idx+1}type{2}"] = pokemon["types"][1]
    else:
        pokeState[f"p{side+1}pkmn{idx+1}type{2}"] = pokemon["types"][0]
    return pokeState


def parseMatchTurns(folderName="data"):
    parsedMatchTurns = []
    dataPath = os.path.join(os.getcwd(), folderName)
    matchTurns = os.listdir(dataPath)

    for matchTurn in matchTurns:
        batlePath = os.path.join(dataPath, matchTurn)
        with open(batlePath) as file:
            sides = json.load(file)["sides"]
        p1Data = parsePlayer(sides, side=0)
        p2Data = parsePlayer(sides, side=1)
        turnData = {**p1Data, **p2Data}
        turnData["match_turn"] = matchTurn

        parsedMatchTurns.append(turnData)

    return pd.DataFrame(parsedMatchTurns)

