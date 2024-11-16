from flask import Flask, render_template, request
import os
from utils.dir_fuzz import dir_fuzz  # Import dir_fuzz function from utils

app = Flask(__name__)

# Ensure necessary directories exist
os.makedirs('uploads', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fuzz', methods=['POST'])
def fuzz():
    target_url = request.form['target_url']
    wordlist_choice = request.form['wordlist']

    # Handle custom wordlist upload
    if wordlist_choice == 'custom':
        wordlist = request.files['wordlist_file']
        wordlist_path = os.path.join('uploads', wordlist.filename)
        wordlist.save(wordlist_path)
    else:
        wordlist_path = os.path.join('default_wordlists', 'directory.txt')

    # Run the fuzzing function and get results
    fuzz_results = dir_fuzz(target_url, wordlist_path)
    return render_template('results.html', target_url=target_url, fuzz_results=fuzz_results)

if __name__ == '__main__':
    app.run(debug=True)
    