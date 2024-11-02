import os
os.environ["CUDA_VISIBLE_DEVICES"]="1"

import shutil
import re
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.chat_models.gigachat import GigaChat

credentials_gigachat = "..."


class Model:
    def __init__(self):
        self.model = GigaChat(
                credentials=credentials_gigachat,
                model='GigaChat',
                verify_ssl_certs=False
            )

    def get_predict(self, system_prompt, human_prompt):
        message = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt),
        ]
        return self.model(message).content


def split_text(text, chunk_size=400):
    """Разделение текста на части с ограничением по количеству слов."""
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks


def summarize_block(model, text_block):
    """Создание конспекта блока в формате LaTeX"""
    prompt =  "Преобразуй следующий текст лекции в краткий конспект на русском языке с использованием LaTeX. Используй основные принципы оформления: выделяй важные термины с помощью жирного (\textbf{}) или курсива (\textit{}), добавляй заголовки с командами \section{}, \subsection{}, а также, если нужно, используй списки (\begin{itemize} или \begin{enumerate}). Сохрани чёткость и структурированность текста."
    summary = model.get_predict(prompt, text_block)
    return summary


def convert_bold_to_latex(text):
    """Заменяет выделение жирным с **текст** на \\textbf{текст} для LaTeX."""
    return re.sub(r"\*\*(.*?)\*\*", r"\\textbf{\1}", text)

def generate_latex_document(text, model_name):
    """Генерация полного LaTeX-документа"""
    model = Model()
    blocks = split_text(text)
    latex_sections = []

    for i, block in enumerate(blocks):
        summary = summarize_block(model, block)
        latex_sections.append(summary)

    latex_document = "\\documentclass{article}\n\\usepackage[english, russian]{babel}\n\\begin{document}\n" + "\n".join(latex_sections) + "\n\\end{document}"
    convert_latex = convert_bold_to_latex(latex_document)
    return convert_latex