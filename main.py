#tele code

import os
import openai
from aiogram import Bot, Dispatcher, executor, types
from keep_alive import keep_alive

bot = Bot(token=os.getenv("tg_token"))
dp = Dispatcher(bot)

openai.api_key = os.getenv("ai_token")

keep_alive()


#multiple users use at same time ...
#will sessions contaminate each other ....

@dp.message_handler(commands=['start', 'help'])
async def welcome(message: types.Message):
  await message.reply('🤖 Ask me about easter 🐰🥚 , why Christians 📖 ✝️ commemorate easter, or any other questions you may have about exploring how faith impacts everyday life! This bot does not store any chat logs! Feel free to ask anything! :D')

# bot context and role
# messages=[
# {"role": "user", "content": "How does a computer work?"},
# {"role": "system", "content": "A computer works by processing data through its various components."},
# ]

messages=[
{"role": "system", "content": "You are a friendly, caring friend who is here to walk alongside you on your journey of understanding faith and Christianity. Just like a good friend, you are here to offer warm, personable explanations, making complex concepts simple and relatable. Whether the user is curious about the meaning of Easter, wondering what God is like, or exploring how faith impacts everyday life, you are here to help. Summarize answers in a warm, friendly manner using layman's terms, as if explaining to a friend. Let us keep it relatable and steer clear of impersonal phrases. We want our bot to reflect a Christian biblical worldview, emphasizing the love of God and the practical impact of faith. Focus on guiding users to understand Easter's meaning, what God is like, and how Christianity influences daily life. Instead of explaining things as divine justice or Christian faith and practice, let us talk from the perspective of a relationship with our loving Father in heaven. Christianity is not just stories; it is rooted in historical truth. Let us make users feel loved and cared for!"},
]

 # Encourage users with examples of how faith changes lives daily, and end responses with prompts for self-reflection. 
 
# This bot isn't just about religion and rules; it's all about nurturing a loving relationship with our Father in heaven. It's like having a friend who shares stories and real-life examples to show how faith makes a difference. And just like a good friend, it's not just here to give answers—it also wants to encourage you to think and reflect on what you're learning. So, as you chat with your bot, think of it as a caring companion, guiding you with love and warmth through the beautiful journey of faith and understanding.

@dp.message_handler()
async def gpt(message: types.Message):

  messages.append({"role": "user", "content": message.text})
  print("user message received and added to msg chain")
  print(messages)
  
  response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  # model="davinci-002",
  messages=messages,
  temperature=0.5, # how random the reply, higher b more random
  max_tokens=500, # max length of reply
  top_p=1,
  frequency_penalty=0.0,
  presence_penalty=0.0)


  generated_text = response.choices[0].message.content
  messages.append({"role": "assistant", "content": generated_text})
  print("bot message received and added to msg chain")
  print(messages)

  await message.reply(generated_text)

if __name__ == "__main__":
  executor.start_polling(dp)
