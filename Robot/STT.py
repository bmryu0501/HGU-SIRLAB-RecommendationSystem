#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Requires PyAudio and PySpeech.

import pyaudio
import wave

FORMAT = pyaudio.paInt16
CHANNELS = 1
# RATE = 16000
RATE = 44100
CHUNK = RATE/10
WAVE_OUTPUT_FILENAME = "file.wav"

def recording(record_sec=10): 
    audio = pyaudio.PyAudio()

    # start Recording
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        input_device_index=0,
        frames_per_buffer=CHUNK
    )
    print("recording..")
    frames = []

    for i in range(0, int(RATE/CHUNK * record_sec)):
        data = stream.read(CHUNK)
        frames.append(data)
        
    print("finished recording")
    # stop Recording

    stream.stop_stream()
    stream.close()
    audio.terminate()

    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

import io
from google.cloud import speech

def transcribe_streaming(stream_file="file.wav"):
    """Streams transcription of the given audio file."""

    client = speech.SpeechClient()

    with io.open(stream_file, "rb") as audio_file:
        content = audio_file.read()

    # In practice, stream should be a generator yielding chunks of audio data.
    stream = [content]

    requests = (
        speech.StreamingRecognizeRequest(audio_content=chunk) for chunk in stream
    )

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="ko-KR",
    )

    streaming_config = speech.StreamingRecognitionConfig(config=config)

    # streaming_recognize returns a generator.
    responses = client.streaming_recognize(
        config=streaming_config,
        requests=requests,
    )

    transcript_sentence = ''
    for response in responses:
        # Once the transcription has settled, the first result will contain the
        # is_final result. The other results will be for subsequent portions of
        # the audio.
        for result in response.results:
            # print("Finished: {}".format(result.is_final))
            # print("Stability: {}".format(result.stability))
            alternatives = result.alternatives

            # The alternatives are ordered from most likely to least.
            for alternative in alternatives:
                # print("Confidence: {}".format(alternative.confidence))
                # print(u"Transcript: {}".format(alternative.transcript), "\n")
                transcript_sentence = transcript_sentence + alternative.transcript
    
    return transcript_sentence

# Start STT
STT_sentence = ''
STT_cond = True

recording()
while STT_cond:
    transcript_sentence = transcribe_streaming()
    STT_sentence = STT_sentence + transcript_sentence + " "
    
    if transcript_sentence:
        print("녹음을 5초 연장합니다.")
        recording(5)
        continue
    else:
        print("녹음을 끝냅니다.")
        break

print(STT_sentence)