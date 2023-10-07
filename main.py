import telebot 
from bot_config import TOKEN 
from database_manipulations import Users, Chat
from loguru import logger
import os 
from key import openapi_key
import openai
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
import requests 
import os 
from langchain.prompts import PromptTemplate
from langchain import LLMChain

os.environ["OPENAI_API_KEY"] = openapi_key



prompt = PromptTemplate(input_variables=['query'], template='Give answer in Russian. The answer from Kazakhsta law codex. {query}')

llms = OpenAI()
bot = telebot.TeleBot(TOKEN)
embeddings = OpenAIEmbeddings()
docsearch = FAISS.load_local("zakon_index", embeddings)
chain = load_qa_chain(llms, chain_type="refine")
llm_chain = LLMChain(prompt=prompt, llm=llms)


@bot.message_handler(commands=["start"])
def start_command(message):
    user_id = message.from_user.id
    logger.info(user_id)
    check_user_exist = Users.check_user_exist(user_id)
    if not check_user_exist:
        Users.add_user(user_id)
        logger.info('user is added')
    bot.send_message(user_id, "Здравствуйте! Меня зовут ZanBot, ваш виртуальный юридический ассистент, созданный специально для граждан Казахстана. Я здесь, чтобы помочь вам с базовыми юридическими вопросами и предоставить полезную информацию, связанную с законодательством нашей страны.")
    
    

@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.from_user.id
    query = message.text
    logger.info(query)
    docs = docsearch.similarity_search(query)
    answer = llm_chain.run(input_documents=docs, query=query)
    bot.send_message(user_id, answer)
    Chat.insert_to_chat(user_id, query, answer)
    

def main():
    bot.polling()
    
if __name__ == '__main__':
    main()