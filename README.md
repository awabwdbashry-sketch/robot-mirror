# 🤖 Robot Mirror ✋

A real-time computer vision project that creates an interactive **Robot Mirror** controlled by the user's hand movements.

The project uses a webcam to track the user's hand through **MediaPipe**, processes the camera feed using **OpenCV**, and uses the detected hand information to control an animated robot interface.

The result is a fun **human-computer interaction** experience where the robot responds to the user's hand movement.

---

## ✨ Features

- 📷 Real-time webcam processing
- ✋ Real-time hand detection
- 🎯 Hand landmark tracking using MediaPipe
- 🤖 Interactive animated robot
- 🪞 Mirror-style interaction
- 🖐️ Robot response to hand movement
- 🎨 Visual effects and animations
- ⚡ Real-time response
- 🧩 Modular multi-file architecture
- ⚙️ Configurable project settings
- 🖥️ Desktop computer vision application

---

## 🛠️ Technologies Used

- 🐍 **Python**
- 📷 **OpenCV** — Camera capture, image processing, and rendering
- ✋ **MediaPipe** — Hand detection and landmark tracking
- 🔢 **NumPy** — Numerical and image-processing operations

---

## ⚙️ How It Works

The application continuously captures frames from the webcam and detects the user's hand.

MediaPipe identifies the hand landmarks and provides their coordinates. These coordinates are then processed by the project logic and used to control the robot's behavior and animations.

### 🔄 Processing Pipeline

```text
Webcam
   ↓
OpenCV
   ↓
MediaPipe Hand Detection
   ↓
Hand Landmarks
   ↓
Hand Position / Movement
   ↓
Robot Logic
   ↓
Animation + Effects
   ↓
Interactive Robot Mirror
```

---

## 🤖 Robot Interaction

The main idea of the project is to make the robot behave as a visual mirror of the user's hand interaction.

When the camera detects the user's hand:

1. 📷 The camera captures the frame.
2. ✋ MediaPipe detects the hand.
3. 🎯 Hand landmarks are extracted.
4. 📍 Hand position and movement are processed.
5. 🤖 The robot receives the calculated movement.
6. 🎨 The robot animation is updated.
7. 🪞 The result is displayed in real time.

This creates a responsive interaction between the user and the virtual robot.

---

## ✋ Hand Tracking

MediaPipe provides a set of hand landmarks that describe the structure and position of the detected hand.

These landmarks can be used to determine:

- 📍 Hand position
- ↔️ Horizontal movement
- ↕️ Vertical movement
- 🖐️ Hand orientation
- 👆 Finger positions
- 🎯 Movement changes

The project uses this information as input for the robot system.

---

## 🎨 Animation System

The robot is built using a modular animation system.

The animation components are responsible for updating the robot's visual state based on the detected hand movement.

This structure makes it easier to:

- 🤖 Change robot behavior
- 🎨 Add new animations
- ✨ Add visual effects
- 🧩 Modify individual components
- 🚀 Extend the project in the future

---

## ✨ Effects System

The project includes a dedicated effects component for visual feedback.

The effects system can be used to create a more dynamic experience by adding visual reactions to the robot's behavior.

This keeps visual effects separated from the main hand-tracking logic.

---

## ⚙️ Configuration

Project settings are separated into a dedicated configuration file.

This allows important parameters to be organized without placing all configuration values directly inside the main application.

The modular configuration approach makes the project easier to maintain and customize.

---

## 🧩 Project Architecture

Unlike simple hand-tracking demos, this project is organized into multiple Python modules.

Each module has a specific responsibility:

- `robot_mirror.py` — Main application and execution flow
- `config.py` — Project configuration
- `hand_tracker.py` — Hand detection and tracking
- `animation.py` — Robot animation logic
- `robot.py` — Robot representation and behavior
- `effects.py` — Visual effects
- `background.py` — Background rendering
- `utils.py` — Utility functions

This separation improves code organization and makes individual components easier to maintain.

---

## 📁 Project Structure

```text
robot-mirror/
│
├── robot_mirror.py
├── config.py
├── hand_tracker.py
├── animation.py
├── robot.py
├── effects.py
├── background.py
├── utils.py
│
├── requirements.txt
├── README.md
├── README_AR.md
└── .gitignore
```

---

## 📦 Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/awabwdbashry-sketch/robot-mirror.git
```

### 2️⃣ Enter the Project Directory

```bash
cd robot-mirror
```

### 3️⃣ Create a Virtual Environment

```bash
python -m venv venv
```

### 4️⃣ Activate the Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / macOS

```bash
source venv/bin/activate
```

### 5️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 📋 Requirements

The project requires:

```text
opencv-python>=4.8.0
mediapipe>=0.10.9
numpy>=1.24.0
```

Python **3.9+** is recommended.

A working webcam is also required for real-time hand tracking.

---

## ▶️ Usage

Run the main application:

```bash
python robot_mirror.py
```

### 🖥️ Using the Application

1. 📷 Make sure your webcam is connected.
2. ▶️ Start the application.
3. ✋ Place your hand inside the camera view.
4. 🖐️ Move your hand naturally.
5. 🤖 Observe the robot responding to your movement.
6. 🛑 Exit the application using the project's configured exit mechanism.

---

## 💡 Applications

The concepts demonstrated by this project can be used in:

- 🤖 Human-robot interaction
- 🖐️ Gesture-controlled interfaces
- 🎮 Interactive applications
- 🧑‍💻 Computer vision experiments
- 🎨 Interactive visual installations
- 🎓 Educational projects
- 🥽 Touchless interfaces
- 🧠 AI and computer vision prototypes

---

## ⭐ Advantages

- 📷 Uses a standard webcam
- ✋ Natural hand-based interaction
- ⚡ Real-time processing
- 🤖 Interactive robot concept
- 🧩 Modular architecture
- 🎨 Extensible animation system
- ✨ Separate visual effects system
- 🔧 Easy to expand with additional behaviors

---

## 🚀 Future Improvements

Possible future improvements include:

- 🖐️ Support for multiple hand gestures
- 👥 Support for two hands
- 🤖 More advanced robot behaviors
- 🎭 Facial expression animations
- 👀 Eye tracking
- 🗣️ Voice interaction
- 🔊 Sound effects
- 🎨 More advanced visual effects
- 🧠 AI-based behavior prediction
- 🎮 Gesture-controlled mini games
- 📱 Mobile or web version
- 🌐 Remote robot control integration

---

## 🎯 Project Purpose

The main purpose of **Robot Mirror** is to demonstrate how hand tracking can be combined with animation and interactive graphics to create an engaging human-computer interaction experience.

The project combines:

**Webcam → Hand Tracking → Movement Detection → Robot Logic → Animation → Visual Effects**

It is a practical example of how computer vision can be used beyond simple detection and classification to create interactive visual systems.

---

## 📄 License

This project is intended for educational and experimental purposes.

You are free to study, modify, and extend the project according to your needs.

---

## ⭐ Support

If you find this project useful or interesting, consider giving the repository a ⭐ on GitHub.

**Repository:**

`https://github.com/awabwdbashry-sketch/robot-mirror.git`

---

**Built with 🐍 Python, 📷 OpenCV, ✋ MediaPipe, 🤖 and Computer Vision.**
## 👨‍💻 Developer

**Awab Bashary | AwabBuilds**

GitHub: **awabwdbashry-sketch**

