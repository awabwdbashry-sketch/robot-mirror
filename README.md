# Robot Mirror 🤖✋

A real-time computer vision project that creates an animated robot character controlled by hand movements.

The project uses MediaPipe Hands to track the user's hand and mirrors its movement through an animated robot rendered with OpenCV.

## ✨ Features

- Real-time hand tracking
- Robot hand and arm mirroring
- Finger movement tracking
- Smooth motion using EMA smoothing
- Animated robot body
- Breathing animation
- Idle movement
- Eye blinking
- Dynamic facial expressions
- Sci-fi animated background
- Glow effects
- Particles
- Hand motion trails
- Real-time OpenCV rendering

## 🛠️ Technologies

- Python
- OpenCV
- MediaPipe
- NumPy
- Dataclasses
- Math
- Time

## ⚙️ How It Works

The webcam captures the user's hand.

MediaPipe detects the hand landmarks and provides their coordinates.

The project processes these landmarks and converts the hand movement into a robot pose.

The robot then mirrors the detected hand and finger movements.

Additional animation systems create:

- Smooth motion
- Breathing
- Swaying
- Blinking
- Facial expressions
- Particles
- Glow effects
- Hand trails
- Animated backgrounds

## 🧩 Project Architecture

The project is divided into several modules.

### `robot_mirror.py`

Main application entry point.

Responsible for:

- Starting the webcam
- Running the main loop
- Connecting hand tracking with the robot
- Rendering the final scene

### `config.py`

Central configuration module.

Contains:

- Colors
- Robot proportions
- Animation settings
- Visual settings
- Keyboard controls
- Other project configuration

### `hand_tracker.py`

MediaPipe hand-tracking wrapper.

Responsible for:

- Detecting the hand
- Reading landmarks
- Providing simplified hand-tracking data

### `animation.py`

Animation and motion-processing system.

Includes:

- EMA smoothing
- Blinking
- Idle motion
- Robot pose management

### `robot.py`

Robot rendering system.

Responsible for drawing:

- Head
- Body
- Arms
- Hands
- Fingers
- Legs
- Facial elements

### `effects.py`

Visual effects system.

Includes:

- Glow
- Particles
- Hand trails
- Shadows

### `background.py`

Generates the animated sci-fi background.

### `utils.py`

Contains reusable mathematical and drawing utilities.

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/awabwdbashry-sketch/robot-mirror.git
cd robot-mirror