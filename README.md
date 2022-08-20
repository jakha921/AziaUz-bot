# Azia.uz bot

### Setting up

#### System dependencies

* Python 3.9+
* Redis (if you set `use_redis = true` in **bot.ini**)

#### Preparations

* Clone this repo via `https://github.com/jakha921/AziaUz-bot.git`


#### Create venv
* Create virtual environment: `python -m venv venv`
* Make **venv** your source: `source ./venv/bin/activate` (Linux) or `.\venv\Scripts\activate (Windows)`
* Install requirements: `pip install -r requirements.txt`

### Deployment

* Copy **bot.ini.example** to **bot.ini** and set your variables.

Without Systemd:

* Run bot: `python bot.py`

