Vindinium Bot AI
=========================
Started Oct 2014

- Uses Python 2.7

Install deps:

    pip install -r requirements.txt

Run with:

    python client.py <key> arena <number-of-games-to-play> [server-url]
    python client.py <key> training <number-of-turns-to-play> [server-url]

Examples:

    python client.py mySecretKey arena 3
    python client.py mySecretKey training 50

Notes:

    Currently, the bot name in bot.py must match the associated bot name for 
    the key used for the code to run.