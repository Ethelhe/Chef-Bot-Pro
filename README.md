# 👨‍🍳 Chef-Bot Pro

Chef-Bot Pro is an intelligent, content-based recipe recommendation system built with Python and Streamlit. It uses Natural Language Processing (TF-IDF Vectorizer) and Cosine Similarity to recommend recipes based on user-provided ingredients and specific dietary/nutritional goals.

## 🚀 Features
* **Content-Based Filtering:** Recommends recipes by analyzing ingredient similarities using TF-IDF and Cosine Similarity.
* **Nutritional & Dietary Filtering:** Allows filtering by maximum calories, minimum protein, and specific diets (e.g., Vegan, Vegetarian, Low-Carb).
* **Pantry Management:** Users can add available ingredients to their virtual pantry to get personalized results.
* **Categorical Asset Mapping:** Displays consistent, high-quality visuals for recipes using a robust fallback mechanism.

## 🛠️ Required Libraries
To run this project, you need Python 3.8+ and the following libraries:
* `streamlit`
* `pandas`
* `scikit-learn`

*Note: All dependencies are listed in the requirements.txt file.*

## ⚙️ Setup and Installation (Step-by-Step)

Follow these steps to run the application on your local machine:

**Step 1: Clone the Repository**
Open your terminal and clone this repository to your local machine:
> git clone https://github.com/Ethelhe/Chef-Bot-Pro.git
> cd Chef-Bot-Pro

**Step 2: Set Up a Virtual Environment (Recommended)**
It is recommended to use a virtual environment to avoid library conflicts.
> python -m venv venv
> venv\Scripts\activate

**Step 3: Install Dependencies**
Install all required libraries using the requirements.txt file:
> pip install -r requirements.txt

**Step 4: Run the Application**
Start the Streamlit server to launch the app:
> streamlit run app.py

The application will automatically open in your default web browser at http://localhost:8501.

## 📂 Project Structure
* `app.py`: The main Streamlit application script handling the UI and user inputs.
* `ml_engine.py`: Contains the machine learning logic (TF-IDF, Cosine Similarity) and data processing functions.
* `data/recipes.csv`: The Kaggle Food Recipes dataset used for recommendations.
* `requirements.txt`: The list of Python packages required to run the app.

## 👨‍💻 Author
**Muhammed Mansur Güney** Data Science and Analytics (DSA-102 Project Submission)