from flask import Flask, render_template, request
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier

app = Flask(__name__)

# Load the updated dataset (without CROP_PRICE)
df = pd.read_csv('indiancrop_dataset.csv')

# Encode categorical labels (CROP)
crop_encoder = LabelEncoder()
df['CROP'] = crop_encoder.fit_transform(df['CROP'])

# Encode "STATE"
state_encoder = LabelEncoder()
df['STATE'] = state_encoder.fit_transform(df['STATE'])

# Define features & target
X = df.drop(columns=['CROP'])
y = df['CROP']

# Train the model
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_scaled, y)

# Function to recommend a crop
def recommend_crop(features):
    features = np.array(features).reshape(1, -1)
    features = scaler.transform(features)
    prediction = model.predict(features)
    return crop_encoder.inverse_transform(prediction)[0]

# Flask routes
@app.route('/')
def home():
    states = sorted(df['STATE'].unique())  # Get unique encoded states
    state_names = state_encoder.inverse_transform(states)  # Decode to original state names
    return render_template('template.html', states=state_names)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get form data
        n = float(request.form['N'])
        p = float(request.form['P'])
        k = float(request.form['K'])
        temp = float(request.form['temperature'])
        humidity = float(request.form['humidity'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])
        state_name = request.form['state']

        # Convert state name to encoded value
        state_encoded = state_encoder.transform([state_name])[0]

        # Create feature array
        data = [n, p, k, temp, humidity, ph, rainfall, state_encoded]

        # Predict crop
        result = recommend_crop(data)

        return render_template('template.html', states=state_encoder.inverse_transform(sorted(df['STATE'].unique())), prediction_text=f'Recommended Crop: {result}')
    
    except Exception as e:
        return render_template('template.html', states=state_encoder.inverse_transform(sorted(df['STATE'].unique())), prediction_text=f'Error: {str(e)}')

if __name__ == '__main__':
    app.run(debug=True)
