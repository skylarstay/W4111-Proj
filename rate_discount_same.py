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

# with engine.connect() as conn:
# 	create_table_command = """
# 	CREATE TABLE IF NOT EXISTS test (
# 		id serial,
# 		name text
# 	)
# 	"""
# 	res = conn.execute(text(create_table_command))
# 	insert_table_command = """INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace')"""
# 	res = conn.execute(text(insert_table_command))
# 	# you need to commit for create, insert, update queries to reflect
# 	conn.commit()



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


@app.route('/find_similar_games', methods=['POST'])
def find_similar_games():
    game_name = request.form['game_name']
    if game_name:
        similar_games_query = """
        SELECT g2.Game_Title
            FROM ONLY Games g1
            JOIN ONLY Games g2 ON g1.Average_Rate_Type = g2.Average_Rate_Type AND g1.Discount = g2.Discount AND g1.Game_Title <> g2.Game_Title
            WHERE g1.Game_Title = :game_name;
        """
        cursor = g.conn.execute(text(similar_games_query), {'game_name': game_name})
        similar_games = [row[0] for row in cursor]
        cursor.close()
        return render_template("similar_games.html", similar_games=similar_games)
    return redirect('/')


@app.route('/')
def index():
    # Other code...
    return render_template("game_query.html")


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