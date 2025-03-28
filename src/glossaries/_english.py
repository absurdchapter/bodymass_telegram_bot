import src.config as config
from src.datautils import date_format

COMMAND_LIST = "/enter_weight - enter current weight\n\n" \
               "/plot - show plot (2 weeks) \n" \
               "/plot_all - show plot (all time) \n" \
               "/download - download data (*.csv) \n" \
               "/upload - upload data (*.csv)\n" \
               "/erase - erase all data \n" \
               "/challenge - start / view challenge\n\n" \
               "/start - show menu \n\n" \
               "/info - info and advice on how to use this bot\n" \
               "/language - сменить язык"

ENTER_WEIGHT_BUTTON = "Enter current body weight"
ENTER_WEIGHT_COMMANDS = ['/enter_weight', ENTER_WEIGHT_BUTTON]

SHOW_MENU_BUTTON = 'Show menu'
SHOW_MENU_COMMANDS = ['/start', SHOW_MENU_BUTTON]

INFO = "This bot is designed to track body weight and will help you on your fitness journey. " \
       "Simply weigh yourself regularly and send me the results.\n\n" \
       "Your body weight highly varies from day to day (up to ~3 kg). " \
       "This happens mainly due to food and fluid retention. " \
       "So if you weigh yourself one day, then simply look at the scales the other day, unfortunately " \
       "you will not get any insights on how many kilos of tissue you actually gained or lost. " \
       "To track your progress " \
       "efficiently you need to measure your body mass at least <b>3 times a week (ideally, every day)</b> and " \
       "write down the results. " \
       "It is also recommended to weigh yourself approximately at the same hour of day. " \
       "After doing this for at least 2 weeks straight, you need to look at the " \
       "<a href=\"https://en.wikipedia.org/wiki/Trend_line_(technical_analysis)\">trend line</a>. " \
       "This way you will get a real picture of what is going on - are you losing or gaining weight, " \
       "and at what speed. \n\n" \
       "The mission of this bot is to make this process <b>as effortless as possible</b>. " \
       "Just pull out your phone and send me a couple of digits. " \
       "This is as easy as it gets. " \
       "Remember, fitness is all about building momentum, and <b>the less unnecessary " \
       "resistance you meet, the more sustainable your habits become in the long run.</b>\n\n" \
       "By the way, the general guideline is you should aim " \
       "at <b>0.5-1 kg per week</b> for <b>weight loss</b>, " \
       "and at <b>0.2-0.5 kg per week</b> for <b>bulking</b> if you want to do this without health risks. " \
       "But it is a better idea to consult a coach or nutritionist since these numbers depend" \
       "on a variety of factors (sex, age, overall health). "

HELLO = "Hello, I am a bot designed to track body weight and help you reach fitness goals. " \
        "Please select a command below.\n\n"

HOW_MUCH_DO_YOU_WEIGH = "How much do you weigh today?"

YOU_ARE_MAINTAINING = "\nYou are currently <i>maintaining</i> your body weight.\n"
YOU_ARE_SURPLUS = "\nYou are currently in a <i>calorie surplus</i>.\n"
YOU_ARE_DEFICIT = "\nYou are currently in a <i>calorie deficit</i>.\n"

YOU_ARE_GAINING_TEMPLATE = "You are gaining weight at an average rate of <i>%.2f kg/week</i>\n"
YOU_ARE_LOSING_TEMPLATE = "You are losing weight at an average rate of <i>%.2f kg/week</i>\n"

WHICH_IS_TOO_SLOW = "(which is too slow to classify as a surplus or a deficit)\n"

PLEASE_ENTER_VALID_POSITIVE_NUMBER = ("Please enter a valid positive number (your body mass in kg)\n"
                                      "/start - return to menu")

SUCCESSFULLY_ADDED_NEW_ENTRY = "Successfully added a new entry:"

HERE_PLOT_LAST_TWO_WEEKS = "Here's a plot of your progress over the last two weeks.\n"
HERE_PLOT_OVERALL_PROGRESS = "Here's a plot of your overall progress.\n"

NO_DATA_TO_DOWNLOAD_YET = "You don't have any data to download yet.\n\n" \
                          "Use /enter_weight daily. \n" \
                          "Alternatively, use /upload to upload your existing data."

HERE_ALL_YOUR_DATA = "<b>Here is all of your data.</b>"
YOU_CAN_ANALYZE_OR_BACKUP = "You can either analyze it by yourself, or use it as a backup to " \
                            "/upload it in case of the data loss."

REPLY_UPLOAD = "You can upload your existing body weight data by giving me a *.csv table."
REPLY_UPLOAD += "The table should contain two columns:\n"
REPLY_UPLOAD += "- Date in the " + date_format + " format\n"
REPLY_UPLOAD += "- Body weight\n"
REPLY_UPLOAD += "You can download an example by using /download command. \n\n"
REPLY_UPLOAD += "To proceed with uploading, please send me a valid *.csv file."
REPLY_UPLOAD += "\n\n/start - return to menu"

NO_VALID_DOCUMENT = "I didn't get a valid document.\n/start"

FILE_TOO_BIG = f"File is too big (max size {config.MAX_FILE_SIZE // 1024} kb)"
FILE_INVALID = "The file is invalid. Please use /download to get an example of a valid file.\n/start"
FILE_UNEXPECTED_ERROR = "Unexpected error occurred during your file processing. I'm sorry.\n/start"

DATA_UPLOADED_SUCCESSFULLY = "<b>Data has been uploaded successfully.</b>\nTake a look at the plot."

