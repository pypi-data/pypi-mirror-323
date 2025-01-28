from huggingface_hub import (
    hf_hub_download,
    list_repo_files
)
import os
from pathlib import Path
import polars as pl
import random
from shutil import rmtree
from tld import get_tld
from tqdm.auto import tqdm
from typing import List, Dict
from urllib.parse import urlparse

def get_fineweb_paths(language = "")-> List[str]:
    """Helper function that queries the FineWeb repository and returns all train files."""
    paths =  [
        path
        for path in list_repo_files("HuggingFaceFW/fineweb-2", repo_type="dataset")
        if path.endswith("parquet")
        and "removed" not in path
        and "train" in path
    ]
    if language:
        paths = [path for path in paths if language in path]
    return paths

def get_fineweb_languages()-> List[str]:
    """Helper function that collects all languages from the FineWeb repository."""
    paths = get_fineweb_paths()
    return list(set([path.split('/')[1] for path in paths]))

def get_io_paths(language, output_dir: str='FineWeb')-> Dict[str, Path]:
    """Helper function for building directory paths to save raw, intermediate, and preprocessed data."""

    dirs = {
        'stripped': Path(output_dir, 'intermediate', language, 'stripped'),
        'grouped': Path(output_dir, 'intermediate', language, 'grouped'),
        'preprocessed': Path(output_dir, 'preprocessed', f'{language}.parquet')
    }
    return dirs

def download_fineweb_data(
    language: str,
    local_dir: str = 'FineWeb/raw',
    sample: int = int(),
    disable_progress_bar: bool = False,
    restart: bool = False
)-> None:
    
    """
    Given a language code, this function will download raw FineWeb files from HF Hub.
    For possible languages, please use 'get_fineweb_languages', or visit https://huggingface.co/datasets/HuggingFaceFW/fineweb-2.
    Use the 'sample' arguement to run a sanity check.

    Args:
        language (str): Language code of the target language.
        local_dir (str): Directory where raw FineWeb data is to be saved.
        sample (int): For running a sanity check. Will sample 'n' paths.
        diable_progress_bar (bool): Whether to diable the progress bar.
        restart (bool): If True, will download all paths and overwrite previously written files.
    """
    
    #Checks if input language code matches FineWeb data.
    print(f'Checking FineWeb hub for the language code, "{language}"...')
    possible_languages = get_fineweb_languages()
    if language not in possible_languages:
        raise ValueError ("Input language is not recognized. Please use the function, 'get_fine_web_languages' to view possible languages, or visit https://huggingface.co/datasets/HuggingFaceFW/fineweb-2")

    #Retrieves paths. If doing a sanity check, takes a sample of the paths for downloading.

    paths = get_fineweb_paths(language)
    if sample:
        sample = min(sample, len(paths))
        paths = random.sample(paths, sample)
        print (f'Running sanity check. {sample} paths sampled.')
    os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
    
    #Creates a directory to save FineWeb data.
    os.makedirs(local_dir, exist_ok=True)

    #Iterates through paths and downloads FineWeb data using 'hf_hub_download'.
    for path in tqdm(paths, desc="Downloading FineWeb data", disable=disable_progress_bar):
        if os.path.exists(Path(local_dir, path)) and not restart:
            continue

        hf_hub_download(
        repo_id="HuggingFaceFW/fineweb-2",
        repo_type="dataset",
        filename=path,
        local_dir=local_dir)
    
    raw_data_dir = Path(local_dir, os.path.dirname(paths[0]))
    print(f'Download complete. Saved raw FineWeb data to {raw_data_dir}')
    return raw_data_dir

def get_domain(url: str)-> str:
    """Helper function that will take a URL and return the domain."""

    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"

def add_domain_column(df: pl.DataFrame)-> pl.DataFrame:
    """Helper function that will take a polars FineWeb DataFrame and add a domain column."""

    df = df.with_columns(
    pl.col("url").map_elements(lambda x: get_domain(x), return_dtype=pl.Utf8).alias("domain")
    )
    return df.drop_nans()

