# Replication Package for the Paper: Unveiling the Role of ChatGPT in Software Development: Insights from Developer-ChatGPT Interactions on GitHub

##### Authors: Ruiyin Li, Peng Liang, Yifei Wang, Yangxiao Cai, Weisong Sun

## Abstract
(to be updated)

## Experiment Steps
### 1. Data Collection
Before you begin, note the following important points:

* **Data Sources:** This study collects shared ChatGPT URLs from five data sources on GitHub: Code, Commits, Discussions, Issues, and Pull Requests (PRs). Each source is collected using separate scripts (except issues and PRs, which share a script).
* **GitHub Token:** Ensure that you have entered your personal GitHub token on the first line of the `config.py` file. For more details, refer to the [GitHub's documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).
* **Configuration:**
    * **Time Slices:** If you wish to customize the collection period, modify the `time_slices` variable in `config.py` to set your desired time ranges.
    * **Programming Languages:** To specify which programming languages to search, update the `languages_top_50` variable in `config.py` with your preferred languages.
* **Data Models:** The definitions of the relevant data objects can be found in `models.py`.

**Collection Process**
For each data source, the collection is divided into two steps. Using the code category as an example:

**Step 1: Searching:**
   * Run `search_code.py` to search the code category.
   * The search results are saved in the `search_results` subdirectory with the file name `code_search_results.json`.
   * Note: For issues and pull requests, run `search_pr_and_discussions.py`. The results will be stored as `pullrequests_search_results.json` and `discussions_search_results.json` in the `search_results` subdirectory.
**Step 2: Extraction**
   * Run `extract_code.py` to parse `code_search_results.json` obtained from Step 1.
   * This script parses `search_results/code_search_results.json`, retrieves conversation records from the ChatGPT website, and saves the parsed data as an array of `githubCode` objects in `data/code_sharings.json`.
   * Repeat these two steps for each data category.

To collect all raw data, execute the search and extraction scripts sequentially for each data source.

### 2. Data Cleaning and Statistics
1. **Data Cleaning:**
    * Run `clean.py` to perform preliminary cleaning on the five primary data files (e.g., `code_sharing.json`) located in the data subdirectory.
    * Cleaned data is saved to `cleaned/code_sharings.json`, and invalid samples are saved to `cleaned/invalid_samples_code_sharings.json`.
2. **Statistics (Optional):**
    * Run `statistics.py` to generate several statistical reports on the cleaned data.

### 3. Data Extraction
1.  **Data Splitting:**
    * To facilitate easier processing, the cleaned results have been pre-split. For example, `code_sharings.json` is divided into smaller JSON files.
    * If needed, you can modify the filenames variable in `extract.py` to adjust which files to process. The splitting is performed by running `split_code.py`.
2.  **Key Information Extraction:**
    * Run `extract.py` to extract key information from the JSON files.
    * The extracted data is saved as Excel files (e.g., `extracted_code_sharings_01.xlsx`, `extracted_issues_sharings.xlsx`) in the extracted directory.
    * These files are intended to assist researchers with data labeling.

**Note:** If you encounter errors related to missing directories or files, manually create the necessary directories and retry.

### Experiment Environment
Ensure that the following packages are installed:
* `beautifulsoup4==4.12.3`
* `emoji==2.12.1`
* `lxml==5.2.2`
* `pandas==2.2.2`
* `tiktoken==0.7.0`
* `requests==2.31.0`


