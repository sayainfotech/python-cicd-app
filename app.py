from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <html>
        <head><title>Python CI/CD Application</title></head>
        <body>
            <h1>Welcome to Python CI/CD!</h1>
            <p>Deployed using Jenkins, Docker and Kubernetes.</p>
            <p>Application is running successfully.</p>
        </body>
    </html>
    """

@app.route("/api")
def api():
    return jsonify({
        "application": "Python CI/CD App",
        "language": "Python",
        "framework": "Flask",
        "status": "running"
    })

@app.route("/health")
def health():
    return jsonify({"status": "UP"}), 200

@app.route("/version")
def version():
    return jsonify({
        "version": os.getenv("APP_VERSION", "1.0.0")
    })

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000"))
    )
