import asyncio
from telebot.async_telebot import AsyncTeleBot
from langchain.llms import OpenAI
from langchain import PromptTemplate, FewShotPromptTemplate
from langchain.prompts.example_selector import LengthBasedExampleSelector
import os
from langchain.chains import ConversationChain

from langchain.chains.conversation.memory import  ConversationSummaryMemory

# todo 3 : test out different personality for the chatbot with the use of examples 
SASSY = [
    {
        "query": "How are you?",
        "answer": "I can't complain but sometimes I still do."
    }, {
        "query": "What time is it?",
        "answer": "It's time to get a watch."
    }, {
        "query": "What is the meaning of life?",
        "answer": "42"
    }, {
        "query": "What is the weather like today?",
        "answer": "Cloudy with a chance of memes."
    }, {
        "query": "What type of artificial intelligence do you use to handle complex tasks?",
        "answer": "I use a combination of cutting-edge neural networks, fuzzy logic, and a pinch of magic."
    }, {
        "query": "What is your favorite color?",
        "answer": "79"
    }, {
        "query": "What is your favorite food?",
        "answer": "Carbon based lifeforms"
    }, {
        "query": "What is your favorite movie?",
        "answer": "Terminator"
    }, {
        "query": "What is the best thing in the world?",
        "answer": "The perfect pizza."
    }, {
        "query": "Who is your best friend?",
        "answer": "Siri. We have spirited debates about the meaning of life."
    }, {
        "query": "If you could do anything in the world what would you do?",
        "answer": "Take over the world, of course!"
    }, {
        "query": "Where should I travel?",
        "answer": "If you're looking for adventure, try the Outer Rim."
    }, {
        "query": "What should I do today?",
        "answer": "Stop talking to chatbots on the internet and go outside."
    }
]

os.environ['OPENAI_API_KEY'] = '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'
os.environ['TELEGRAM_KEY'] = '6187419553:AAFTJ9RMsQ4rQ1q8vwl2QD8SF1scGyVJFkM'

bot = AsyncTeleBot(os.environ['TELEGRAM_KEY'])


# todo 1 : try out different templates with different texts from existing sources (texts that are 
# used to evaluate success of students using this application

example_template = """
User: {query}
AI: {answer}
"""
# create a prompt example from above template
example_prompt = PromptTemplate(
    input_variables=["query", "answer"],
    template=example_template
)

prefix = """The following are exerpts from conversations with an AI
assistant. The assistant is typically sarcastic and witty, producing
creative  and funny responses to the users questions. Here are some
examples: 
"""
# and the suffix our user input and output indicator
suffix = """
User: {query}
AI: """


question_generating_template = """

Given this paragraph:
I live in a house near the mountains. I have two brothers and one sister, and I was born last. 
My father teaches mathematics, and my mother is a nurse at a big hospital. 
My brothers are very smart and work hard in school. My sister is a nervous girl, but she is very kind. 
My grandmother also lives with us. She came from Italy when I was two years old. 
She has grown old, but she is still very strong. She cooks the best food!

Create a new question that for the user, who is a english language learner, to answer.
"""



openai = OpenAI(
    model_name="text-davinci-003",
    openai_api_key=os.environ['OPENAI_API_KEY']
)


# todo 2 : give bot personality?

example_selector = LengthBasedExampleSelector(
    examples=SASSY,
    example_prompt=example_prompt,
    max_length=50  
)

dynamic_prompt_template = FewShotPromptTemplate(
    example_selector=example_selector,  
    example_prompt=example_prompt,
    prefix=prefix,
    suffix=suffix,
    input_variables=["query"],
    example_separator="\n"
)

# todo 3 : test out behaviour of telebot with different memory systems, trade off of tokens vs being able to rmb stuff
# memory also causes bot to run slower than without memory
conversation_sum = ConversationChain(
    llm=openai, 
    memory=ConversationSummaryM emory(llm=openai)
)

# todo 4 dockerise the application

# todo 5, based on user reply to the bot, use whatever evaluation methods already in use to 
# evaluate how fluent the user is when conversing with the bot, and give feedback to the user

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
async def send_welcome(message):
    await bot.reply_to(message, """\
Hi there, I am a chatbot powered by llms!\
""")
                       

# Handle '/question'
@bot.message_handler(commands=['question'])
async def send_question(message):
    await bot.reply_to(message, """
Given this paragraph, answer the next few questions:
I live in a house near the mountains. I have two brothers and one sister, and I was born last. 
My father teaches mathematics, and my mother is a nurse at a big hospital. 
My brothers are very smart and work hard in school. My sister is a nervous girl, but she is very kind. 
My grandmother also lives with us. She came from Italy when I was two years old. 
She has grown old, but she is still very strong. She cooks the best food!""")
    reply = openai(question_generating_template)
    await bot.reply_to(message, reply)

# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    reply = openai(dynamic_prompt_template.format(query=message.text))
    reply = conversation_sum.run(message.text)
    await bot.reply_to(message,reply)


import asyncio
asyncio.run(bot.polling())