from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import GlobalVariables
import Scraper
import threading
import re
from unidecode import unidecode

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

if __name__ == '__main__':
    app.run(debug=True)#run
