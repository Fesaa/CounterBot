# Simply Counter Bot
Extremely simple Counter bot written in python with discord.py. (exact commit: `g5538cd50`)
Supports multiple channels, and has a simply scoreboard counter. 
___
## Installing
Clone, venv, pip, MySQL and run!
```
cd <your folder>

git clone https://github.com/Fesaa/CounterBot

python3 -m venv venv/

source venv/bin/activate

pip install -r requirements.txt
```
Open CounterBot.py and edit lines 10 to 13 to your needs.

As displayed there, you need a MySQL server; with a database with two tables.
```
CREATE TABLE `counter` (
  `channel_id` bigint unsigned NOT NULL,
  `count` int DEFAULT NULL,
  `last_user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`channel_id`)
);
CREATE TABLE `leaderboard` (
  `channel_id` bigint unsigned NOT NULL,
  `user_id` bigint NOT NULL,
  `score` bigint DEFAULT NULL,
  PRIMARY KEY (`channel_id`,`user_id`)
);
```
At last, run the python file!
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
