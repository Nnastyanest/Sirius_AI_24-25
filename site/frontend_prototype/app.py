import streamlit as st
import requests
from io import BytesIO
from datetime import datetime
from config import *


def send_file_to_server(file):
    """Отправляет файл на сервер FastAPI и возвращает ответ"""
    with st.spinner('Отправка файла на сервер...'):
        files_data = {'file': (file.name, file.read())}
        response = requests.post(FASTAPI_URL + 'process', files=files_data)
    return response


def main_page():
    """Главная страница для загрузки и обработки файлов"""
    st.title("Добавить конспект")
    uploaded_file = st.file_uploader(
        "Загрузите текстовые, аудио или видео файлы",
        type=["txt", "mp3", "mp4"]
    )

    if uploaded_file:
        if st.button("Отправить на сервер"):
            response = send_file_to_server(uploaded_file)

            if response.status_code == 200:
                file_name = '.'.join(str(uploaded_file.name).split('.')[:-1]) + '.tex'
                file_content = BytesIO(response.content)

                st.write(f"**Имя файла**: {file_name}")
                st.download_button(
                    label="Скачать документ LaTeX",
                    data=file_content,
                    file_name=file_name,
                    mime="application/x-tex"
                )
                st.session_state['history'].append({
                    "type": "received",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "name": file_name,
                    "size": len(response.content),
                    "content": response.content
                })

            else:
                st.error("Ошибка при обработке файла на сервере")


def settings_page():
    """Раздел с настройками"""
    st.title("Настройки")
    st.write("В процессе реализации...")


def wastebasket_page():
    """Раздел с настройками"""
    st.title("Корзина")
    st.write("В процессе реализации...")


def history_page():
    """Раздел для отображения истории загруженных и полученных файлов"""
    st.title("История")

    if st.session_state['history']:
        for idx, entry in enumerate(st.session_state['history']):
            st.write(f"**Время**: {entry['timestamp']}")
            st.write(f"**Тип**: {'Загружен' if entry['type'] == 'uploaded' else 'Получен'}")
            st.write(f"**Имя файла**: {entry['name']}")

            size_in_mb = entry['size'] / (1024)
            st.write(f"**Размер файла**: {size_in_mb:.2f} Кб")

            if 'content' in entry:
                st.download_button(
                    label="Скачать из истории",
                    data=BytesIO(entry['content']),
                    file_name=entry['name'],
                    mime="application/x-tex",
                    key=f"download_{idx}"
                )
            else:
                st.write("Файл недоступен для загрузки.")
            
            st.write("---")
    else:
        st.write("История пуста.")


if __name__ == "__main__":
    if 'history' not in st.session_state:
        st.session_state['history'] = []

    st.sidebar.title("Разделы")
    page = st.sidebar.selectbox("Выберите страницу", ["Добавить конспект", "История", "Настройки", "Корзина"])

    if page == "Добавить конспект":
        main_page()
    elif page == "История":
        history_page()
    elif page == "Настройки":
        settings_page()
    elif page == "Корзина":
        wastebasket_page()
