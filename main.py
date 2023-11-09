import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import random
import time

TEXT_FONT = cv2.FONT_HERSHEY_PLAIN
TEXT_SCALE = 3
TEXT_THICKNESS = 3
TEXT_COLOR = (248, 117, 169)
GAME_TIME = 5
COUNTDOWN_TIME = 5
SHOW_MOVE_TIME = 2  # Time to show the moves before displaying the result
RESULTS_DISPLAY_TIME = 5
WINNING_SCORE = 2  # Number of wins required to win the game

# Game moves
MOVES = ["rock", "paper", "scissors"]

# Capture video from webcam
cap = cv2.VideoCapture(0)
detector = HandDetector(maxHands=1)

# Game variables
timer = 0
start_game = False
results = False
scores = [0, 0]

# Function to determine player move


def determine_player_move(fingers):
    if fingers == [0, 0, 0, 0, 0]:
        return "rock"
    elif fingers == [1, 1, 1, 1, 1]:
        return "paper"
    elif fingers == [0, 1, 1, 0, 0]:
        return "scissors"
    return None

# Function to determine winner


def determine_winner(player_move, computer_move):
    if player_move == computer_move:
        return "Tie"
    elif (player_move == "rock" and computer_move == "scissors") or \
         (player_move == "paper" and computer_move == "rock") or \
         (player_move == "scissors" and computer_move == "paper"):
        scores[0] += 1
        return "Player Wins"
    else:
        scores[1] += 1
        return "Computer Wins"

# Function to display text


def display_text(image, text, position):
    cv2.putText(image, text, position, TEXT_FONT,
                TEXT_SCALE, TEXT_COLOR, TEXT_THICKNESS)

# Main function


def main():
    global timer, start_game, results, scores

    # Load the background image
    background = cv2.imread('images/bg.png')
    if background is None:
        print("Error: Background image not found.")
        return

    player_move = None
    computer_move = None
    countdown_started = False
    countdown_timer = 0
    player_wins = 0
    computer_wins = 0
    round_over = False

    while True:
        success, img = cap.read()
        if not success:
            print("Failed to capture image from webcam.")
            break

        # Resize the background to match the webcam frame size
        background_resized = cv2.resize(
            background, (img.shape[1], img.shape[0]))

        hands, img = detector.findHands(img)

        # Overlay the webcam feed onto the background
        combined_img = cv2.addWeighted(background_resized, 0.5, img, 0.6, 0)

        if start_game and not results:
            if not countdown_started:
                countdown_timer = time.time()
                countdown_started = True

            elapsed_time = time.time() - timer
            countdown_elapsed = time.time() - countdown_timer

            if elapsed_time < GAME_TIME:
                # During the game time, show the playing status and countdown
                display_text(combined_img, "Playing", (100, 100))
                # Show countdown
                display_text(combined_img, str(COUNTDOWN_TIME -
                             int(countdown_elapsed)), (200, 200))

                if hands:
                    player_move = determine_player_move(
                        detector.fingersUp(hands[0]))

            elif countdown_elapsed < GAME_TIME + SHOW_MOVE_TIME:
                if not player_move:
                    player_move = "none"
                if not computer_move:
                    computer_move = random.choice(MOVES)
                display_text(
                    combined_img, f"Your Move: {player_move}", (100, 400))
                display_text(
                    combined_img, f"Computer Move: {computer_move}", (100, 500))
            else:
                # After showing the moves, display the result
                results = True
                winner_text = determine_winner(player_move, computer_move)
                display_text(combined_img, winner_text, (100, 100))

        elif results:
            # Display both moves and the scores
            display_text(
                combined_img, f"Player Score: {scores[0]}", (100, 200))
            display_text(
                combined_img, f"Computer Score: {scores[1]}", (100, 300))

            if scores[0] == WINNING_SCORE or scores[1] == WINNING_SCORE:
                final_winner = "Player" if scores[0] == WINNING_SCORE else "Computer"
                cv2.putText(combined_img, f"{final_winner} Wins!", (100, 100),
                            TEXT_FONT, TEXT_SCALE, (10, 194, 240), TEXT_THICKNESS)
                round_over = True

            if round_over and time.time() - timer > GAME_TIME + SHOW_MOVE_TIME + RESULTS_DISPLAY_TIME:
                # Reset for a new game session if a player has won twice
                results = False
                start_game = False
                scores = [0, 0]
                player_move = None
                computer_move = None
                countdown_started = False
                round_over = False
            elif time.time() - timer > GAME_TIME + SHOW_MOVE_TIME + RESULTS_DISPLAY_TIME:
                # Continue the same game session if no player has won twice
                results = False
                start_game = True
                player_move = None
                computer_move = None
                countdown_started = False
                timer = time.time()
        else:
            display_text(combined_img, "Press Space to Start", (100, 100))

        cv2.imshow("Image", combined_img)

        key = cv2.waitKey(1)
        if key == 32 and not start_game:  # Space key to start
            start_game = True
            timer = time.time()
        if key == 27:  # Esc key to exit
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
