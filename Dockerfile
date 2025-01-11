FROM python:3.11.7
# Устанавливаем переменную среды для отключения буферизации Python-вывода
ENV PYTHONUNBUFFERED=1
# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    libportaudio2 \
    portaudio19-dev \
    ffmpeg\
    && rm -rf /var/lib/apt/lists/*

# Копируем и устанавливаем зависимости Python
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Устанавливаем рабочую директорию
WORKDIR /bot

# Копируем весь код бота в контейнер
COPY ./bot /bot/

# Указываем команду для запуска приложения
CMD ["python", "/bot/main.py"]


#FROM python:3.11.7
#
## Устанавливаем переменную среды для отключения буферизации Python-вывода
#ENV PYTHONUNBUFFERED=1
#
## Устанавливаем системные зависимости для PyAudio
#RUN apt-get update && apt-get install -y \
#    gcc \
#    libportaudio2 \
#    portaudio19-dev \
#    libasound2-dev \
#    && rm -rf /var/lib/apt/lists/* \
#RUN apt-get update && apt-get install -y \
#    alsa-utils \
#    libasound2 \
#    libasound2-dev
#RUN apt-get update && apt-get install -y libportaudio2
## Копируем и устанавливаем зависимости Python
#COPY ./requirements.txt /requirements.txt
#RUN pip install --no-cache-dir -r /requirements.txt
#
## Устанавливаем рабочую директорию
#WORKDIR /bot
## Копируем весь код бота в контейнер
#COPY ./bot /bot/
## Указываем команду для запуска приложения
#CMD ["python", "/bot/main.py"]




#FROM python:3.11.7
#
#ENV PYTHONUNBUFFERED=1
#
#COPY ./requirements.txt /requirements.txt
#
#RUN pip install -r /requirements.txt
#
#WORKDIR /bot
#
#COPY ./bot /bot/
#
#CMD ["python", "/bot/main.py"]