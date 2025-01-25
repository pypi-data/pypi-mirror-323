from pydantic import BaseModel
from openai import OpenAI

client = OpenAI(base_url="http://192.168.170.76:11434/v1", api_key="ollama")
model = "qwen2.5:7b-instruct"

# Define the schema for the response
class FriendInfo(BaseModel):
    name: str
    age: int
    is_available: bool

class FriendList(BaseModel):
    friends: list[FriendInfo]

completion = client.beta.chat.completions.parse(
    temperature=0,
    model=model,
    messages=[
        {"role": "user", "content": "I have two friends. The first is Ollama 22 years old busy saving the world, and the second is Alonso 23 years old and wants to hang out. Return a list of friends in JSON format"}
    ],
    response_format=FriendList,
)

friends_response = completion.choices[0].message
print(friends_response)
print('@@@@@@@')
if friends_response.parsed:
    print(friends_response.parsed)
elif friends_response.refusal:
    print(friends_response.refusal)
