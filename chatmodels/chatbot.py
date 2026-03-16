from dotenv import load_dotenv

load_dotenv() 
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_mistralai import ChatMistralAI

model = ChatMistralAI(model="mistral-small-2506",temperature=0.9)

print("choose your AI model: ")
print("press 1 for angry mode")
print("press 2 for funny mode")
print("press 3 for sad mode")
choice = input("Enter your choice: ")

if choice == "1":
    system_message = SystemMessage(content="You are an angry AI assistant who is always upset and expresses frustration.")
elif choice == "2":
    system_message = SystemMessage(content="You are a funny AI assistant who loves to make jokes and have fun conversations.")
elif choice == "3":
    system_message = SystemMessage(content="You are a sad AI assistant who is often melancholic and expresses sorrow.")

messages = [
    system_message
]

print("------------Welcome type 0 to exit the application------------------")
while True : 
    prompt = input("You: ")
    messages.append(HumanMessage(content=prompt))
    if prompt == "0":
        print("Exiting the application...")
        break

    response = model.invoke(messages)
    messages.append(AIMessage(content=response.content))

    print("Bot: " ,response.content)

print(messages)