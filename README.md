# README IS OUTDATED


# TGEB

TGEB is a Telegram bot written in Python to serve the purpose of notifying subscribers of when there is an electricity outage in their home. It utilizes Termux:API to check for whether it's plugged in or not and notifies subscribers based off that information.

## Installation

### Termux

Firstly, you'll have to get Termux and Termux:API from [F-Droid](https://f-droid.org/packages/com.termux/).

### Preparing the workspace

After installing both Termux and Termux:API apps, install git:
```bash
pkg install git
``` 
And run the following command:
```bash
git clone https://github.com/vad1m4/tgeb.git
```
Now, change your directory by running `cd tgeb`.

### Setting up the bot

To simplify the setting up process, I've created a bash file that will install and set up everything you'll need. To run it, you'll have to make it executable by running the following command:
```bash
chmod +x setup.sh
```
Now, run the script:
```bash
./setup.sh
```
You'll be asked to fill in the following information:
* `Group`: The group of the scheduled outages that your address has been assigned to. You can find out yours at the [official LOE page](https://poweron.loe.lviv.ua/)
* `Address`: Pretty self-explanatory. Your address will be displayed in all notifications
* `Token`: Your telegram bot token. You can find out yours at `@BotFather` on Telegram
* `Debug token`: Only use this if you need a bot to test new stuff on. It will be used when running the bot with the `-d` parameter
* `Admin`: User id of the admin of the bot. You can add more than one manually, but the setup script only takes one for the sake of the simplicity

After filling those out, you'll be all set and ready to go. The setup script will run the bot for you.


## Usage

To run the bot manually, simply run `main.py` with python:
```bash
python main.py
```

## Debugging

There's an option to debug the bot if you were to add something yourself. 
To do that, run the bot with the following parameters:

* `--d` or `--debug` to enable debug output from the logger and to use the debug bot's token;

* `--dt` or `--debug-termux` to use a function that imitates termux (useful when you're coding from your desktop computer).

## Cautions

Do not distribute the bot's username to people that you don't know or don't trust. Since this bot uses your address to notify people, everybody who subscribes to it will know your address. Ideally, you should only share it with your neighbours.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
