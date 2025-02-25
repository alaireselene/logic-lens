# from typing import Union

# from fastapi import FastAPI

# app = FastAPI()


# @app.get("/")
# def read_root():
#     return {"Hello": "World"}


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}
import os
import google.genai as genai
from google.genai import types
from langsmith import traceable
from dotenv import load_dotenv
import weaviate
from weaviate.classes.init import Auth
from weaviate.classes.config import Configure


load_dotenv()
weaviate_url = os.getenv("WEAVIATE_URL")
weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
genai_api_key = os.getenv("GENAI_API_KEY")

db = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_url,
    auth_credentials=Auth.api_key(weaviate_api_key),
)
client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))


# Create the model
generation_config = types.GenerateContentConfig(
    system_instruction="""You are a freaky AI that can generate text. Your task is to generate a response to the user input. You can generate any text you want, but it should be relevant to the user input. You can generate a response that is funny, informative, plain weird, or all of them combined. The choice is yours!""",
    temperature=1,
    top_p=0.95,
    top_k=64,
    max_output_tokens=200,
    response_mime_type="text/plain",
)


# Setup LangSmith trace
@traceable
def pipeline(user_input: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp", contents=user_input, config=generation_config
    )
    if (response.text is None) or (response.text == ""):
        return "Sorry, I couldn't generate a response at this time. Please try again later."
    else:
        return response.text


# Test framework
# print(pipeline("Wassup my nigga yo"))
# Test db
print(db.is_ready())
db.close()
