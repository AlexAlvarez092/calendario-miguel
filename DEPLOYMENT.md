# Deployment

How to deploy the bot on the Raspberry Pi ([CON-001](docs/requirements/constraints/con-001-run-on-pi3.md)). The decisions behind it are in the [ADRs](docs/adr/): [0005](docs/adr/0005-keep-secrets-in-env-file.md) (secrets), [0006](docs/adr/0006-run-bot-as-systemd-service.md) (service), [0009](docs/adr/0009-push-to-github-with-deploy-key.md) (publishing) and [0010](docs/adr/0010-monitor-bot-with-healthchecks-io.md) (monitoring).

The calendar itself (the `.ics`) is generated and published by the GitHub Actions workflow, so nothing about it is deployed on the Pi.

## Requirements

- A Raspberry Pi with Python 3.12 or later, `git` and an SSH connection to GitHub.
- A Telegram bot token (from [@BotFather](https://t.me/BotFather)) and the Telegram user ID of the only person allowed to use it (Miguel).
- A Gemini API key with the free tier ([ADR 0001](docs/adr/0001-use-ai-to-read-schedule-photo.md)).
- Optional: a [healthchecks.io](https://healthchecks.io) check that emails the developer when the bot stops (NFR-007).

## 1. Deploy key

The Pi pushes to GitHub with a deploy key limited to this repository ([ADR 0009](docs/adr/0009-push-to-github-with-deploy-key.md)).

On the Pi:

```sh
ssh-keygen -t ed25519 -N "" -C "pi3-calendario-bot" -f ~/.ssh/id_ed25519_calendario
ssh-keyscan -t ed25519 github.com >> ~/.ssh/known_hosts
cat ~/.ssh/id_ed25519_calendario.pub
```

Register the public key with write access, for example from a machine with `gh`:

```sh
gh repo deploy-key add id_ed25519_calendario.pub -R AlexAlvarez092/calendario-miguel --allow-write -t pi3-calendario-bot
```

## 2. Clone the repository

On the Pi:

```sh
git clone -c core.sshCommand="ssh -i ~/.ssh/id_ed25519_calendario -o IdentitiesOnly=yes" \
  git@github.com:AlexAlvarez092/calendario-miguel.git ~/calendario-miguel
cd ~/calendario-miguel
git config core.sshCommand "ssh -i ~/.ssh/id_ed25519_calendario -o IdentitiesOnly=yes"
git config user.name "Calendario Bot"
git config user.email "calendario-bot@users.noreply.github.com"
```

## 3. Install the bot

```sh
cd ~/calendario-miguel/bot
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## 4. Configure the secrets

Create `~/calendario-miguel/bot/.env` and restrict it to its owner ([ADR 0005](docs/adr/0005-keep-secrets-in-env-file.md)). The file is ignored by git: never commit it.

```sh
TELEGRAM_BOT_TOKEN=<token from BotFather>
TELEGRAM_ALLOWED_ID=<Telegram user ID of Miguel>
GEMINI_API_KEY=<Gemini API key>
REPO_DIR=/home/<user>/calendario-miguel
HEALTHCHECK_URL=<healthchecks.io ping URL, optional>
GEMINI_MODEL=<optional, defaults to gemini-3.5-flash-lite>
```

```sh
chmod 600 ~/calendario-miguel/bot/.env
```

## 5. Run it as a service

The bot runs as a systemd service that restarts it on failure ([ADR 0006](docs/adr/0006-run-bot-as-systemd-service.md)). Create `/etc/systemd/system/telegram-bot.service` (needs `sudo`), replacing `<user>`:

```ini
[Unit]
Description=Telegram Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=<user>
WorkingDirectory=/home/<user>/calendario-miguel/bot
ExecStart=/home/<user>/calendario-miguel/bot/.venv/bin/python -m calendar_bot
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```sh
sudo systemctl daemon-reload
sudo systemctl enable --now telegram-bot
```

The bot loads `.env` itself, so the unit does not need `EnvironmentFile`.

## 6. Verify

```sh
systemctl is-active telegram-bot
journalctl -u telegram-bot -n 20 --no-pager
```

The log must end with `Application started`. Then, from the authorized Telegram account, send `/start`: the bot answers with its menu. Messages from any other account are ignored.

## Update

```sh
cd ~/calendario-miguel && git pull --ff-only
bot/.venv/bin/pip install -r bot/requirements.txt
sudo systemctl restart telegram-bot
```

## Current deployment

The Pi already had an older bot, `~/telegram-bot/bot.py`, running under the `telegram-bot` service with the unit pointing at it. Since the unit could not be edited without `sudo`, that file was replaced by a small launcher that starts this bot, and the service was restarted by stopping its process so that systemd relaunched it:

```python
import os

BOT_DIR = "/home/alealvar/calendario-miguel/bot"
os.chdir(BOT_DIR)
os.execv(f"{BOT_DIR}/.venv/bin/python", [f"{BOT_DIR}/.venv/bin/python", "-m", "calendar_bot"])
```

To clean it up, apply the unit of step 5 and remove `~/telegram-bot` (its `bot.py.bak` is the original bot).

## Troubleshooting

- **The bot does not answer:** check `journalctl -u telegram-bot`. A `NetworkError` after a reboot usually means the Pi had no connection yet; `Restart=on-failure` recovers it.
- **Changes are not published:** the bot keeps the commits locally and retries every minute. If the repository has a conflict, it notifies Miguel once; resolve it by hand in `~/calendario-miguel` (`git status`, then `git pull --rebase` and `git push`).
- **No email when the bot is down:** check that `HEALTHCHECK_URL` is set and that the check in healthchecks.io has the email integration.
