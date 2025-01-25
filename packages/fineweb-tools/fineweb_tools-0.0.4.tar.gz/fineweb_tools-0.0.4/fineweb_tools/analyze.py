from math import log10
import os
from pathlib import Path
import polars as pl
from tqdm.auto import tqdm
from typing import Literal

def filter_fineweb(
    data: str,
    filter_fn: object,
)-> pl.DataFrame:
    """
    Flexible function that will iterate through files, filter data, and compile into a single DataFrame.

    Args:
        data(str): Either an explicit path to a parquet DataFrame or a directory where parquet files are saved.
        filter_fn(object): Function that takes a filepath, loads it, filters it, and returns a pl.DataFrame.
    """
    output = pl.DataFrame()

    if os.path.isdir(data):
        paths = [Path(data, file) for file in os.listdir(data) if file.endswith('.parquet')]
        if len(paths) == 0:
            raise ValueError(f'No parquet files found in {data}. Please either provide an explicit path to a parquet DataFrame or a path to a directory where parquet files are saved.')
    elif data.endwith('.parquet'):
        paths = [data]
    else:
        raise ValueError
    for path in tqdm(paths, desc='Filtering FineWeb'):
        filtered = filter_fn(path)
        if not isinstance(filtered, pl.DataFrame):
            raise TypeError(f"Input filter function should return a pl.DataFrame. {type(filtered)} returned. Please check your filter function.")
        output = pl.concat([output, filtered])
    return output
    
def group_domains_by_count(
        df: pl.DataFrame,
        group_fn: object = lambda x: int(log10(x))
):
    """
    Grouping function rigidly configured for analysis of the DataFrame yielded by preprocessing.
    Check fineweb_tools.preprocess.download_and_preprocess_pipeline.

    Given a preprocessed DataFrame, groups domains by the number of pages they contributed.

    Args:
        df (pl.DataFrame): Preprocessed dataframe to group.
        group_fn (object): Defaults to grouping by log10.
    """
    # Create the DataFrame and add the 'group' column
    df = df.with_columns(
        pl.col("count").map_elements(group_fn, return_dtype=pl.Int32).alias("group")
    )

    # First, we calculate the total sum of 'count' for the entire dataset
    total_url_sum = df.select(pl.sum("count")).to_numpy()[0][0]

    # Grouping and aggregating
    result = (
        df.group_by("group")
        .agg([
            pl.min("count").alias("group_min"),   # Min of 'count' within the group
            pl.max("count").alias("group_max"),   # Max of 'count' within the group
            pl.count("domain").alias("domains"),  # Count of domain entries per group
            pl.sum("count").alias("pages")   # Sum of 'count' per group
        ])
        .with_columns(
            # Adding the 'corpus_perc' column as the percentage of the total sum
            ((pl.col("pages") / total_url_sum * 100).round(2)).alias("corpus_perc")
        )

    ).sort('group')

    print ('Total Domains:', f"{result['domains'].sum():,}")
    print ('Total URLs:', f"{result['pages'].sum():,}")
    return result