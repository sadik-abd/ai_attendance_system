from flask import Flask
from flask import render_template, request, redirect, url_for, session

app = Flask(__name__)

@app.route('/', methods=["GET"])
def main():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()