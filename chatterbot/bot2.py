from chatterbot import ChatBot
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download()
#time logic 
time_positive = ['what is the time right now','time','clock','what is the current time', 'what is the time now', 'whats the time', 'what time is it', 'what time is it now', 'do you know what time it is', 'could you tell me the time, please', 'what is the time', 'will you tell me the time', 'tell me the time','time please', 'show me the time', 'what is time', 'whats on the clock', 'show me the clock', 'what is the time','what is on the clock','tell me time','time','clock']

time_negative = ['what are you doing', 'whats up','when is time','who is time' 'could you', 'do you', 'whats', 'will you', 'tell me', 'show me', 'current', 'do', 'now', 'will', 'show', 'tell','me', 'could', 'what', 'whats', 'i have time', 'who', 'who is', 'hardtime','when','what is','how','how is','when is','who is time','how is time','how is time','when is time']


# Uncomment the following lines to enable verbose logging
import logging
logging.basicConfig(level=logging.INFO)

# Create a new instance of a ChatBot
bot = ChatBot(
    'Terminal', read_only=True,
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    #logic_adapters=[
    #    'chatterbot.logic.BestMatch',    
    #    'chatterbot.logic.MathematicalEvaluation',
    #    'chatterbot.logic.TimeLogicAdapter'
    #],
    #database_uri='sqlite:///database.db'
    logic_adapters=[
        { 
            'import_path': 'chatterbot.logic.MathematicalEvaluation'
        },
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'I am sorry, but I do not understand.',
            'maximum_similarity_threshold': 0.65
        }
#        ,
#        { #here is how to call the TimeLogicAdapter when you create your own list
#            'import_path': 'chatterbot.logic.TimeLogicAdapter',
#            'positive': time_positive,
#            'negative': time_negative
#        }
    ],database_uri='sqlite:///database1.db'        
)

print('Type something to begin...')

# The following loop will execute each time the user enters input
while True:
    try:
        user_input = input()

        bot_response = bot.get_response(user_input)

        print('Bot: ', bot_response)

    # Press ctrl-c or ctrl-d on the keyboard to exit
    except (KeyboardInterrupt, EOFError, SystemExit):
        break
