from flask import Flask, render_template, request
from utils.info_gthr import get_network_map, get_whois_info, get_ssl_info

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('target_url')
        options = {
            "network_map": request.form.get('network_map') == 'yes',
            "whois_info": request.form.get('whois_info') == 'yes',
            "ssl_info": request.form.get('ssl_info') == 'yes'
        }
        results = {}

        if options['network_map']:
            results['network_map'] = get_network_map(url)

        if options['whois_info']:
            results['whois_info'] = get_whois_info(url)

        if options['ssl_info']:
            results['ssl_info'] = get_ssl_info(url)

        return render_template('result.html', url=url, results=results)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
