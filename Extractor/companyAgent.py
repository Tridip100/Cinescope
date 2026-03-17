from dotenv import load_dotenv
load_dotenv()
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import List, Optional
from  langchain_mistralai import ChatMistralAI
from langchain_core.output_parsers import PydanticOutputParser


model = ChatMistralAI(
    model="mistral-small-2506",
    temperature=0.9
)

class MovieInfo(BaseModel):
    title: str
    release_year: Optional[int]
    genre: List[str]
    director: Optional[str]
    main_cast: Optional[List[str]]
    setting_location: Optional[str]
    plot: Optional[str]
    themes: Optional[List[str]]
    ratings: Optional[float]
    notable_features: Optional[str]
    short_summary: Optional[str]


prompt = ChatPromptTemplate.from_messages(
   [
        ("system",
        """
        You are a professional Movie Information Extraction Assistant.

        Extract useful structured information from a movie paragraph.

        Rules:
        - Do NOT add explanations
        - Do NOT add commentary
        - Follow the exact format
        - If information is missing write NULL
        - Keep summary short (2–3 lines)
        - Do NOT guess unknown facts

        Output Format:

        Movie Title:
        Release Year:
        Genre:
        Director:
        Main Cast:
        Setting/Location:
        Plot:
        Themes:
        Ratings:
        Notable Features:
        Short Summary:
        """),
        ("human",
        """
        Extract information from the following movie description:
        {paragraph}
        """)
   ]
)

paragraph = input("Enter a movie description: ")

final_prompt = prompt.invoke(
    {
        "paragraph": paragraph
    }
)

response = model.invoke(final_prompt)
print(response.content)