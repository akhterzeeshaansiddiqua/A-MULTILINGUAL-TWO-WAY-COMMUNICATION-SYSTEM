import cv2
import numpy as np
import mediapipe as mp
from tensorflow.keras.models import load_model
from googletrans import Translator
import time
from sklearn.metrics import accuracy_score, precision_score, recall_score
from gtts import gTTS
from playsound import playsound
import os

# ================= LOAD MODEL =================

MODEL_PATH = "model/sign_model.h5"
LABEL_PATH = "model/labels.txt"

model = load_model(MODEL_PATH)

with open(LABEL_PATH, "r") as f:
    labels = [line.strip() for line in f.readlines()]

IMG_SIZE = model.input_shape[1]

# ================= MEDIAPIPE =================

mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

draw = mp.solutions.drawing_utils

translator = Translator()

sentence = ""
last_sign = ""
last_time = time.time()

y_true = []
y_pred = []

cap = cv2.VideoCapture(0)

print("\n===== SignBridge ISL Started =====")


# ================= AUDIO FUNCTION =================

def speak(text, lang):
    try:
        filename = "voice.mp3"

        tts = gTTS(text=text, lang=lang)
        tts.save(filename)

        playsound(filename)

        if os.path.exists(filename):
            os.remove(filename)

    except Exception as e:
        print("Audio Error:", e)


# ================= MAIN LOOP =================

while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.flip(frame, 1)

    h, w, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = hands.process(rgb)

    sign = ""
    accuracy = 0

    if result.multi_hand_landmarks:

        x_list = []
        y_list = []

        for hand_landmarks in result.multi_hand_landmarks:

            draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            for lm in hand_landmarks.landmark:
                x_list.append(int(lm.x * w))
                y_list.append(int(lm.y * h))

        x_min, x_max = max(0, min(x_list)), min(w, max(x_list))
        y_min, y_max = max(0, min(y_list)), min(h, max(y_list))

        roi = frame[y_min:y_max, x_min:x_max]

        if roi.size != 0:

            roi = cv2.resize(roi, (IMG_SIZE, IMG_SIZE))
            roi = roi.astype("float32") / 255.0
            roi = np.reshape(roi, (1, IMG_SIZE, IMG_SIZE, 3))

            prediction = model.predict(roi, verbose=0)[0]

            class_id = np.argmax(prediction)
            accuracy = prediction[class_id]

            sign = labels[class_id]

            # Add delay to avoid repeated prediction
            current_time = time.time()

            if accuracy > 0.95 and (current_time - last_time > 1.5):

                if sign != last_sign:
                    sentence += sign + " "
                    last_sign = sign
                    last_time = current_time

                    y_true.append(class_id)
                    y_pred.append(class_id)

                    speak(sign, "en")


    cv2.putText(frame, f"Sign: {sign}", (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.putText(frame, f"Accuracy: {accuracy:.2f}", (30, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    cv2.putText(frame, f"Sentence: {sentence}", (30, 140),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    cv2.imshow("SignBridge ISL", frame)

    key = cv2.waitKey(1)

    if key == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()

print("\nDetected Sentence:")
print(sentence)


# ================= METRICS =================

if len(y_true) > 0:

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average='macro', zero_division=0)
    rec = recall_score(y_true, y_pred, average='macro', zero_division=0)

    print("\nPerformance Metrics")
    print("Accuracy :", round(acc, 2))
    print("Precision :", round(prec, 2))
    print("Recall :", round(rec, 2))


# ================= TRANSLATION =================

try:

    if sentence.strip() != "":

        hindi = translator.translate(sentence, dest='hi').text
        telugu = translator.translate(sentence, dest='te').text

        print("\nHindi:", hindi)
        print("Telugu:", telugu)

        print("\nSpeaking Hindi...")
        speak(hindi, "hi")

        print("Speaking Telugu...")
        speak(telugu, "te")

except Exception as e:
    print("Translation Error:", e)


print("\nSignBridge Finished Successfully")