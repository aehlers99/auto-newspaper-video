import os
import requests
from PIL import Image
import cv2
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip
import pysubs2
from newspaper import Article
from google.cloud import texttospeech_v1
from pydub import AudioSegment

#Article Scraping
URL = "https://valor.globo.com/financas/noticia/2023/07/26/santander-tem-lucro-de-r-23-bi-alta-de-79percent-no-trimestre-e-queda-de-435percent-em-12-meses.ghtml"
article = Article(URL, language= 'pt')
article.download()
article.parse()
article.nlp()
title, author, text, date, key_words, summary, img= article.title, article.authors, article.text, article.publish_date, article.keywords, article.summary, article.top_image

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'autotube-394018-55d35b0a2f98.json'
client = texttospeech_v1.TextToSpeechClient()

synthesis_input = texttospeech_v1.SynthesisInput(text=summary)
voice1 = texttospeech_v1.VoiceSelectionParams(language_code = 'pt-BR', name = "pt-BR-Wavenet-B")
audio_config = texttospeech_v1.AudioConfig(audio_encoding = texttospeech_v1.AudioEncoding.MP3)
response1 = client.synthesize_speech(request = {'input': synthesis_input, 'voice': voice1, 'audio_config': audio_config})

with open('output.mp3', 'wb') as out:
    out.write(response1.audio_content)

response = requests.get(img)

with open("img.jpg", 'wb') as f:
    f.write(response.content)

image = Image.open("img.jpg")
new_size = (1080, 1920)
image_resize = image.resize(new_size)
image_resize.save("img_edited.jpg")

file = open("summary.txt", "w", encoding="UTF-8")
file.write(summary)
file.close()

# Compute audio length
audio = AudioSegment.from_mp3("output.mp3")
audio_length = len(audio) / 1000.0  # pydub computes in milliseconds

# Creating the video with the image
img = cv2.imread('img_edited.jpg')
height, width, layers = img.shape
frame_rate = 30 
total_frames = (int(audio_length) + 1)* frame_rate

video = cv2.VideoWriter('video.mp4', 0, frame_rate, (width, height))

for _ in range(total_frames):
    video.write(img)

video.release()

video_clip = VideoFileClip("video.mp4")
audio_clip = AudioFileClip("output.mp3")
final_clip = video_clip.set_audio(audio_clip)
final_clip.write_videofile("final_without_subtitles.mp4")

#Under development
#def script_to_srt(script_filename, srt_filename, time_per_word):
#    with open(script_filename, 'r', encoding='UTF-8') as file:
#        script = file.read()
#    words = script.split()
#    subs = pysubs2.SSAFile()
#    start_time = 0
#
#    for word in words:
#        end_time = start_time + time_per_word
#        sub = pysubs2.SSAEvent(start=start_time, end=end_time, text=word)
#        subs.append(sub)
#        start_time = end_time
#
#    subs.save(srt_filename, encoding='UTF-8')
#
#words_in_text = len(summary.split())
#duration_in_minutes = audio_length / 60.0
#speech_rate = words_in_text / duration_in_minutes
#time_per_word = (1 / speech_rate) * 60 * 1000
#script_to_srt('summary.txt', 'legendas.srt', time_per_word)