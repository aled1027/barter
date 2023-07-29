# Barter

A trading system for setting up generic, automated (but not real-time), trades. Right now, this system is built for dydx.

NOTE: This is a work in progress. It is not ready for production use.


## Setting Up VM

```
# Assumes that we're installing as root

git clone ...
cd barter

# Install poetry
curl -sSL https://install.python-poetry.org | python3 -
# Add the following to /root/.bashrc
export PATH="/root/.local/bin:$PATH"
source /root/.bashrc

# Install dependencies
apt install libpq-dev
poetry install

# Setup .env

# Get it running
python manage.py collectstatic
python manage.py migrate
python manage.py runserver 0.0.0.0:80
```

### Starting it with screen

```
# initial
screen -S app
./run.sh
ctrl-a d to leave

# later
screen -ls
screen -r app
```

### Setting up crontab

Set up a crontab that runs cron.py, a copy of `scripts/cron.py` in the root of the repository.
