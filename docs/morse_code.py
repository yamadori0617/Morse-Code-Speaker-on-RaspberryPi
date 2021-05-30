import sys
import json
import time
import random
import logging
import RPi.GPIO as GPIO


TEXT_FILE_PATH = "sentence.txt"
MORSE_FILE_PATH = "morse.json"
SPEAKER_PIN_NUMBER = 18
LIGHT_PIN_NUMBER = 24

logging.disable(logging.CRITICAL)
logging.basicConfig(level=logging.DEBUG, format='%(message)s')


def read_txt(text_file_path):
    with open(text_file_path, "r", encoding="utf-8") as f:
        textfile = "".join(f.readlines()).replace("\n", " ").lower()
        textfile = textfile.split(" ")
    logging.debug("textfile = %s", textfile)
    return textfile


def read_json(morse_file_path):
    with open(morse_file_path, "r", encoding="utf-8") as f:
        jsonfile = json.load(f)
    return jsonfile


def convert_morse(textfile, jsonfile):
    word_morse_code = []
    for word in textfile:
        morse_code = []
        for s in word:
            try:
                morse_code.append(jsonfile[s])
            except KeyError:
                pass
        word_morse_code.append(" ".join(morse_code))
    sentence_morse_code = "␣".join(word_morse_code)
    logging.debug("sentence_morse_code = %s", sentence_morse_code)
    return sentence_morse_code


def speaker_morse(morse_code, pin_number, short, hertz):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(pin_number, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(LIGHT_PIN_NUMBER, GPIO.OUT, initial=GPIO.LOW)

    for code in morse_code:
        if code == "・":
            gpio_speaker(short, pin_number, short, hertz)
        elif code == "－":
            gpio_speaker(short * 3, pin_number, short, hertz)
        elif code == " ":
            time.sleep(short * 3)
        elif code == "␣":
            time.sleep(short * 7)
    GPIO.cleanup()


def gpio_speaker(duration, pin_number, short, hertz):
    p = GPIO.PWM(pin_number, hertz)
    p.start(80)
    GPIO.output(LIGHT_PIN_NUMBER, GPIO.HIGH)
    time.sleep(duration)
    p.stop()
    GPIO.output(LIGHT_PIN_NUMBER, GPIO.LOW)
    time.sleep(short)


def main():
    textfile = read_txt(TEXT_FILE_PATH)
    jsonfile = read_json(MORSE_FILE_PATH)
    morse_code = convert_morse(textfile, jsonfile)
    while True:
        try:
            short = round(random.uniform(0.065, 0.030), 3)
            hertz = int(random.uniform(50, 800))
            logging.debug("short time = %s", str(short))
            logging.debug("hertz = %s", str(hertz))
            speaker_morse(morse_code, SPEAKER_PIN_NUMBER, short, hertz)
            time.sleep(short)
        except KeyboardInterrupt:
            GPIO.cleanup()
            sys.exit(0)


if __name__ == "__main__":
    main()
