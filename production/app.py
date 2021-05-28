from workerA import get_predictions

from flask import (
    Flask,
    request,
    jsonify,
    Markup,
    render_template
)

app = Flask(__name__)


@app.route("/")
def index():
    return '<h1>Welcome to Github Stargazer predictor</h1>'


@app.route("/predictions", methods=['POST', 'GET'])
def predictions():
    if request.method == 'POST':
        results = get_predictions.delay()
        results = results.get()
        return render_template('result.html', results=results)

    return '''<form method="POST">
    <input type="submit">
    </form>'''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100, debug=True)
