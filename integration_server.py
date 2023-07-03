from flask import Flask, request
import os

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.post("/scan")
def scan():
    id = request.args.get("id")
    os.system(f"touch .{id}")
    return ""
