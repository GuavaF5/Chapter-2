import streamlit as st
import requests
import json


st.title("Глава 2")
st.write("У Вас получилось узнать страну, в которой вы находитесь. Вы даже смогли купить билеты на авиарейс домой. Но уже в аэропорту Вы неожиданно получили текстовое сообщение. В нём говорилось, то что если вы хотите найти **сокровище**, то Вам требуется найти некую достопримечательность. Возле неё будет расположено секретное место, где и хранится клад. Затем, Вам поочерёдно прислали ещё три сообщения, в которых содержались подсказки к местонахождению **сокровища**. ")


def get_access_token() -> str:
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    payload = 'scope=GIGACHAT_API_PERS'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': '254ee246-4b6b-49e3-b72e-29c60d84e69d',
        'Authorization': 'Basic YjA2NmI2NDAtZTU3ZC00ZDJkLTk3OWMtODRmYzkyNjAyZjI2OjczYzc1NjdkLWNjNWEtNDJmMS04ZGI3LWFhZTQxZjBlM2UxOA=='
    }
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    access_token = response.json()["access_token"]
    return access_token


def send_prompt(msg: str, access_token: str):
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    payload = json.dumps({
        "model": "GigaChat-Pro",
        "messages": [
            {
                "role": "user",
                "content": msg,
            }
        ],
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.post(url, headers=headers, data=payload, verify=False)
    return response.json()["choices"][0]["message"]["content"]


def generate_landmark(access_token: str):
    prompt = (
        "Загадай известную географическую достопримечательность. "
        "Напиши три подсказки о ней, но не называй её напрямую. "
        "Представь полученный текст в формате строки из 4 элементов, в которой первые три элемента - текстовые подсказки, а 4 - это название достопримечательности"
        "Формат вывода: [Подсказка 1: ...  | Подсказка 2: ... |  Подсказка 3: ... |  Название достопримечательности ]"
    )
    response = send_prompt(prompt, access_token)
    return response.strip()


def parse_landmark_response(response: str):
    parts = response.split("|")
    hints = [part.split(":")[1].strip() for part in parts[:3]]
    qwq = parts[3].replace("]", "").split(":")
    landmark = qwq[1]
    landmark = landmark.strip()
    return hints, landmark

def opis(access_token: str, landmark: str):
    prompt = (
        f"Дай краткое описание данной достопримечательности {landmark}"
    )
    opis=send_prompt(prompt, access_token)
    return opis
    



if "access_token" not in st.session_state:
    try:
        st.session_state.access_token = get_access_token()
        st.toast("Токен успешно получен")
    except Exception as e:
        st.toast(f"Не удалось получить токен: {e}")

if "hints" not in st.session_state:
    st.session_state.hints = []
if "landmark" not in st.session_state:
    st.session_state.landmark = ""
if "user_answer" not in st.session_state:
    st.session_state.user_answer = ""
if "show_question" not in st.session_state:
    st.session_state.show_question = False
if "current_hint_index" not in st.session_state:
    st.session_state.current_hint_index = 0
if "opis" not in st.session_state:
    st.session_state.opis = ""


if st.button("Угадать достопримечательность"):
    response = generate_landmark(st.session_state.access_token)
    st.session_state.hints, st.session_state.landmark = parse_landmark_response(response)
    st.session_state.user_answer = ""  
    st.session_state.show_question = True  
    st.session_state.current_hint_index = 0  

s = 0

if st.session_state.show_question:
    st.write("Подсказки:")
    for i in range(st.session_state.current_hint_index + 1):
        st.write(f"Подсказка {i+1}: {st.session_state.hints[i]}")
        s +=1

    user_answer = st.text_input("Что это за достопримечательность?", value=st.session_state.user_answer)

   
    if user_answer:
        st.session_state.user_answer = user_answer  
        if user_answer.lower() == st.session_state.landmark.lower():
            st.success("Правильно! Вы угадали!")
            rrr = opis(st.session_state.access_token, st.session_state.landmark)
            st.write(rrr)
            st.session_state.show_question = False  
        else:
            st.error("Неправильно. Попробуйте ещё раз.")
            if st.session_state.current_hint_index < 2:  
                st.session_state.current_hint_index += 1
            if s == 3:
                st.session_state.show_question = False  
