# Physical AI & Humanoid Robotics

This educational website provides a comprehensive guide to embodied AI systems, focusing on ROS 2 as the nervous system of humanoid robots. The content connects AI agents (Python-based) with physical robot control systems.

## About This Book

This book is designed for:
- Software developers with basic Python knowledge
- AI learners transitioning from digital AI to physical/embodied AI
- Robotics beginners preparing for humanoid simulation and control

No prior ROS experience is required.

## Course Structure

### Module 1: The Robotic Nervous System (ROS 2)
- Chapter 1: ROS 2 as the Robotic Nervous System (Conceptual Foundations)
- Chapter 2: ROS 2 as Middleware for Physical AI Systems
- Chapter 3: Digital AI Pipelines vs Physical Robot Control

### Module 2: The Digital Twin (Gazebo & Unity)
- Chapter 1: Physics-Based Simulation with Gazebo
- Chapter 2: High-Fidelity Environments with Unity
- Chapter 3: Sensor Simulation for Perception

### Module 3: The AI-Robot Brain (NVIDIA Isaac™)
- Chapter 1: NVIDIA Isaac Sim – Photorealistic Simulation & Synthetic Data
- Chapter 2: Isaac ROS – Hardware-Accelerated Perception
- Chapter 3: Nav2 for Humanoid Navigation

### Module 4: Vision-Language-Action (VLA) – The Cognitive Humanoid
- Chapter 1: Voice-to-Action Interfaces – Speech as Control Modality
- Chapter 2: Cognitive Planning with LLMs – High-Level Reasoning for Robots
- Chapter 3: Capstone – The Autonomous Humanoid System

## Project Setup

### Prerequisites

- Node.js 18+ installed
- Basic command line knowledge
- Git installed for version control

### Installation

```
$ npm install
```

### Local Development

```
$ npm start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

### Build

```
$ npm run build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

### Deployment

```
$ GIT_USER=<Your GitHub username> npm run deploy
```

If you are using GitHub pages for hosting, this command is a convenient way to build the website and push to the `gh-pages` branch.
"# Humanoid-robotics-ai-book" 
