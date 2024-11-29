from flask import Flask, render_template, request

#===================================================================================================
# Flask server for student interaction of PyGame Project
#
# Roupen Kaloustian
# November 9th, 2024
#===================================================================================================
# To-do List
#   - Add js script that checks the student_input.txt file's 2 first rows to check if certain form options are legal to press
#   - add an error message window for any important messages that need to get sent to players
#
#===================================================================================================
def activate_server():
    print("Starting Game Server...")

    app = Flask(__name__)


    @app.route('/', methods=["GET"])
    def hello():
        return render_template('index.html')

    @app.route('/', methods=["POST"])
    def user_input():
        
        unit_type = request.form["unit_type"]
        unit_count = request.form["unit_count"]
        unit_starting_locations = request.form["unit_spawn"]
        unit_destination = request.form["unit_destination"]
        
        

        with open('student_input.txt', 'a') as f:
            f.write(unit_type + " " + unit_starting_locations + " " + unit_destination + " " + unit_count + " " + request.environ['REMOTE_ADDR'] + '\n')

            
        

        return render_template('index.html')

    app.run(host="0.0.0.0")