from math import log10
import os
from pathlib import Path
import polars as pl
from tqdm.auto import tqdm
from typing import Union, List

def filter_fn(
    path: str,
    filter_column: str,
    target: str,
    retrieve_columns: Union[None, List[str]] = None,
)-> pl.DataFrame:
    """
    Flexible helper function to be used in conjunction with collect_ids.filter_fineweb.

    Given a path to a FineWeb DataFrame, filters by the given parameters.

    Args:
        path(str): Path to a FineWeb DataFrame.
        filter_column(str): Column which is to be filtered.
        target(str): Filters rows where the filter_column contains the target string.
        retrieve_columns(List[str]): Only loads retrieve_columns. If None, retrieves all columns.
    """
    possible_columns = pl.read_parquet_schema(path)
    if not filter_column in possible_columns:
        raise ValueError(f'{filter_column} not found. Please select from {possible_columns}')
    if retrieve_columns and not all(c in possible_columns for c in retrieve_columns):
        raise ValueError(f'Retrieve columns do not align with data. Please select from {possible_columns}')
    df = pl.read_parquet(path, columns=retrieve_columns)
    return df.filter(df[filter_column].str.contains(target))

def filter_fineweb(
    data_dir: str,
    filter_fn: object
)-> pl.DataFrame:
    """
    Iterates through a list of FineWeb files, applies a filter function, and combines results into a single DataFrame.

    Args:
        data(str):Directory where FineWeb parquet files are saved.
        filter_fn(object): Function that takes a filepath, loads it, filters it, and returns a pl.DataFrame.
    """
    output = pl.DataFrame()

    paths = [Path(data_dir, file) for file in os.listdir(data_dir) if file.endswith('.parquet')]
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