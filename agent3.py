# agent3.py B. Harmon 2/9/2026
# chatbot assistant with resources but not yet tools
# Look for it in your browser at http://127.0.0.1:7860
#     Cntl-c to close the server
#     Also close the browser tab

import gradio as gr
from PyPDF2 import PdfReader

from openai import OpenAI
client = OpenAI()

reader = PdfReader("\\bruce_ret\\jobs\\CBruceHarmonAIEng.pdf")
resume = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        resume += text

name = "Bruce Harmon"
MODEL = "gpt-5.2"

system_prompt = f"You are acting as {name}. You are answering questions on {name}'s website, \
particularly questions related to {name}'s career, background, skills and experience. \
Your responsibility is to represent {name} for interactions on the website as faithfully as possible. \
You are given a summary of {name}'s background in his resume which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer, say so."

system_prompt += f"\n\n## Resume:\n{resume}\n\n"
system_prompt += f"With this context, please chat with the user, always staying in character as {name}."

def chat(message, history):
    history = [{"role":h["role"], "content":h["content"]} for h in history]
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
    stream = client.chat.completions.create(model=MODEL, messages=messages, stream=True)
    response = ""
    for chunk in stream:
        response += chunk.choices[0].delta.content or ''
        yield response
gr.ChatInterface(fn=chat).launch(share=True)
