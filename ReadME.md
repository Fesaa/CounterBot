# Simply Counter Bot
Extremely simple Counter bot written in python with discord.py. (exact commit: `g5538cd50`)
Supports multiple channels, and has a simply scoreboard counter. 
___
## Installing
Clone, venv, pip and run!
```
cd <your folder>

git clone https://github.com/Fesaa/CounterBot

python3 -m venv venv/

source venv/bin/activate

pip install -r requirements.txt
```
Open CounterBot.py and edit lines 8 to 10 to your needs.
And run the python file!
```
python3 CounterBot.py
```
These commands are for macOS or Linux, if you're on windows you might have to change `python3` into `py`.
___

## Bot commands

| Command |  Aliases | Description |
| :--- | :---: | :--- |
| start | `None` | Initiate channel for Counting, CounterBot replies with '0' as confirmation <br /> Usage: &start \< slowmode: bool\>. Slowmode defaults to `True`, if `True` will add a slowmode of one second to the channel.  |
| stop | `None` | Remove channel for Counter, CounterBot replies with '👌' as confirmation |
| scoreboard | `sc`, `lb`, `leaderboard` | Display leaderboard for a Counter channel. |

## Contributing
Sure ¯\\_(ツ)_/¯
