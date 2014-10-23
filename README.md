Vindinium Bot AI
=========================
Started Oct 2014

- Uses Python 2.7

Install deps:

    pip install -r requirements.txt

Run with:

    python client.py <key> <publicName> arena <number-of-games-to-play> [server-url]
    python client.py <key> <publicName> training <number-of-turns-to-play> [server-url]

Examples:

    python client.py mySecretKey myBotName arena 3
    python client.py mySecretKey myBotName training 50

Notes:

    BOTNAME must be passed in as argument