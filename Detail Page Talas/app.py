from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pickle
import tensorflow as tf
from keras.preprocessing.sequence import pad_sequences
import sys
import numpy as np
import requests

# Inisialisasi Flask
app = Flask(__name__)
CORS(app)  # Mengaktifkan CORS untuk akses lintas domain

# Memperbaiki masalah dependensi TensorFlow-Keras
sys.modules['keras.src.preprocessing'] = tf.keras.preprocessing

# Path model dan tokenizer
current_dir = os.path.dirname(os.path.abspath(__file__))

tokenizer_A3_path = os.path.join(current_dir, os.pardir, 'Model', 'hoax', 'tokenizer_A3.pkl')
tokenizer_bias_path = os.path.join(current_dir, os.pardir, 'Model', 'bias', 'bias_tokenizer.pkl')

model_A3_path = os.path.join(current_dir, os.pardir, 'Model', 'hoax', 'hoax_detection_A3.tflite')
model_bias_path = os.path.join(current_dir, os.pardir, 'Model', 'bias', 'bias_detection_lstm.tflite')

# Load tokenizer
with open(tokenizer_A3_path, 'rb') as f:
    tokenizer_A3 = pickle.load(f)

with open(tokenizer_bias_path, 'rb') as f:
    tokenizer_bias = pickle.load(f)

# Load model TFLite
interpreterHoaks = tf.lite.Interpreter(model_path=model_A3_path)
interpreterHoaks.allocate_tensors()

interpreterBias = tf.lite.Interpreter(model_path=model_bias_path)
interpreterBias.allocate_tensors()

# Ambil informasi tensor input-output
input_details_hoaks = interpreterHoaks.get_input_details()
output_details_hoaks = interpreterHoaks.get_output_details()

input_details_bias = interpreterBias.get_input_details()
output_details_bias = interpreterBias.get_output_details()

# Endpoint: Prediksi Semua Berita
@app.route('/predict-all', methods=['GET'])
def predict_all_news():
    api_url = 'http://127.0.0.1:5000/api/news'
    try:
        # Ambil berita dari API eksternal
        response = requests.get(api_url)
        response.raise_for_status()
        news_data = response.json()

        predictions = []
        for i, news_item in enumerate(news_data):
            try:
                news_text = [news_item['title'] + " " + news_item['content']]

                # Prediksi Hoax
                new_sequences_hoax = tokenizer_A3.texts_to_sequences(news_text)
                new_padded_hoax = pad_sequences(new_sequences_hoax, maxlen=100).astype('float32')
                interpreterHoaks.set_tensor(input_details_hoaks[0]['index'], new_padded_hoax)
                interpreterHoaks.invoke()
                predictions_hoax = np.copy(interpreterHoaks.get_tensor(output_details_hoaks[0]['index']))

                # Prediksi Bias
                new_sequences_bias = tokenizer_bias.texts_to_sequences(news_text)
                new_padded_bias = pad_sequences(new_sequences_bias, maxlen=30).astype('float32')
                interpreterBias.set_tensor(input_details_bias[0]['index'], new_padded_bias)
                interpreterBias.invoke()
                predictions_bias = np.copy(interpreterBias.get_tensor(output_details_bias[0]['index']))

                # Tambahkan hasil prediksi
                predictions.append({
                    "title": news_item['title'],
                    "content": news_item['content'],
                    "image": news_item.get('image', ''),
                    "link": news_item.get('link', ''),
                    "hoax_label": "Hoax" if predictions_hoax[0][0] > 0.5 else "Not Hoax",
                    "hoax_confidence": float(predictions_hoax[0][0]),
                    "bias_label": "Bias" if predictions_bias[0][0] > 0.5 else "Neutral",
                    "bias_confidence": float(predictions_bias[0][0])
                })
            except Exception as e:
                print(f"Error processing news item {i}: {str(e)}")
        return jsonify(predictions)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news from API: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Endpoint: Prediksi Individual
@app.route('/predict', methods=['POST'])
def predict_individual_news():
    try:
        data = request.json
        if not data or 'title' not in data or 'content' not in data:
            return jsonify({"error": "Invalid input: 'title' and 'content' are required"}), 400

        news_text = [data['title'] + " " + data['content']]

        # Prediksi Hoax
        new_sequences_hoax = tokenizer_A3.texts_to_sequences(news_text)
        new_padded_hoax = pad_sequences(new_sequences_hoax, maxlen=100).astype('float32')
        interpreterHoaks.set_tensor(input_details_hoaks[0]['index'], new_padded_hoax)
        interpreterHoaks.invoke()
        predictions_hoax = np.copy(interpreterHoaks.get_tensor(output_details_hoaks[0]['index']))

        # Prediksi Bias
        new_sequences_bias = tokenizer_bias.texts_to_sequences(news_text)
        new_padded_bias = pad_sequences(new_sequences_bias, maxlen=30).astype('float32')
        interpreterBias.set_tensor(input_details_bias[0]['index'], new_padded_bias)
        interpreterBias.invoke()
        predictions_bias = np.copy(interpreterBias.get_tensor(output_details_bias[0]['index']))

        # Format hasil
        response = {
            "title": data['title'],
            "content": data['content'],
            "hoax_label": "Hoax" if predictions_hoax[0][0] > 0.5 else "Not Hoax",
            "hoax_confidence": float(predictions_hoax[0][0]),
            "bias_label": "Bias" if predictions_bias[0][0] > 0.5 else "Neutral",
            "bias_confidence": float(predictions_bias[0][0])
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Jalankan server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
