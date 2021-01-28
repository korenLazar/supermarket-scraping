# Supermarket basic scraping
The library supports scraping from Shufersal, Co-Op and Zol Vebegadol.

## Installation
clone:
```cmd script
git clone https://github.com/korenLazar/supermarket-scraping.git
cd supermarket-scraping
virtualenv venv
venv\bin\activate
pip install -r requirements.txt
```

## Dependencies

1. python (3.7+)
2. virtualenv

## Usage
First, to find your Shufersal store's ID, you can run the following command (assuming you live in Jerusalem):
```cmd script
python main.py --find_store ירושלים --chain Shufersal
```
In case you want a different supermarket chain, just change 'Shufersal' to a different name (the options will be
 printed in case of misspelling).

The output of the last command - the different Shufersal stores in Jerusalem with their IDs - should be printed.

Now, that we have the store's ID, we can get the store's relevant promotions sorted by their start date, last update and length.
```cmd script
python main.py --promos 5 --chain Shufersal
```
* We assumed that the store's ID is 5.
Now, you can find the promos in both "results\Shufersal_promos_5.csv" and "results\Shufersal_promos_5.log".

For other documentation and commands, you can run 
```cmd script
python main.py --h
```

Any file that was downloaded in the process will be located in the "raw_files" directory.

Good luck!
