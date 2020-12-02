# Shufersal basic scraping

## Installation
clone:
```cmd script
git clone https://github.com/korenLazar/shufersal-scraping.git
cd shufersal-scraping
virtualenv venv
venv\bin\activate
pip install -r requirements.txt
```

## Simulator

This app simulates a bitcoin network with many transactions resulting in a bloated blockchain. When the `--evil`
flag is enabled, one of the nodes will commence an attack on some of the blocks, resulting in a lower fee rate
in spite of the blockchain being full.

## Dependencies

1. python (3.7+)
2. virtualenv

## Usage
First, to find your store's id, you can run the following command (assuming you live in Jerusalem):
```cmd script
python main.py --find_store ירושלים
```
After running the command, you'll be able to see the different stores in Jerusalem with their ids in "stores_ירושלים.log".

Now, that we have the store's id, we can get its promotions sorted by their update date by running:
```cmd script
python main.py --promos 5
```
* We assumed that the store's id is 5.
Now, you can find the promos in promos_5.log.

For other documentation and commands, you can run 
```cmd script
python main.py --h
```

Good luck!
