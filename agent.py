import os
import pickle
import base64
from typing import TypedDict
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

class State(TypedDict):
    topic: str
    content: str
    feedback: str
    quality: str
    posts: dict


class PostGeneration(BaseModel):
    X: str = Field(description="Short version for Twitter (X).")
    LinkedIn: str = Field(description="Professional version for LinkedIn.")
    Facebook: str = Field(description="Friendly version for Facebook.")


def save_draft(subject, html_body):
    creds = None
    if os.path.exists("token.pkl"):
        with open("token.pkl", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            return "Gmail credentials missing. Please connect again."

    try:
        service = build("gmail", "v1", credentials=creds)
        message = f"Subject: {subject}\nContent-Type: text/html; charset=UTF-8\n\n{html_body}"
        encoded_message = base64.urlsafe_b64encode(message.encode("utf-8")).decode("utf-8")
        draft = {"message": {"raw": encoded_message}}
        service.users().drafts().create(userId="me", body=draft).execute()
        return "Draft saved successfully to Gmail!"
    except Exception as e:
        return f"Error saving draft: {e}"


llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)
evaluator = llm.with_structured_output(PostGeneration)


def content_generator(state: State):
    msg = llm.invoke(
        f"Generate engaging, inspiring social media content about '{state['topic']}' for a wide audience."
    )
    return {"content": msg.content}


def content_evaluator(state: State):
    feedback = llm.invoke(
        f"Evaluate this content:\n\n{state['content']}\n\n"
        "Give short feedback and label it as 'good' or 'bad'."
    )
    fb = feedback.content
    return {"feedback": fb, "quality": "good" if 'good' in fb.lower() else 'bad'}


def post_generator(state: State):
    posts = evaluator.invoke(
        f"Based on this content:\n\n{state['content']}\n\n"
        "Create three unique versions for LinkedIn, Facebook, and X (Twitter)."
    )
    return {"posts": posts.dict()}


def route(state: State):
    return "Retry" if state["quality"] == "bad" else "Accept"


builder = StateGraph(State)
builder.add_node("content_generator", content_generator)
builder.add_node("content_evaluator", content_evaluator)
builder.add_node("post_generator", post_generator)
builder.add_edge(START, "content_generator")
builder.add_edge("content_generator", "content_evaluator")
builder.add_conditional_edges("content_evaluator", route, {"Retry": "content_generator", "Accept": "post_generator"})
builder.add_edge("post_generator", END)
workflow = builder.compile()


def generate_social_posts(topic: str):
    state = {"topic": topic}
    return workflow.invoke(state)