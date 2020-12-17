# Supermarket basic scraping

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
After running the command, you'll be able to see the different stores in Jerusalem with their IDs on the screen.

Now, that we have the store's ID, we can get its promotions sorted by their update date by running
```cmd script
python main.py --promos 5 --chain Shufersal
```
* We assumed that the store's ID is 5.
Now, you can find the promos in "promos_5.log".

For other documentation and commands, you can run 
```cmd script
python main.py --h
```

Good luck!
