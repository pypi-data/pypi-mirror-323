import bs4
from collections import Counter
from datasets import Dataset
import json
import os
from pathlib import Path
import polars as pl
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from tqdm.auto import tqdm
from typing import Union, List, Literal, Tuple
from urllib.parse import urlparse

def filter_links(
    links: List[str],
    regex: str = ""
)->List[str]:
    """Helper funtion that will filter links using the provided regex."""
    
    if regex:
        links = [link for link in list(set(links)) if re.search(regex, link)]
    return links

def scrape_links(
    method: Literal['bs4', 'selenium'],
    url: str,
    regex: str = "",
    driver: object = None
) -> List[str]:
    """
    Scrapes links from a target page using either the BeautifulSoup library (bs4) or Selenium.

    Args:
        method (str): The scraping method to use ('bs4' or 'selenium').
        url (str): The URL from which to scrape links.
        regex (str, optional): If provided, regular expressions will be used to filter the links collected from the target page.
        driver (object, optional): A pre-initialized Selenium WebDriver instance. If not provided, a new instance will be created.

    Returns:
        links (list): A list of links scraped from the target page.
    """
    if method not in ['bs4', 'selenium']:
        raise ValueError('Input scraping method not supported. Please choose bs4 or selenium')
    
    if method == 'bs4':
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise HTTPError for bad responses
            
            soup = bs4.BeautifulSoup(response.text, 'html.parser')

            # Find all <a> tags and extract their href attributes
            links = [a_tag['href'] for a_tag in soup.find_all('a', href=True)]
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return []
        
    elif method == 'selenium':
        try:
            # If no driver is provided, create a new instance
            if not driver:
                driver = webdriver.Chrome()
            
            driver.get(url)

            # Locate all links on the page using the <a> tag
            links_elements = driver.find_elements(By.TAG_NAME, "a")

            # Extract href attributes from the <a> tags
            links = [link.get_attribute('href') for link in links_elements]
        
        except Exception as e:
            print(f"Error during Selenium scraping on {url}: {e}")
            links = []
        
        finally:
            # Ensure the driver quits after the scraping is done
            if driver:
                driver.quit()
    
    # Filter links with the provided regex
    return filter_links(links=links, regex=regex)

def count_path_branches(links: List[str])->Counter:
    """
    Useful for developing regex to target links.

    Takes a list of links and counts URL branches.
    """
    paths = [urlparse(link).path for link in links]
    branches = []
    
    # Split each path into hierarchical components
    for path in paths:
        parts = path.split('/')
        for i in range(1, len(parts) + 1):
            branches.append('/'.join(parts[:i]))
    
    # Count the frequency of each branch
    branch_freq = Counter([b for b in branches if b])
    return branch_freq

def save_list_to_txt(
        _list: List[str],
        output_path: str
) -> None:
    """Helper function that saves a list to a text file."""
    #checks if output path is to be saved in a directory, makes directory if neccesary.
    if os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    #As the crawl iterates across pages, scraped links are saved to a text file.
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding ='utf-8') as f:

            #Combines new and old contents.
            old_list = f.read().split('\n')
            _list += old_list
    
    #Eliminates duplicates.
    _list = list(set(_list))

    #Writes the list to a text file, sepearted by newlines.
    with open(output_path, 'w', encoding = 'utf-8') as f:
        f.write('\n'.join(_list))

def load_list_from_txt(file_path: str)->List[str]:
    """Helper function that loads a text seperated by newlines into a list"""
    with open(file_path, 'r', encoding='utf-8') as f:
        ids = [id_ for id_ in f.read().split('\n') if id_ != ""]
        return ids
    
def pagerange(
        fstring: str, 
        first: int, 
        last: str
        )->List[str]:
    """
    Helper function for building a list of pages to crawl.
    
    Args:
        fstring (str): Base URL, with open curly-brackets placed where the page is input.
        first (int): The first page number.
        last (int): The last page number.

    Ex: pagerange('example.com/page{}, 1, 3) -> ['example.com/page1', 'example.com/page2', 'example.com/page3']
    """
    return [fstring.format(i) for i in range(first, last+1)]

