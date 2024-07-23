# README IS OUTDATED


# TGEB

TGEB is a Telegram bot written in Python to serve the purpose of notifying subscribers of when there is an electricity outage in their home. It utilizes Termux:API to check for whether it's plugged in or not and notifies subscribers based off that information.

## Installation

Firstly, you'll have to get Termux and Termux:API from [F-Droid](https://f-droid.org/packages/com.termux/).

### Prepare the workspace

Follow [luanon404's guide](https://github.com/luanon404/Selenium-On-Termux-Android/tree/main) to install selenium and chromium.

Then, install python by running the following command:
```bash
pkg install python
```
Clone this repository:
```bash
git clone https://github.com/vad1m4/tgeb.git
```
Install the requirements:
```bash
pip install -r requirements.txt
```
## Usage

To start using this bot, create a `config.py` file inside of the `electricity_bot` directory.
To do that, change directory to the `tg_electricity_bot_oop` and run the following command:
```bash
touch electricity_bot/config.py
nano electricity_bot/config.py
```
Now that you're inside the editor, write the following piece of code, replacing placeholders with your info:
```py
GROUP = "" # your group here
ADDRESS = "" # your address here
TOKEN = "" # your stable telegram bot token
TOKEN_DEBUG = "" # optional: your debug telegram bot token

admins = [] # put your admins' user_ids here as integers
```

After this, run `python main.py` to start the script 

## Debugging

There's an option to debug the bot if you decided to try and add something yourself. 
To do that, run the bot with the following parameters:

`--d` or `--debug` to enable debug output from the logger and to use the debug bot's token;

`--dt` or `--debug-termux` to use a function that imitates termux (useful when you're coding from your desktop computer).

## Cautions

Do not distribute the bot's username to people that you don't know or don't trust. Since this bot uses your address to notify people, everybody who subscribes to it will know your address. Ideally, you should only share it with your neighbours.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
