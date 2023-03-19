NoFap Streak Telegram Bot
===

# Installing

Install requirements:

```bash
$ pip install -r requirements.txt 
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

## LICENSE

This product is licensed by the **GNU Lesser General Public License v3.0**. [LICENSE](/aqendo/nofap-bot/src/branch/master/LICENSE)