def strip_and_add_domain_pipeline(
        language: str,
        raw_data_dir: str,
        output_dir: str = 'FineWeb',
        columns: List[str] = ['id', 'date', 'url'],
        disable_progress_bar: bool = False,
        print_statement: bool = True,
        restart: bool = False
)-> None:
    """
    Pipeline that will iterate through FineWeb parquet files,
    strip away unneccesary data, add the domain column, and save
    the DataFrame to disk.

    Args:
        language (str): Language which is being processed.
        raw_data_dr (str): Explicit path to directory where raw data is stored.
        output_dir (str): Direcotry to save intermediate and final outputs.
        columns (List[str]): The columns from FineWeb that are to be kept.
        disable_progress_bar (bool): Whether or not to disable the progresss bar.
        print_statement(bool): Whether to issue a print statment when complete.
        restart (bool): If True, starts over and overwrites files that have already been processed.
    """

    #Build your input/output paths
    io_paths = get_io_paths(language, output_dir)

    #Checks if FineWeb data has been stripped with domain column added.
    if not os.path.exists(raw_data_dir):
        raise FileNotFoundError(f'{raw_data_dir} not found. Use download_fineweb_data to get language data.')
    elif len(os.listdir(raw_data_dir)) == 0:
        raise FileNotFoundError(f'{raw_data_dir} found, but it has no files. Use download_fineweb_data to get language data.')
 
    #Builds a list a files, and makes a directory to save stripped data.
    files = [file for file in os.listdir(raw_data_dir) if file.endswith('.parquet')]
    os.makedirs(io_paths['stripped'], exist_ok=True)

    #Ensures that 'url' is included, which is neccesary to proceed with grouping.
    if 'url' not in columns:
        raise ValueError ("To proceed with grouping, 'url' must be included in columns.")
    
    #Ensures that the input columns are contained in the FineWeb data.
    possible_columns = pl.read_parquet_schema(Path(raw_data_dir, os.listdir(raw_data_dir)[0]))
    if not all(column in possible_columns for column in columns):
        raise ValueError (f"Column selection does not align with FineWeb data. Please select from these columns: {list(possible_columns.keys())}")

    for file in tqdm(files, desc= "Stripping dfs and adding domain column", disable=disable_progress_bar):
        input_file, output_file = Path(raw_data_dir, file), Path(io_paths["stripped"], file)
        
        if os.path.exists(output_file) and not restart:
            continue

        #Iterates through files, loads only the specefied columns, adds the domain column, and saves to disk.
        df = pl.read_parquet(input_file, columns=columns)
        df = add_domain_column(df)
        df.write_parquet(output_file)
    if print_statement:
        total_files = len(os.listdir(io_paths['stripped']))
        print(f'Stripping complete. {total_files} processed. Saved files to {io_paths["stripped"]}')

def group_pipeline(
    language: str,
    output_dir: str="FineWeb",
    disable_progress_bar: bool = False,
    print_statement: bool = True,
    restart: bool = False
)-> None:
    """
    Given a directory of parquet files that have been processed by the function,
    'strip_and_add_domain_pipeline', this function will group them by domain
    and save them to disk.

    Args:
        language (str): Language which is being processed.
        output_dir (str): Direcotry to save intermediate and final outputs.
        disable_progress_bar (bool): Whether or not to disable the progress bar.
        print_statment (bool): Whether or not to issue a print statemnt on completion.
        restart (bool): If True, starts over and overwrites files that have already been processed.

    """
    #Build your input/output paths
    io_paths = get_io_paths(language, output_dir)

    if not os.path.exists(io_paths['stripped']):
        raise FileNotFoundError(f'{io_paths["stripped"]} not found. Run strip_and_add_domain_pipeline before grouping.')
    elif len(os.listdir(io_paths['stripped'])) == 0:
        raise FileNotFoundError(f'{io_paths["stripped"]} found, but it has no files. Run strip_and_add_domain_pipeline before grouping.')

    #Builds a list a files, and makes a directory to save stripped data.
    files = [file for file in os.listdir(io_paths['stripped']) if file.endswith('.parquet')]
    os.makedirs(io_paths['grouped'], exist_ok=True)

    for file in tqdm(files, desc= 'Grouping by domain', disable=disable_progress_bar):
        input_file, output_file = Path(io_paths['stripped'], file), Path(io_paths['grouped'], file)
        if os.path.exists(output_file) and not restart: 
                continue
        
        #Loads the file, groups by domain, returning a df with columns 'domain' and 'count'
        df = pl.read_parquet(input_file)
        df = df.group_by('domain').count()
        df.write_parquet(output_file)
    if print_statement:
        total_files = len(os.listdir(io_paths['grouped']))
        print(f'Grouping complete. {total_files} processed. Saved output to {io_paths["grouped"]}')