CONFIRMATION_WORD = "yes"

REPLY_ERASE = 'You are about to <b>erase all of your data</b>. '
REPLY_ERASE += 'This cannot be undone.\n\n'
REPLY_ERASE += '<b>Please confirm by typing <i>yes</i></b>.\n\n'
REPLY_ERASE += '/start - return'

CANCEL_DELETE = 'Ok, cancelling the deletion.'

NO_DATA_YET = "You don't have any data yet."

ERASE_COMPLETE = 'Ok, I have forgotten everything about your progress.\n' \
                 'But grab the file with your erased data, just in case.'

UNEXPECTED_DOCUMENT = ("That is an unexpected document. "
                       "Do you want me to upload your body weight data? Use the /upload command.")

BODYWEIGHT_PLOT_LABEL = 'Bodyweight, kg'

LANGUAGE_SELECTED = ("Language has been successfully changed to English.\n\n"
                     "/start - show menu")

NOTFAT_OPTIONS = [
    "Hey there! 🌟 You're beautifully unique, strong, and on an incredible journey towards your best self. Keep shining, keep moving, and never forget how amazing you are, just the way you are! 🏋️‍♀️💪 Let's keep getting leaner and stronger together! 🎉",
    "Ah, you used the secret `/notfat` command! 🕵️‍♂️ Well, let me tell you something — you're fabulous! Your body is a temple, and you're nurturing it with care and dedication. Keep up the fantastic work! 💖",
    "Listen closely, dear %USERNAME%! <b>You are absolutely uniquely wonderful and beautifully crafted!</b>\n\nRemember, the journey to your ideal self is not just about the numbers on the scale but about health, joy, and self-acceptance.\n\n<b>Let's make this journey even brighter and more inspiring together! You've got this! 💪</b>",
    "Absolutely not! You're looking fantastic and full of potential. Keep up the great work!",
    "Heck no! You're amazing just the way you are. Keep shining and striving for your best self!",
    "Not in the slightest! You're beautiful, both inside and out. Keep nurturing yourself with love and care."
]

CHALLENGE_REPLY_TEMPLATE = "Your goal is to reach <b>{target_weight:.2f} kg</b> by <b>{target_date}</b>.\n"
CHALLENGE_REPLY_TEMPLATE += "You started with <b>{start_weight:.2f} kg</b> on <b>{start_date}</b>.\n"
CHALLENGE_REPLY_TEMPLATE += "To succeed, your speed should be <b>{desired_speed:.2f} kg per week</b>.\n"
CHALLENGE_REPLY_TEMPLATE += "You are currently moving at a rate of <b>{current_speed:.2f} kg per week</b>.\n"
CHALLENGE_REPLY_TEMPLATE += "\n/start - show menu"
CHALLENGE_REPLY_TEMPLATE += "\n/clear_challenge - disable challenge"

START_CHALLENGE_QUESTION = "Start challenge?"

DISABLE_CHALLENGE_QUESTION = "Disable challenge?"

CONFIRMATION_MARKUP = ['Yes', 'No']

TODAY_LOWERCASE = 'today'

ENTER_STARTING_WEIGHT = "Enter your starting weight"

assert date_format == "%Y/%m/%d"
ENTER_STARTING_DATE = ("Enter starting date in format <b>YYYY/MM/DD</b> (e.g. 2023/06/23) or simply write "
                       "\"<b>{0}</b>\" to use today's date".format(TODAY_LOWERCASE.capitalize()))
PLEASE_ENTER_VALID_DATE = "Please enter a valid date"
ENTER_TARGET_WEIGHT = "Enter target weight"
# TARGET_WEIGHT_CANNOT_BE_SAME_TRY_AGAIN = "Target weight cannot be the same as the starting weight.\nTry again"

assert date_format == "%Y/%m/%d"
WHEN_DO_YOU_WANT_TO_REACH_TEMPLATE = ("When do you want to reach {target_weight:.2f} kg?"
                             "\nEnter challenge end date in format <b>YYYY/MM/DD</b> (e.g. 2023/06/23)")

TARGET_DATE_CANNOT_BE_EARLIER_TEMPLATE = "Target date cannot be earlier than start date ({start_date}). \nTry again"

PLEASE_CONFIRM = f"Please confirm (\"{CONFIRMATION_WORD}\"):"
YOU_WANT_TO_LOSE_WEIGHT_TEMPLATE = "You want to lose weight from {start_weight} kg to {target_weight} kg."
YOU_WANT_TO_GAIN_WEIGHT_TEMPLATE = "You want to gain weight from {start_weight} kg to {target_weight} kg."
YOU_WANT_TO_MAINTAIN_WEIGHT = "You want to maintain weight."
YOU_START_AND_FINISH_TEMPLATE = "You start on {start_date} and finish on {target_date}."
YOUR_CHALLENGE_WILL_LAST_TEMPLATE = "Your challenge will last {days}."
YOUR_DESIRED_SPEED_IS_TEMPLATE = "You will need to move at a rate of {speed:.2f} kg per week to achieve the goal."

CHALLENGE_DISABLED = 'Challenge disabled.\n/start - show menu\n/challenge - start new challenge'
ACTION_CANCELLED = 'Action cancelled.\n/start - show menu'
CHALLENGE_SUCCESSFULLY_CREATED = 'Challenge successfully created\n/start - return to menu'

YES_CANCLEL_MARKUP = [CONFIRMATION_WORD.capitalize(), 'Cancel']
