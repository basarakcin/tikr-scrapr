# Tikr Scraper

This is a web scraper script built using Python and Selenium to scrape data from the Tikr website.

## Prerequisites

- Python 3.x
- ChromeDriver (download from https://chromedriver.storage.googleapis.com/index.html?path=114.0.5735.90/)
- Google Chrome (sudo apt install google-chrome-stable)

## Installation

1. Clone the repository.
   
   ```bash
   git clone git@github.com:basarakcin/tikr-scrapr.git
   ```
   
3. Create a virtual environment using the following command:

   ```bash
   python3 -m venv env-tikr
   ```

4. Activate the virtual environment:

   ```bash
   source env-tikr/bin/activate
   ```

5. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

6. Create a `.env` file in the project directory and add the following lines:

   ```plaintext
   EMAIL=<YOUR-EMAIL-ADDRESS>
   PASSWORD=<YOUR-PASSWORD>
   ```

## How to Run

1. Make sure the virtual environment is activated:

   ```bash
   source venv-activate.sh
   ```

2. Run the main `tikr-scrapr.py` script:

   ```bash
   python3 tikr-scrapr.py
   ```

   The script will log in to the Tikr website and perform the scraping process.

3. After finishing development session, run the `update-requirements.py` to update the requirements.txt file:

   ```bash
   python3 update-requirements.py
   ```

4. After finishing the development session, deactivate the virtual environment:

   ```bash
   deactivate
   ```

**Note:** Please make sure to replace `<YOUR-EMAIL-ADDRESS>` and `<YOUR-PASSWORD>` in the `.env` file with your actual Tikr login credentials.
