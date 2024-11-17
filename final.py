# -*- coding: utf-8 -*-

import logging
from colorama import Fore
from TwitchChannelPointsMiner import TwitchChannelPointsMiner
from TwitchChannelPointsMiner.logger import LoggerSettings, ColorPalette
from TwitchChannelPointsMiner.classes.Chat import ChatPresence
from TwitchChannelPointsMiner.classes.Discord import Discord
from TwitchChannelPointsMiner.classes.Telegram import Telegram
from TwitchChannelPointsMiner.classes.Settings import Priority, Events, FollowersOrder
from TwitchChannelPointsMiner.classes.entities.Bet import Strategy, BetSettings, Condition, OutcomeKeys, FilterCondition, DelayMode
from TwitchChannelPointsMiner.classes.entities.Streamer import Streamer, StreamerSettings


## This will gather the data from the user before executing the script. This version of the script is only for grabbing twitch drops. 
## Theoretically It will watch a stream till it grabs the drop and then it will switch to a new streamer. If all streamers with drops are offline it will watch them in the order of the list.
usernamedata = input("What is the username?: ").lower()
filename = input("What file would you like to pull the streamers from?:")
twitch_miner = TwitchChannelPointsMiner(
    username=usernamedata,
    password="write-your-secure-psw",           # If no password will be provided, the script will ask interactively
    claim_drops_startup=False,                  # If you want to auto claim all drops from Twitch inventory on the startup
    priority=[                                  # Custom priority in this case for example:         
        Priority.DROPS,                         # - When we don't have anymore watch streak to catch, wait until all drops are collected over the streamers
        Priority.ORDER                          # - When we have all of the drops claimed and no watch-streak available, use the order priority (POINTS_ASCENDING, POINTS_DESCEDING)
    ],
    logger_settings=LoggerSettings(
        save=True,                              # If you want to save logs in a file (suggested)
        console_level=logging.INFO,             # Level of logs - use logging.DEBUG for more info
        file_level=logging.DEBUG,               # Level of logs - If you think the log file it's too big, use logging.INFO
        emoji=True,                             # On Windows, we have a problem printing emoji. Set to false if you have a problem
        less=False,                             # If you think that the logs are too verbose, set this to True
        colored=True,                           # If you want to print colored text
        color_palette=ColorPalette(             # You can also create a custom palette color (for the common message).
            STREAMER_online="GREEN",            # Don't worry about lower/upper case. The script will parse all the values.
            streamer_offline="red",             # Read more in README.md
            BET_wiN=Fore.MAGENTA                # Color allowed are: [BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET].
        ),
        telegram=Telegram(                                                          # You can omit or leave None if you don't want to receive updates on Telegram
            chat_id=123456789,                                                      # Chat ID to send messages @GiveChatId
            token="123456789:shfuihreuifheuifhiu34578347",                          # Telegram API token @BotFather
            events=[Events.STREAMER_ONLINE, Events.STREAMER_OFFLINE, "BET_LOSE"],   # Only these events will be sent to the chat
            disable_notification=True,                                              # Revoke the notification (sound/vibration)
        ),
        discord=Discord(
            webhook_api="https://discord.com/api/webhooks/1307119559861600256/fqZW11IOa4mqA4gOof_VXUyvWnZLhmbeV2fj4ZRIzSRu3zg25_8tA0zzrT0ZWN83HP1b",  # Discord Webhook URL
            events=[Events.STREAMER_ONLINE, Events.STREAMER_OFFLINE, Events.BET_LOSE],       # Only these events will be sent to the chat
        )
    ),
    streamer_settings=StreamerSettings(
        make_predictions=False,                  # If you want to Bet / Make prediction
        follow_raid=False,                       # Follow raid to obtain more points
        claim_drops=True,                       # We can't filter rewards base on stream. Set to False for skip viewing counter increase and you will never obtain a drop reward from this script. Issue #21
        watch_streak=False,                      # If a streamer go online change the priority of streamers array and catch the watch screak. Issue #11
        chat=ChatPresence.ONLINE,               # Join irc chat to increase watch-time [ALWAYS, NEVER, ONLINE, OFFLINE]
        bet=BetSettings(
            strategy=Strategy.SMART,            # Choose you strategy!
            percentage=5,                       # Place the x% of your channel points
            percentage_gap=20,                  # Gap difference between outcomesA and outcomesB (for SMART strategy)
            max_points=50000,                   # If the x percentage of your channel points is gt bet_max_points set this value
            stealth_mode=True,                  # If the calculated amount of channel points is GT the highest bet, place the highest value minus 1-2 points Issue #33
            delay_mode=DelayMode.FROM_END,      # When placing a bet, we will wait until `delay` seconds before the end of the timer
            delay=6,
            minimum_points=20000,               # Place the bet only if we have at least 20k points. Issue #113
            filter_condition=FilterCondition(
                by=OutcomeKeys.TOTAL_USERS,     # Where apply the filter. Allowed [PERCENTAGE_USERS, ODDS_PERCENTAGE, ODDS, TOP_POINTS, TOTAL_USERS, TOTAL_POINTS]
                where=Condition.LTE,            # 'by' must be [GT, LT, GTE, LTE] than value
                value=800
            )
        )
    )
)

# You can customize the settings for each streamer. If not settings were provided, the script would use the streamer_settings from TwitchChannelPointsMiner.
# If no streamer_settings are provided in TwitchChannelPointsMiner the script will use default settings.
# The streamers array can be a String -> username or Streamer instance.

# The settings priority are: settings in mine function, settings in TwitchChannelPointsMiner instance, default settings.
# For example, if in the mine function you don't provide any value for 'make_prediction' but you have set it on TwitchChannelPointsMiner instance, the script will take the value from here.
# If you haven't set any value even in the instance the default one will be used
try:
    with open(filename, "r") as file:
            streamer_usernames = [line.strip() for line in file]
except: FileNotFoundError
    print(f"Error The file'{filename}' was not found.")
    exit(1) # Exit if file doesnt exist
streamers = [Streamer(username) if i < 5 else username for i, username in enumerate(streamer_usernames)]

twitch_miner.mine(

    streamers,                                 # Array of streamers (order = priority)
    followers=False,                    # Automatic download the list of your followers
    followers_order=FollowersOrder.ASC  # Sort the followers list by follow date. ASC or DESC
)
