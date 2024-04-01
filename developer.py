import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

#tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
tmpl_dir = "./templates"
app = Flask(__name__, template_folder=tmpl_dir)

DATABASE_USERNAME = "yc4387"
DATABASE_PASSWRD = "221558"
DATABASE_HOST ="35.212.75.104"
#DATABASE_HOST = "34.148.107.47" 
#DATABASE_HOST = "34.28.53.86"# change to 34.28.53.86 if you used database 2 for part 2
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)




@app.before_request
def before_request():
	"""
	This function is run at the beginning of every web request 
	(every time you enter an address in the web browser).
	We use it to setup a database connection that can be used throughout the request.

	The variable g is globally accessible.
	"""
	try:
		g.conn = engine.connect()
	except:
		print("uh oh, problem connecting to database")
		import traceback; traceback.print_exc()
		g.conn = None


@app.teardown_request
def teardown_request(exception):
	"""
	At the end of the web request, this makes sure to close the database connection.
	If you don't, the database could run out of memory!
	"""
	try:
		g.conn.close()
	except Exception as e:
		pass


@app.route('/find_developer_games', methods=['POST'])
def find_developer_games():
    developer_name = request.form['developer_name']
    positive_rate = float(request.form['positive_rate_requirement'])*0.01
    
    if developer_name:
        if positive_rate:  # if user provides positive_rate, construct a query with the condition
            developer_games_query = """
            SELECT g.Game_Title, g.Genre, g.Original_Price, g.Current_Price, g.Positive_ratings_percentage, d.Developer_name, d.Website
                FROM ONLY Games g
                JOIN Games_Developers gd ON g.Game_id = gd.Game_id
                JOIN Developers d ON gd.Developer_id = d.Developer_id
                WHERE g.Positive_ratings_percentage >= :positive_rate
                AND d.Developer_name = :developer_name;
            """
            cursor = g.conn.execute(text(developer_games_query), {'developer_name': developer_name, 'positive_rate': positive_rate})
        else:  # if user does not provide any requirements of positive_rate, construct a query without the condition
            developer_games_query = """
            SELECT g.Game_Title, g.Genre, g.Original_Price, g.Current_Price, g.Positive_ratings_percentage, d.Developer_name, d.Website
                FROM ONLY Games g
                JOIN Games_Developers gd ON g.Game_id = gd.Game_id
                JOIN Developers d ON gd.Developer_id = d.Developer_id
                WHERE d.Developer_name = :developer_name;
            """
            cursor = g.conn.execute(text(developer_games_query), {'developer_name': developer_name})
			
        developer_games = cursor.fetchall()
        cursor.close()
        return render_template("developer_games.html", developer_games=developer_games)
    return redirect('/')


@app.route('/')
def index():
    # Other code...
    return render_template("developer_type_query.html")


if __name__ == "__main__":
	import click

	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8111, type=int)
	def run(debug, threaded, host, port):
		"""
		This function handles command line parameters.
		Run the server using:

			python server.py

		Show the help text using:

			python server.py --help

		"""

		HOST, PORT = host, port
		print("running on %s:%d" % (HOST, PORT))
		app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

run()