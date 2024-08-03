import pathlib
import textwrap

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown


def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


def init_gemini(model_name="models/gemini-1.5-pro-latest"):
  model = genai.GenerativeModel(model_name)
  return model


def invoke_gemini(prompt, model):
  try:
    response = model.generate_content(prompt)
    return response.text
  except Exception as e:
    print("Error invoking Gemini API: ", e)