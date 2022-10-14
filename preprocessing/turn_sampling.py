from types import FunctionType
import pandas as pd
import numpy as np


def randomStrategy(labels_df: pd.DataFrame) -> pd.DataFrame:
    """To prevent leakage different turn instances of the same match
    cannot be included in train and test at the same time.
    To prevent this the dataset can be reduced to only contain one
    random sample of a given match. This ensures that this will not
    occur.

    Args:
        labels_df (pd.DataFrame): dataset containing the labels.

    Returns:
        pd.DataFrame: A dataset containing one random sample per group.
    """
    return (
        labels_df.groupby("match")
        .apply(pd.DataFrame.sample, n=1)
        .reset_index(drop=True)
    )


def secondLastStrategy(labels_df: pd.DataFrame) -> pd.DataFrame:
    """To prevent leakage different turn instances of the same match
    cannot be included in train and test at the same time.
    To prevent this the dataset can be reduced to only
    the second last sample per group. This ensures that this will not
    occur.

    Args:
        labels_df (pd.DataFrame): dataset containing the labels.

    Returns:
        pd.DataFrame: A dataset containing one sample per group.
    """
    return (
        labels_df.sort_values(["match", "turnNumber"], ascending=True)
        .groupby("match")
        .last()
    )


def firstStrategy(labels_df: pd.DataFrame) -> pd.DataFrame:
    """To prevent leakage different turn instances of the same match
    cannot be included in train and test at the same time.
    To prevent this the dataset can be reduced to only
    the first sample per group. This ensures that this will not
    occur.

    Args:
        labels_df (pd.DataFrame): dataset containing the labels.

    Returns:
        pd.DataFrame: A dataset containing one sample per group.
    """
    return (
        labels_df.sort_values(["match", "turnNumber"], ascending=True)
        .groupby("match")
        .first()
    )


def middleStrategy(labels_df: pd.DataFrame) -> pd.DataFrame:
    """To prevent leakage different turn instances of the same match
    cannot be included in train and test at the same time.
    To prevent this the dataset can be reduced to only
    the middle sample per group. This ensures that this will not
    occur.

    Args:
        labels_df (pd.DataFrame): dataset containing the labels.

    Returns:
        pd.DataFrame: A dataset containing one sample per group.
    """
    labels_df = labels_df.sort_values(["match", "turnNumber"], ascending=True)
    labels_df["index"] = pd.RangeIndex(stop=labels_df.shape[0])
    idxpos = (
        labels_df.groupby(
            "match", sort=False, as_index=False, group_keys=False, dropna=False
        )["index"]
        .agg(["first", "count"])
        .values
    )
    # Create middle rows position vector
    idxmid = idxpos[:, 0] + idxpos[:, 1] // 2
    # Extract them and drop the index that we created
    df_mids = labels_df.iloc[idxmid].drop("index", axis=1)
    return df_mids


def entireMatchStrategy(labels_df: pd.DataFrame, proportion=0.3) -> pd.DataFrame:
    """To prevent leakage different turn instances of the same match
    cannot be included in train and test at the same time.
    To prevent this the dataset can be split into having multiple
    state instances in training OR test. The same instances may
    not occur in both. To guarantee this you must use group
    K-fold as a validation strategy

    Args:
        labels_df (pd.DataFrame): dataset containing the labels.

    Returns:
        (pd.DataFrame, pd.Dataframe): train and test
    """
    groups = pd.unique(labels_df.match)
    count = len(groups)
    sampleCount = int(np.round(count * proportion))
    testMatches = np.random.choice(a=groups, size=sampleCount, replace=False)

    train = np.in1d(labels_df["match"], testMatches)
    test = np.in1d(labels_df["match"], testMatches, invert=True)
    return labels_df[train], labels_df[test]


def sampleTurns(data, strategy: FunctionType = randomStrategy) -> pd.DataFrame:
    return strategy(data)