def combine_grouped_dfs(
    language: str,
    output_dir: str='FineWeb',
    batch_size: int=10,
    disable_progress_bar: bool = False,
    print_statement: bool = True
    )-> None:
    """
    Given a directory of grouped DataFrames, combines into a single DataFrame.

    Args:
        language (str): Language which is being processed.
        output_dir (str): Direcotry to save intermediate and final outputs.
        batch_size (int): Number of DataFrames to process in each batch.
        diable_progress_bar (bool): Whether to disable the progress bar.
        print_statement (bool): Whether to issue a print statement on completion.
    
    Returns (saved to disk):
        Grouped DataFrame with the following columns:
            domain (str): URL of the contributing domain.
            count (u32): Number of pages which that domain contributed.
            tld (str): Top-level domain of the contributing domain.
    """

    #Build your input/output paths
    io_paths = get_io_paths(language, output_dir)

    #Checks if FineWeb data has been stripped with domain column added.
    if not os.path.exists(io_paths['grouped']):
        raise FileNotFoundError(f'{io_paths["grouped"]} not found. Group data using group_pipeline.')
    elif len(os.listdir(io_paths['grouped'])) == 0:
        raise FileNotFoundError(f'{io_paths["grouped"]} found, but it has no files. Group data using group_pipeline.')
    #Initialize the output and the filepaths
    output = None 
    paths = [Path(io_paths['grouped'], file) for file in os.listdir(io_paths['grouped']) if file.endswith('.parquet')]

    #Compile the data in batches
    for i in tqdm(
        range(0, len(paths), batch_size),
        desc = "Combining grouped data",
        disable=disable_progress_bar):

        #Concatenate a batch of files and group them by domain.
        batch_files = paths[i:i + batch_size]
        batch_data = pl.concat([pl.read_parquet(file) for file in batch_files])
        batch_grouped = batch_data.group_by('domain').agg(pl.col('count').sum())
        
        #Combine current batch with previous batches.
        if output is None:
            output = batch_grouped
        else:
            output = pl.concat([output, batch_grouped]).group_by('domain').agg(pl.col('count').sum())
    
    if print_statement:
        print ("All DataFrames combined. Adding top-level domain column.")
    
    #Add the tld column.
    output = output.with_columns(
        pl.col("domain").map_elements(lambda x: get_tld(x, fail_silently=True), return_dtype=pl.Utf8).alias("tld")
        )
    
    #Sort and save
    os.makedirs(os.path.dirname(io_paths['preprocessed']), exist_ok=True)
    output = output.sort('count', descending=True)
    output.write_parquet(io_paths['preprocessed'])

    if print_statement:
        print(f"Saved combined dataframe to {io_paths['preprocessed']}")
        print(output.head(10))

def download_and_preprocess_pipeline(
    language: str,
    local_dir: str = "FineWeb/raw",
    output_dir: str = 'FineWeb',
    sample: int = int(),
    columns: List[str] = ['id', 'date', 'url'],
    batch_size: int=10,
    disable_progress_bar: bool = False,
    print_statement: bool = True,
    restart: bool = False
    )-> pl.DataFrame:
    """
    Combines all previous pipelines.
    Given a language, this function will download FineWeb data, strip it,
    group it, and combine all files into a single DataFrame.

    Args:
        language (str): Language which is being processed.
        local_dir (str): Directory where raw FineWeb data is stored.
        output_dir (str): Direcotry to save intermediate and final outputs.
        columns (List[str]): During stripping, identifies columns to keep.
        grouped_data_dir (str): Directory to save DataFrames grouped by domain.
        batch_size (int): When combining grouped data, the number of DataFrames to combine in each batch.
        path_to_output (str): Path to save the final combined DataFrame.
        disable_progress_bar (bool): Whether or not to disable the progress bar.
        print_statment (bool): Whether or not to issue a print statemnt on completion.
        restart (bool): If True, starts over and overwrites files that have already been processed.
    
    Returns:
        Each step of preprocessing saves files to disk. 
        With the default settings, the structure will be:

        root/
        └── FineWeb/
            ├── raw/
            │   └── data/
            │       └── {language}/
            │           └── train/
            │               ├── 000_00000.parquet
            │               ├── 000_00001.parquet
            │               └── 000_00002.parquet
            ├── intermediate/
            │   └── {language}/
            │       ├── stripped/
            │       │   ├── 000_00000.parquet
            │       │   ├── 000_00001.parquet
            │       │   └── 000_00002.parquet
            │       └── grouped/
            │           ├── 000_00000.parquet
            │           ├── 000_00001.parquet
            │           └── 000_00002.parquet
            └── preprocessed/
                └── {language}.parquet

        
        raw: Raw data from from FineWeb.
        intermediate/{lang}/stripped: DataFrames with unneccesary columns stripped and domain added.
        intermediate/{lang}/grouped: Invidual DataFrames grouped by domain.
        preprocessed/{lang}.parquet: Final output. All grouped DataFrames are combined and tld is added.
    """

    raw_data_dir = download_fineweb_data(
        language=language,
        local_dir=local_dir,
        sample=sample,
        disable_progress_bar=disable_progress_bar,
        restart=restart
    )

    strip_and_add_domain_pipeline(
        language=language,
        raw_data_dir=raw_data_dir,
        output_dir=output_dir,
        columns=columns,
        disable_progress_bar=disable_progress_bar,
        print_statement=print_statement,
        restart=restart
    )

    group_pipeline(
        language=language,
        output_dir=output_dir,
        disable_progress_bar=disable_progress_bar,
        print_statement=print_statement,
        restart=restart
    )

    combine_grouped_dfs(
        language=language,
        output_dir=output_dir,
        batch_size=batch_size,
        disable_progress_bar=disable_progress_bar,
        print_statement=print_statement
    )