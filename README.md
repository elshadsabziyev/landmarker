# LandMarker (Landmark Marker) 🗺️📌

## Table of Contents
- 🌟 [Introduction](#introduction)
- ⭐ [Features](#features)
- 💻 [Technologies Used](#technologies-used)
- 🛠️ [Installation](#installation)
- 🚀 [Usage](#usage)
- 🌐 [Deployment](#deployment)
- 🏗️ [Architecture](#architecture)
- 🛣️ [Roadmap](#roadmap)
- 👨‍💻 [Project Team](#project-team)
- 🤝 [Contributing](#contributing)
- 📝 [License](#license)

---

## 🌟 Introduction

LandMarker is a Python-based application designed for landmark detection using the Google Cloud Vision API, Streamlit, and Folium.

---

## ⭐ Features

LandMarker offers the following features:
- **Image Upload**: Easily upload images containing landmarks for recognition.
- **Landmark Detection**: Utilizes the Google Cloud Vision API for precise landmark recognition in images.
- **Geographical Mapping**: Retrieves geographical coordinates (latitude and longitude) of detected landmarks.
- **Interactive Map Display**: Exhibits detected landmarks on an interactive map using the Folium library.

---

## 💻 Technologies Used

The project utilizes the following technologies:
- **Python**: Core programming language.
- **Google Cloud Vision API**: Empowers the system for landmark detection in images.
- **Folium**: Python library employed for creating interactive maps.
- **Streamlit**: Web application framework facilitating the user interface.
- **PIL (Python Imaging Library)**: Utilized for image processing and display.

---

## 🛠️ Installation

To set up and run this project locally, follow these steps:
1. **Clone the repository**.
2. **Set Up Environment**: Create a virtual environment and install required dependencies.
3. **Google Cloud Platform (GCP) Setup**: Establish a GCP project, enable the Vision API, and configure credentials.
4. **Running the Application**: Execute specific commands to run the Streamlit application.

---

## 🚀 Usage

For local usage, credentials should be stored in a secret.toml file. For deployment on Streamlit Sharing or other hosting platforms, ensure the application is appropriately configured for deployment and follow platform-specific instructions.

---

## 🌐 Deployment

- **Environment Variables**: Set up environment variables using Streamlit's interface or the secret.toml file.
- **Geo API Integration**: Utilize the geographical API for enhanced mapping features and better user experience.
- **Streamlit Sharing**: Sign up for Streamlit Sharing or select a hosting platform and follow the provided instructions for deployment.

---

## 🏗️ Architecture

### Components
- **Google Cloud Vision API**: Handles landmark detection in images.
- **Python Backend**: Utilizes Streamlit to create the user interface and Folium for map generation.
- **Folium Map**: Used to display detected landmarks on an interactive map.

### Workflow
1. User uploads an image via the Streamlit interface.
2. Python backend sends the image data to the Google Cloud Vision API for landmark detection.
3. The API returns landmark information (name and coordinates).
4. Folium library creates an interactive map displaying the detected landmark.

---

## 🛣️ Roadmap

### Version 1.0.0 (Current Release)
- Basic functionality with landmark detection and mapping features implemented.
- Local deployment and usage instructions provided.
- Integration with Geo API for enhanced mapping capabilities.
- Streamlit hosting guide included.

### Future Enhancements
- Advanced API Integration for more accurate and diverse landmark identification.
- Real-time camera capture capabilities for on-the-fly landmark detection.
- AI-Enhanced Landmark Identification for improved accuracy.
- Cloud-Based Mapping for scalability and collaborative mapping features.

---

## 👨‍💻 Project Team

- [Elshad Sabziyev](https://github.com/elshadsabziyev) 👨‍💻
- [Arif Najafov](https://github.com/member-profile) 👨‍💻

---

## 🤝 Contributing

Contributions are welcome! Fork the repository, make changes, and submit a pull request.

---

## 📝 License

This project is licensed under the [MIT License](LICENSE). 📄