def crawl(
        method: Literal['bs4', 'selenium'],
        urls : Union[str, List[str]],
        output_path: str,
        regex: str="",
        driver: object=None
) -> None:
    """
    Given a list of URLs, this functional will iterate across pages, scrape links, and save the list to a .txt file.

    Args:
        scrape_method (function): Identifies which library to use for scraping.
        urls (Union[str, List[str]]): Either a URL or a list of URLs to scrape.
        output_path (str): Path to save the list of links.
        regex (str): Regex used to filter URLs.
        driver (object): If using selenium, driver from which to access the web.
    """
    #Iterates across URLs, scrapes links, and saves them.
    if type(urls) == str:
        urls = [urls]
    for url in tqdm(urls, desc = 'Crawling and scraping links'):
        links = scrape_links(
            method=method, 
            url=url, 
            regex=regex,
            driver=driver
            )
        if links:
            save_list_to_txt(links, output_path)
    
    #Upon completion, states how many links were scraped.
    links = load_list_from_txt(output_path)
    print(f"Crawl complete. {len(links)} links scraped")

def extract_path(url: str) -> str:
    """Helper function that normalizes the URL for matching scraped links to FineWeb"""

    #Removes the terminal '/'
    if url[-1] == '/':
        url = url[:-1]
    if url[0] == '/':
        url = url[1:]

    # Check if the input is a full URL. If so, extracts the path.
    if re.match(r'^(https?:\/\/|www\.)', url):
        parsed_url = urlparse(url)
        return parsed_url.path if parsed_url.path else '/'
    
    # If not a full URL, simply returns the input.
    else:
        return url
    
def combine_links_into_regex(links: List[str]) -> str:
    """Helper function that will combine a list of links into a regex."""

    return '|'.join(map(re.escape, links))

def get_ids_from_fineweb(
        df_path: str,
        domain: str,
        links: List[str]
) -> List[str]:
    """
    Given a polars DataFrame, filter rows that match one of the target links, and return a list of IDs.

    Args:
        df_path (str): Path to the parquet file where FineWeb data is saved.
        domain (str): Target domain.
        links (List[str]): List of promising links from the target domain.

    Returns:
        List of IDs from FineWeb tahtt align with the target links.
    """
    links = [extract_path(link) for link in links] #Normalize the links.
    regex = combine_links_into_regex(links) #Combine the links into regex for querying FineWeb
    
    #Chooses a column for the initial filter.
    filter_column = 'domain' if 'domain' in pl.read_parquet_schema(df_path) else 'url'

    #loads the FineWeb data with minimal columns
    df = pl.read_parquet(df_path, columns = list(set(['id', 'url', filter_column])))

    #Filters domains by the input domain. Then, filters rows where the URL matches the target link regex.
    filtered = df.filter(df[filter_column].str.contains(domain))
    filtered = filtered.filter(filtered['url'].str.contains(regex, literal=False))

    #Return a list of IDs from the filtered rows.
    return filtered['id'].to_list()

def compare_notes_to_id_files(paths) -> Tuple[dict, List[str]]:
    """Helper function that retrieves notes and ID files and ensures that their content is aligned."""
    
    if not os.path.exists(paths['notes']):
        raise FileNotFoundError("'notes_path' not found. Please input a path to a JSON object with notes for the FineWeb IDs.")
    
    if not str(paths['notes']).endswith('.json'):
        raise ValueError("Input 'notes_path' is not a JSON file.")
    
    if not os.path.exists(paths['ids']):
        raise FileNotFoundError("'ids_dir' not found. Please input a path to a directory with text files containing FineWeb IDs.")
    
    with open(paths['notes'], 'r', encoding='utf-8') as f:
        notes = json.load(f)

    id_files = [file for file in os.listdir(paths['ids']) if file.endswith('.txt')]
    if len(id_files) == 0:
        raise FileNotFoundError("No text files were found in the input 'ids_dir'.")
    
    missing_notes = [note for note in notes.keys() if note not in [file.split('.')[0] for file in id_files]]
    missing_files = [file for file in id_files if file.split('.')[0] not in notes.keys()]

    if missing_notes:
        print(f'{missing_notes} are not recorded in {paths["notes"]}. The final DataFrame may be incomplete.')
    if missing_files:
        print(f'{missing_files} not found in {paths["ids"]}. The final DataFrame may be incomplete.')
    
    if not (missing_files or missing_notes):
        print("Notes and id files match perfectly.")
    return notes, id_files

