import io
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import GlobalVariables
import Scraper
import threading
import re
from unidecode import unidecode
import tensorflow as tf
from PIL import Image
import numpy as np
import cv2

app = Flask(__name__)
CORS(app)

#initiates the scraper
@app.route('/initiate_scrape', methods=['POST'])
def initiate_scrape():
    #make a new user uid takes the params words and language
    newUserUID = str(uuid.uuid4()) 
    words = request.json["text"]
    language = request.json["language"]

    #words lower because upper have no sens
    words = words.lower()
    words = unidecode(words)#other langauges extra letters besides english ones get transformed their english equivalent
    broken_words = re.findall(r"\b[a-zA-Z]+\b", words)#gets the list of words

    broken_words = list(filter(lambda word: len(word) >= 3, broken_words))#filters words that are less than 3 to avoid searching for "ml" for example 

    print(broken_words)

    with GlobalVariables.threadLock:#with thread lock initiate the user in the 2 dictionaries
        GlobalVariables.procentageReadySraper[newUserUID] = 0
        GlobalVariables.ResultsScraper[newUserUID] = []

    def start_scraper():#function to start the scraper
        scraper = Scraper.Scraper(newUserUID,broken_words,language)
        scraper.start_scraper()

    thread = threading.Thread(target=start_scraper, daemon=True)#new thread for every new user 
    thread.start()#starts the thread

    return jsonify({"user_id": newUserUID, "message": "Scraper started"}), 202#sends back the uid of the user and the status


@app.route('/cancel_scrape_request/<user_id>', methods=['POST'])
#not used if i remember corectly because the thread can crash the program cause of errors
def delete_scraper_data(user_id):
    with GlobalVariables.threadLock:#if cancelled then just delete the new declarations
        if user_id in GlobalVariables.procentageReadySraper:
            del GlobalVariables.procentageReadySraper[user_id]
            del GlobalVariables.ResultsScraper[user_id]

    return jsonify({"message":"canceled successfully"}), 202


@app.route('/progress/<user_id>', methods=['GET'])
def progress_stream(user_id):
    progress = 0#prints the progress to the user
    with GlobalVariables.threadLock:#every 5 seconds it is queried for the procentage
        if user_id not in GlobalVariables.procentageReadySraper:
            return jsonify({"error": "User ID not found"}), 404

        progress = GlobalVariables.procentageReadySraper[user_id]
    return jsonify({"progress": progress})#sends the progress

@app.route('/results_scrape/<user_id>', methods=['GET'])
def ResultedLinks(user_id):

    with GlobalVariables.threadLock:#the scrape is now done and we can query this to get back the results
        print("reuqested id",user_id)
        print(GlobalVariables.procentageReadySraper)

        if user_id in GlobalVariables.ResultsScraper:
            cpy = GlobalVariables.ResultsScraper[user_id]#after everything is done we delete the user to not take up space

            del GlobalVariables.procentageReadySraper[user_id]
            del GlobalVariables.ResultsScraper[user_id]

            return jsonify({"results": cpy}), 202#we send the lists of results

    return jsonify({"results":"error"}), 404#error

@app.route('/startDiagnosis', methods=['POST'])
def StartDiagnosis():

    if 'photo' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['photo']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Read the file into memory
        
        image = Image.open(io.BytesIO(file.read()))
        
        # Preprocess the image (resize and normalize as needed by your model)
        image_array = np.array(image)

        gray_img = image_array
        
        if len(gray_img.shape) != 2:
            gray_img = cv2.cvtColor(gray_img, cv2.COLOR_RGB2GRAY)
        clahe = cv2.createCLAHE(clipLimit=3, tileGridSize=(10, 10))
        processed_img = clahe.apply(gray_img)

        final_img = cv2.add(processed_img, 5)
        final_img = cv2.cvtColor(final_img, cv2.COLOR_GRAY2RGB)
        final_img = cv2.resize(final_img, (224, 224))
        final_img = final_img.astype(np.float32)
        final_processed_img = final_img / 255.0

        # Convert to TensorFlow tensor
        tensor = tf.convert_to_tensor(final_processed_img, dtype=tf.float32)
        tensor = tf.expand_dims(tensor, axis=0)  # Add batch dimension

        # Load your TensorFlow model
        model = tf.keras.models.load_model('./idenbol_1.0.h5')  # Replace with your model's path

        # Run inference
        predictions = model(tensor)
        predictions = tf.squeeze(predictions, axis=0)

        binary_predictions = [True if pred >= 0.5 else False for pred in predictions]

        return jsonify({
            "message": "Photo processed successfully",
            "predicted_class": binary_predictions,
        }), 200
    except Exception as e:
        print(str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)#run
