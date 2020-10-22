from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.trainers import ListTrainer
import os

'''
This is an example showing how to train a chat bot using the
ChatterBot ListTrainer.
'''

#here is how to create your own time list

time_positive = ['what is the time right now','time','clock','what is the current time', 'what is the time now', 'whats the time', 'what time is it', 'what time is it now', 'do you know what time it is', 'could you tell me the time, please', 'what is the time', 'will you tell me the time', 'tell me the time','time please', 'show me the time', 'what is time', 'whats on the clock', 'show me the clock', 'what is the time','what is on the clock','tell me time','time','clock']

time_negative = ['what are you doing', 'whats up','when is time','who is time' 'could you', 'do you', 'whats', 'will you', 'tell me', 'show me', 'current', 'do', 'now', 'will', 'show', 'tell','me', 'could', 'what', 'whats', 'i have time', 'who', 'who is', 'hardtime','when','what is','how','how is','when is','who is time','how is time','how is time','when is time']


#chatbot = ChatBot(
#    'Terminal',
#    storage_adapter='chatterbot.storage.SQLStorageAdapter',
#    logic_adapters=[
#        'chatterbot.logic.MathematicalEvaluation',
#        'chatterbot.logic.TimeLogicAdapter',
#        'chatterbot.logic.BestMatch'
#    ],
#    database_uri='sqlite:///database.db'
#)

chatbot = ChatBot(
    'Terminal', read_only=True,
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'I am sorry, but I do not understand.',
            'maximum_similarity_threshold': 0.65
        }
        ,
        { #here is how to call the TimeLogicAdapter when you create your own list
            'import_path': 'chatterbot.logic.TimeLogicAdapter',
            'positive': time_positive,
            'negative': time_negative
        }
    ],database_uri='sqlite:///database1.db'
)


# Create a new trainer for the chatbot
trainer = ChatterBotCorpusTrainer(chatbot)

# Train based on the english corpus
trainer.train("chatterbot.corpus.english")

# Train based on english greetings corpus
trainer.train("chatterbot.corpus.english.greetings")

# Train based on the english conversations corpus
trainer.train("chatterbot.corpus.english.conversations")

trainer = ListTrainer(chatbot)
  
########################################
###   TRAINING - run this just one time
########################################
  
trainer.train([
    "I did not do much this week",
    "Did you run into the problems with programs or just did not have time?"
])
 
 
trainer.train([
    "I did a lot of progress",
    "Fantastic! Keep going on"
]) 
 
 
trainer.train([
    'Good morning!',
    'Good morning!',
    'How are you today?',
    'I am fine',
    'Do you like machine learning?',
    'Yes, I like machine learning'
])
  
  
trainer.train([
    'Good morning!',
    'Good morning!'
   
])
  
trainer.train([
    'Hello',
    'Hi there!'
   
])
  
  
trainer.train([
    'Let us talk about current activities',
    'What are you working on now?',
    'I am just browsing Internet for news',
    'What a waste of time! Dont you have any other things to do?',
    'I am working on python script to make new chatbot',
    'This is great. Keep working on this'
])
  
trainer.train(
    "chatterbot.corpus.english.greetings"
   
)
  
trainer.train(
   "chatterbot.corpus.english.conversations"
)
  
  
conversation = [
    "Hello",
    "Hi there!",
    "How are you doing?",
    "I'm doing great.",
    "That is good to hear",
    "Thank you.",
    "You're welcome."
]
  

trainer.train(conversation)
  
print ("USER: How are you doing?")
  
response = chatbot.get_response("How are you doing?")
print("BOT:" + str(response))
print ("USER: Hello")
  
response = chatbot.get_response("Hello")
print("BOT:" + str(response))
print ("USER: Good morning!")
  
response = chatbot.get_response("Good morning!")
print("BOT:" + str(response))
  
  
  
print ("USER: Do you like machine learning?")
  
response = chatbot.get_response("Do you like machine learning?")
print ("BOT:" + str(response))
print ("USER: How do I make a neural network?")
  
response = chatbot.get_response('How do I make a neural network?')
print("BOT:" + str(response))
print ("USER: Let us talk about current activities")
  
response = chatbot.get_response("Let us talk about current activities")
print("BOT:"+str(response))
  
print ("USER: I am just browsing Internet for news")
  
response = chatbot.get_response(" I am just browsing Internet for news")
print("BOT:" + str(response))
  
print ("USER: I am working on python script to make new chatbot")
  
response = chatbot.get_response("I am working on python script to make new chatbot")
print("BOT:"+str(response))
  
  
print ("USER: Bye")
  
response = chatbot.get_response("Bye")
print("BOT:" + str(response))