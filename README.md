Streak Telegram Bot
===

## Features
- Count your streak
- Count total days of preventing addiction
- Collaborate with friends in groups
- Leaderboard by streak days
- Convenient use
- Admins can remove cheaters from leaderboard
- Admins can return people to leaderboard
- Users can delete all info about theirselfs
- PostgreSQL
- Async
- Docker support
- Written in [Aiogram](https://github.com/aiogram/aiogram)
- MIT License :)

## Try it out
There is a public instance of this bot located at [@streakaqbot](https://t.me/streakaqbot)

## Installing

Install requirements:

```console
$ cp .env{.example,}
```
Editing `.env` file:
```python
TOKEN="12345678:AAAAAAAAAAAAAAAAAAAAAAAAAAAA"
POSTGRES_LOGIN="login"
POSTGRES_PASSWORD="password"
POSTGRES_HOST="localhost"
POSTGRES_DB="database"
SQLALCHEMY_ECHO=false
TIMEOUT_SCOREBOARD_IN_SECONDS=360
```

- TOKEN - Token from https://t.me/BotFather
- SQLALCHEMY_ECHO - Every SQL transaction will be echoed. `true` or `false`
- TIMEOUT_SCOREBOARD_IN_SECONDS - Every X seconds scoreboards will be refreshed.

```console
$ docker-compose up -d --build
```
## LICENSE

This product is licensed by the **MIT License**. [LICENSE](/LICENSE)
