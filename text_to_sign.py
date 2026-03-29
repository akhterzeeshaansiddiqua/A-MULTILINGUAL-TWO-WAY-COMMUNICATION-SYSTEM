import cv2
import os

# Folder containing sign videos
SIGN_FOLDER = "sign_videos"


# Function to play sign video in full screen
def play_sign(word):

    # Create video path
    path = os.path.join(SIGN_FOLDER, word + ".mp4")

    # Check if video exists
    if not os.path.exists(path):
        print("Sign not found for:", word)
        return

    # Fullscreen window
    cv2.namedWindow("Text to Sign", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(
        "Text to Sign",
        cv2.WND_PROP_FULLSCREEN,
        cv2.WINDOW_FULLSCREEN
    )

    cap = cv2.VideoCapture(path)

    while cap.isOpened():

        ret, frame = cap.read()

        if not ret:
            break

        cv2.imshow("Text to Sign", frame)

        # Press Q to exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return

    cap.release()


# Convert text to sign
def text_to_sign(sentence):

    words = sentence.lower().split()

    for word in words:
        play_sign(word)


# User input
text = input("Enter text: ")

# Run
text_to_sign(text)

cv2.destroyAllWindows()