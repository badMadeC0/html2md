from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    import os
    default_port = 10000
    port_str = os.environ.get('PORT')
    try:
        port = int(port_str) if port_str is not None else default_port
    except ValueError:
        print(f"Warning: Invalid PORT environment variable value {port_str!r}; falling back to default {default_port}.")
        port = default_port
    app.run(host='0.0.0.0', port=port)
