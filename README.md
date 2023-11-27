# 🌍 LoBot (Location Bot)

## 📋 Table of Contents

- [🚀 Introduction](#-introduction)
- [✨ Features](#-features)
- [🛠️ Technologies Used](#%EF%B8%8F-technologies-used)
- [⚙️ Installation](#%EF%B8%8F-installation)
- [🔧 Usage](#-usage)
- [🏗️ Architecture](#%EF%B8%8F-architecture)
- [🗺️ Roadmap](#%EF%B8%8F-roadmap)
- [👥 Project Team](#-project-team)
- [🤝 Contributing](#-contributing)
- [📝 License](#-license)

## 🚀 Introduction

LoBot (Location Bot) is a Python-based application utilizing the Google Cloud Vision API for landmark detection in images. This system enables users to upload images, identify landmarks within them, retrieve the landmark's name, acquire its geographical coordinates (latitude and longitude), and display the detected landmarks on a map using the Folium library.

## ✨ Features

- **Image Upload**: Users can upload images containing landmarks for recognition.
- **Landmark Detection**: Utilizes Google Cloud Vision API for landmark recognition in images.
- **Geographical Mapping**: Retrieves geographical coordinates (latitude and longitude) of detected landmarks.
- **Interactive Map Display**: Shows detected landmarks on an interactive map using Folium library.

## 🛠️ Technologies Used

- **Python**: Core programming language used for the application.
- **Google Cloud Vision API**: For landmark detection in images.
- **Folium**: Python library for creating interactive maps.
- **Streamlit**: Web application framework for building the user interface.
- **PIL (Python Imaging Library)**: Used for image processing and display.

## ⚙️ Installation

To set up and run this project locally, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/lobot-location-bot.git
    cd lobot-location-bot
    ```

2. **Set Up Environment**:
   - Create a virtual environment (recommended):
     ```bash
     python3 -m venv venv
     source venv/bin/activate  # Linux / MacOS
     .\venv\Scripts\activate   # Windows
     ```
   - Install required dependencies:
     ```bash
     pip install -r requirements.txt
     ```

3. **Google Cloud Platform (GCP) Setup**:
   - Create a GCP project and enable the Vision API.
   - Obtain API key or service account credentials for Vision API access.
   - Set the credentials as environmental variables:
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials.json  # Linux / MacOS
     set GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials.json    # Windows
     ```

4. **Running the Application**:
   - Run the Streamlit application by executing:
     ```bash
     streamlit run main.py
     ```
   - Access the application through the provided URL (usually on `http://localhost:8501`).

5. **Using the Application**:
   - Once the application is running, you'll be prompted to upload an image containing a landmark.
   - After uploading the image, the system will use Google Cloud Vision API to detect the landmark.
   - Detected landmarks will be displayed along with their names, confidence scores, and geographical coordinates on an interactive map generated using Folium.

6. **Note**:
   - Ensure stable internet connectivity for Google Cloud Vision API usage.
   - Properly configure Streamlit's secrets.toml or environment variables for API key/secrets handling.

## 🔧 Usage

For deploying the application on Streamlit Sharing or other hosting platforms:

1. **Streamlit Deployment**:
   - Ensure the application is properly configured for deployment.
   - Sign up for Streamlit Sharing or choose a hosting platform of your choice.
   - Follow platform-specific instructions to deploy the application.

For local usage on Windows or other operating systems, follow similar steps provided in the installation section with respective command syntax adjustments.

## 🏗️ Architecture

### Components

- **Google Cloud Vision API**: Handles landmark detection in images.
- **Python Backend**: Utilizes Streamlit to create the user interface and Folium for map generation.
- **Folium Map**: Used to display detected landmarks on an interactive map.

### Workflow

1. User uploads an image through the Streamlit interface.
2. Python backend sends the image data to the Google Cloud Vision API for landmark detection.
3. The API returns landmark information (name and coordinates).
4. Folium library creates an interactive map and displays the detected landmark.

## 🗺️ Roadmap

### 🚀 Version 1.0.0 (Current Release)

- **Basic Functionality**:
  - Landmark detection and mapping features implemented.
  - Local deployment and usage instructions provided.
  - Streamlit hosting guide provided.
  - Auto-zoom, map download functionalities added.
  - App redesigned to be more colorful.

### 🚀 Future Enhancements

- **📡 Improved API Integration**:
  - Implement caching mechanisms for API requests to enhance performance.
  - Explore asynchronous processing for quicker responses.
  - Integrate Wikipedia and Britannica APIs to provide additional information about recognized landmarks.

- **🌐 Advanced Mapping Framework**:
  - Explore advanced mapping frameworks or libraries for a more interactive and visually appealing mapping experience.
  - Include support for more image file formats.

- **🌍 Direct Camera Capture**:
  - Enable direct photo capture capabilities from cameras and mobile devices for seamless image recognition.
  - Implement real-time landmark detection for instant feedback on captured images.

- **🤖 AI-Powered Landmark Identification**:
  - Utilize AI models trained specifically for landmark identification to improve accuracy and reliability.
  - Incorporate sophisticated algorithms for better handling of complex landscapes and diverse landmarks.

- **🌐 Cloud-Based Mapping**:
  - Integrate cloud-based mapping services for scalability and robustness in handling large volumes of mapping data.
  - Implement collaborative mapping features to allow multiple users to contribute to landmark identification and mapping.

- **🔒 Privacy and Security**:
  - Strengthen data privacy measures for handling data.

## 👥 Project Team

- [Elshad Sabziyev](https://github.com/elshadsabziyev)
- [Arif Najafov](https://github.com/member-profile)

## 🤝 Contributing

Contributions to improve functionality or add new features are welcome! To contribute:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature/your-feature`
3. Make changes and commit: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request.

## 📝 License

This project is licensed under the [MIT License](LICENSE).
