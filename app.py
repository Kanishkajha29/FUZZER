from flask import Flask, render_template, request
from utils.rate import perform_rate_limit_test, format_url

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results', methods=['POST'])
def results():
    target_url = request.form.get('target_url')
    num_requests = request.form.get('num_requests', type=int)
    
    if not target_url or not num_requests or num_requests <= 0:
        return render_template(
            'index.html', 
            error="Please enter a valid target endpoint and a positive number of requests."
        )

    # Format URL to ensure it is valid
    formatted_url = format_url(target_url)

    # Perform rate limit testing
    results = perform_rate_limit_test(formatted_url, num_requests)
    return render_template('results.html', results=results, num_requests=num_requests)

if __name__ == '__main__':
    app.run(debug=True)
