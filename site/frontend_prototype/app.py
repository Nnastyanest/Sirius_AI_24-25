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
    uploaded_files = st.file_uploader(
        "Загрузите текстовые, аудио или видео файлы",
        type=["txt", "mp3", "wav", "mp4", "mkv"]
    )

    if uploaded_files:
        if st.button("Отправить на сервер"):
            response = send_file_to_server(uploaded_files)

            if response.status_code == 200:
                files_received = response.json().get("files", [])

                st.write("Полученные файлы:")

                for file_info in files_received:
                    file_name = file_info["name"]
                    file_extension = file_info["extension"]
                    file_content = BytesIO(file_info["content"].encode('latin1'))

                    st.write(f"**Имя файла**: {file_name}")
                    st.write(f"**Расширение**: {file_extension}")
                    st.download_button(
                        label="Скачать",
                        data=file_content,
                        file_name=f"{file_name}.{file_extension}",
                        mime="application/octet-stream"
                    )

                    st.session_state['history'].append({
                        "type": "received",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "name": f"{file_name}.{file_extension}",
                        "size": len(file_content.getvalue()),
                    })
            else:
                st.error("Ошибка при обработке файлов на сервере")


def settings_page():
    """Раздел с настройками"""
    st.title("Настройки")
    st.write("пумпурм")


def wastebasket_page():
    """Раздел с настройками"""
    st.title("Корзина")
    st.write("пумпурм")


def history_page():
    """Раздел для отображения истории загруженных и полученных файлов"""
    st.title("История")

    if st.session_state['history']:
        for entry in st.session_state['history']:
            st.write(f"**Время**: {entry['timestamp']}")
            st.write(f"**Тип**: {'Загружен' if entry['type'] == 'uploaded' else 'Получен'}")
            st.write(f"**Имя файла**: {entry['name']}")
            st.write(f"**Размер файла**: {entry['size']} байт")
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
