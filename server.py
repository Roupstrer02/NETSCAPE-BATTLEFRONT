from flask import Flask, render_template, request


def activate_server():
    print("Starting Game Server...")

    app = Flask(__name__)


    @app.route('/', methods=["GET"])
    def hello():
        return render_template('index.html')

    @app.route('/', methods=["POST"])
    def user_input():
        
        unit_type = request.form["unit_type"]
        #unit_count = request.form["unit_count"]
        #unit_starting_location = request.form["starting_location"]
        #unit_destination = request.form["destination"]

        with open('student_input.txt', 'a') as f:
            f.write(unit_type + '\n')

        return render_template('index.html')

    app.run(host="0.0.0.0")