def id_retrieval_pipeline(
        data_dir: str,
        domain: str,
        links_path: str,
        output_path: str
)-> None:
    """
    Given a domain, a list of links, and a directory where files are saved,
    this pipeline will retrieve IDs from a series of FineWeb files.

    Args:
        data_dir: Path to directory where FineWeb files are saved.
        domain: Target domain for ID extraction.
        links_path: Path to the file where target links are saved.
        output_path: Path to save list of IDs.
    """

    #Load links from the text file.
    links = load_list_from_txt(links_path)

    #Build a list of filepaths.
    paths = [Path(data_dir, file) for file in os.listdir(data_dir)]

    #Iterates through files, extracts IDs, and saves them.
    for path in tqdm(paths, desc = "Finding IDs"):
        ids = get_ids_from_fineweb(path, domain, links)
        save_list_to_txt(ids, output_path)
    
    #Completes the process by returning the number of IDs matched.
    ids = load_list_from_txt(output_path)
    print(f"IDs extracted. {len(ids)} found.")

def build_notes_df(notes: dict) -> pl.DataFrame:
    """Helper function that builds a Polars DataFrame from FineWeb ID notations."""

    flattened = [{'name': key, **subdict} for key, subdict in notes.items()]
    return pl.DataFrame(flattened)

def build_id_df(
        id_dir: str,
        id_files: List[str]
        )-> pl.DataFrame:
    """Helper function that builds a Polars DataFrame from FineWeb IDs."""

    paths = [Path(id_dir, file) for file in id_files]
    id_dict = {path.name.split('.')[0]: load_list_from_txt(path) for path in paths}
    flattened = [{"name": key, "ids": value} for key, value in id_dict.items()]
    output = pl.DataFrame(flattened)

    output = output.with_columns(
        pl.col("ids").map_elements(len).alias("id_count")
    )
    
    return output

def build_hub_dataset(
        data_dir: str,
        output_path: str='',
        hub_path: str='' 
)-> Union[pl.DataFrame, Dataset]:
    """
    This function combines text files with FineWeb IDs and JSON notes into a DataFrame to be uploaded to HF Hub.

    It is rigidly configured to operate on a data directory (data_dir) with this structure:

    root/
    ├── hub_dataset
            ├── notes.json
            └── ids
                ├──name001.txt
                ├──name002.txt
                └──name003.txt

    'notes.json' is a file with contextual information about the IDs collected from FineWeb.
    Minimally, it must have key values that align with text files in the 'ids' directory.

    'ids' is a direcotry of text files where FineWeb ids are saved.

    Args:
        data_dir (str): Path to directory with data to build HF hub dataset.
        output_path (str): Path where HF hub dataset is to be saved locally.
        hub_path (str): Path to upload HF hub dataset. You must provide an API key for this to function.
    """
    paths = {
        "ids": Path(data_dir, "ids"),
        "notes": Path(data_dir, "notes.json")
    }
    notes, id_files = compare_notes_to_id_files(paths)

    notes = build_notes_df(notes)
    ids = build_id_df(paths['ids'], id_files)
    output = notes.join(ids, on = 'name')

    if output_path:
        output.write_parquet(output_path)
        print(f"Saved to {output_path}")
    
    if hub_path:
        output = Dataset.from_polars(output)
        output.push_to_hub(hub_path)
    return output