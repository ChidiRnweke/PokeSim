import os
import json
from typing import Dict, List
import pandas as pd


def create_labels(folderName: str) -> pd.DataFrame:
    """Constructs labels for each of the turns generated from the matches.

    Args:
        folderName (str): folder that contains the data

    Returns:
        pd.DataFrame: DataFrame with the following columns
                      match_turn: file name of the match turn
                      winner: Bot 1 or bot 2
                      match: the match to which the turn belongs
                      turnNumber: the turn number
                      isLast: if the turn number is the last turn
    """
    dataPath = os.path.join(os.getcwd(), folderName)
    battleTurns = os.listdir(dataPath)

    matchTurns = [turn.split("-turn") for turn in battleTurns]

    # Constructs the matchMap: Match => List[turn]
    matchMap = _createMatchMap(matchTurns)
    # Finds the winner, last turn and turn number for each turn
    labels = _createTurnLabels(dataPath, matchMap)

    labels_df = pd.DataFrame(labels.items(), columns=["match_turn", "winner"])
    labels_df[["match", "turnNumber", "isLast", "winner"]] = pd.DataFrame(
        labels_df.winner.tolist()
    )
    return labels_df


def _createMatchMap(matchTurns: List[str]) -> Dict[str, List[int]]:
    """Helper function that maps a match to a list of turns

    Args:
        matchTurns (List[str]): List of all the match - turns

    Returns:
        Dict[str, List[int]]: For each match a list of turns
    """
    matchMap = {}
    for match in matchTurns:
        matchName = match[0]
        turnNumber = int(match[1].split(".txt")[0])
        if matchName in matchMap:
            matchMap[matchName].append(turnNumber)
        else:
            matchMap[matchName] = [turnNumber]
    return matchMap


def _createTurnLabels(dataPath: str, matchMap: Dict[str, List[int]]) -> Dict[str, List]:
    """Helper function that turns the matchMap into the associated labels

    Args:
        dataPath (str): path to data folder
        matchMap (Dict[str, List[int]]): For each match a list of turns

    Returns:
        Dict[str, List]: For each match the labels and metadata
    """
    labels = {}
    for match, turnList in matchMap.items():
        last = max(turnList)
        fileName = f"{match}-turn{last}.txt"
        battleOutcomePath = os.path.join(dataPath, fileName)
        with open(battleOutcomePath) as file:
            outcome = json.load(file)["winner"]
        for turnNumber in turnList:
            isLast = turnNumber == last
            matchTurn = f"{match}-turn{turnNumber}.txt"
            labels[matchTurn] = [match, turnNumber, isLast, outcome]
    return labels


labels = create_labels("data")
labels.to_csv("cleaned_data/labels.csv")
