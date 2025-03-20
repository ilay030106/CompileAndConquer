import os
import cv2
import json
import time
#import dlib
import numpy as np
#import face_recognition
from datetime import datetime


class FacialRecognitionSystem:
    def __init__(self):
        self.data_dir = "facial_data"
        self.users_file = os.path.join(self.data_dir, "users.json")
        self.logs_file = os.path.join(self.data_dir, "logs.json")
        self.users_data = {}
        self.confidence_threshold = 0.6

        # Create directory for facial data if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

        # Load existing user data if available
        if os.path.exists(self.users_file):
            with open(self.users_file, 'r') as f:
                self.users_data = json.load(f)

        # Initialize logs file if it doesn't exist
        if not os.path.exists(self.logs_file):
            with open(self.logs_file, 'w') as f:
                json.dump([], f)

    def save_user_data(self):
        """Save user data to JSON file"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users_data, f)

    def log_authentication(self, user_id, success):
        """Log authentication attempts"""
        with open(self.logs_file, 'r') as f:
            logs = json.load(f)

        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": user_id,
            "success": success
        }

        logs.append(log_entry)

        with open(self.logs_file, 'w') as f:
            json.dump(logs, f)

    def preprocess_face(self, image):
        """Preprocess face image"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply histogram equalization
        equalized = cv2.equalizeHist(gray)

        return cv2.cvtColor(equalized, cv2.COLOR_GRAY2BGR)

    def enroll_user(self, user_id):
        """Enroll a new user by capturing and encoding their face"""
        print(f"Starting enrollment for user: {user_id}")
        print("We'll capture 5 images of your face from different angles.")
        print("Please move your head slightly between captures.")

        # Check if user already exists
        if user_id in self.users_data:
            overwrite = input(f"User {user_id} already exists. Overwrite? (y/n): ")
            if overwrite.lower() != 'y':
                print("Enrollment cancelled.")
                return False

        # Initialize camera
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not open camera.")
            return False

        # Create directory for user images
        user_dir = os.path.join(self.data_dir, user_id)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)

        face_encodings = []
        captured_images = 0
        target_images = 5

        while captured_images < target_images:
            ret, frame = cap.read()

            if not ret:
                print("Error: Failed to capture image.")
                continue

            # Display current frame
            cv2.imshow("Enrollment - Press SPACE to capture", frame)

            key = cv2.waitKey(1)
            if key == 27:  # ESC key to exit
                break
            elif key == 32:  # SPACE key to capture
                # Detect faces
                face_locations = face_recognition.face_locations(frame)

                if len(face_locations) == 0:
                    print("No face detected. Please try again.")
                    continue
                elif len(face_locations) > 1:
                    print("Multiple faces detected. Please ensure only one face is visible.")
                    continue

                # Preprocess the face region
                top, right, bottom, left = face_locations[0]
                face_image = frame[top:bottom, left:right]
                processed_face = self.preprocess_face(face_image)

                # Save the captured image
                image_path = os.path.join(user_dir, f"face_{captured_images}.jpg")
                cv2.imwrite(image_path, processed_face)

                # Compute face encoding
                encoding = face_recognition.face_encodings(frame, face_locations)[0]
                face_encodings.append(encoding.tolist())

                captured_images += 1
                print(f"Captured image {captured_images}/{target_images}")

                # Wait a moment to allow user to change pose
                time.sleep(1)

        cap.release()
        cv2.destroyAllWindows()

        # Save user data
        self.users_data[user_id] = {
            "name": user_id,
            "encodings": face_encodings,
            "enrollment_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.save_user_data()
        print(f"Enrollment complete for user: {user_id}")
        return True

    def authenticate(self):
        """Authenticate a user based on their face"""
        print("Starting face authentication...")

        if not self.users_data:
            print("No users enrolled. Please enroll a user first.")
            return None

        # Initialize camera
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not open camera.")
            return None

        authenticated = False
        authenticated_user = None
        start_time = time.time()
        timeout = 30  # Timeout after 30 seconds

        while not authenticated and (time.time() - start_time) < timeout:
            ret, frame = cap.read()

            if not ret:
                print("Error: Failed to capture image.")
                continue

            # Display current frame
            display_frame = frame.copy()
            cv2.putText(display_frame, "Looking for face...", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow("Authentication", display_frame)

            if cv2.waitKey(1) == 27:  # ESC key to exit
                break

            # Detect faces
            face_locations = face_recognition.face_locations(frame)

            if len(face_locations) == 0:
                continue

            # Get face encodings
            face_encodings = face_recognition.face_encodings(frame, face_locations)

            if not face_encodings:
                continue

            current_encoding = face_encodings[0]

            # Check against all enrolled users
            best_match = None
            lowest_distance = float('inf')

            for user_id, user_data in self.users_data.items():
                stored_encodings = np.array(user_data["encodings"])

                # Calculate distances to all stored encodings for this user
                distances = face_recognition.face_distance(stored_encodings, current_encoding)

                # Get the minimum distance
                min_distance = np.min(distances)

                if min_distance < lowest_distance:
                    lowest_distance = min_distance
                    best_match = user_id

            # If the best match is below the threshold, authenticate
            if best_match and lowest_distance < self.confidence_threshold:
                authenticated = True
                authenticated_user = best_match

                # Display authentication success
                cv2.putText(frame, f"Welcome, {best_match}!", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.rectangle(frame, (face_locations[0][3], face_locations[0][0]),
                              (face_locations[0][1], face_locations[0][2]), (0, 255, 0), 2)
                cv2.imshow("Authentication", frame)
                cv2.waitKey(2000)  # Display for 2 seconds

                # Log successful authentication
                self.log_authentication(best_match, True)
            else:
                # Display authentication failure
                cv2.putText(frame, "Face not recognized", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                if face_locations:
                    cv2.rectangle(frame, (face_locations[0][3], face_locations[0][0]),
                                  (face_locations[0][1], face_locations[0][2]), (0, 0, 255), 2)
                cv2.imshow("Authentication", frame)
                cv2.waitKey(100)

        cap.release()
        cv2.destroyAllWindows()

        if not authenticated:
            print("Authentication failed: No matching face found.")
            # Log failed authentication attempt
            self.log_authentication("unknown", False)
            return None

        print(f"Authentication successful. Welcome, {authenticated_user}!")
        return authenticated_user

    def list_users(self):
        """List all enrolled users"""
        if not self.users_data:
            print("No users enrolled.")
            return

        print("Enrolled users:")
        for user_id, user_data in self.users_data.items():
            print(f"- {user_id} (enrolled on {user_data['enrollment_date']})")

    def delete_user(self, user_id):
        """Delete a user from the system"""
        if user_id not in self.users_data:
            print(f"User {user_id} not found.")
            return False

        confirm = input(f"Are you sure you want to delete user {user_id}? (y/n): ")
        if confirm.lower() != 'y':
            print("Deletion cancelled.")
            return False

        # Delete user data
        del self.users_data[user_id]
        self.save_user_data()

        # Delete user images
        user_dir = os.path.join(self.data_dir, user_id)
        if os.path.exists(user_dir):
            for file in os.listdir(user_dir):
                os.remove(os.path.join(user_dir, file))
            os.rmdir(user_dir)

        print(f"User {user_id} deleted successfully.")
        return True


def main():
    system = FacialRecognitionSystem()

    while True:
        print("\n===== Facial Recognition Authentication System =====")
        print("1. Enroll a new user")
        print("2. Authenticate")
        print("3. List enrolled users")
        print("4. Delete a user")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            user_id = input("Enter user name or ID: ")
            system.enroll_user(user_id)
        elif choice == '2':
            authenticated_user = system.authenticate()
        elif choice == '3':
            system.list_users()
        elif choice == '4':
            user_id = input("Enter user name or ID to delete: ")
            system.delete_user(user_id)
        elif choice == '5':
            print("Exiting system...")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()