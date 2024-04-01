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


@app.route('/find_multiple_search_games', methods=['GET','POST'])
def multiple_search():
    derivative_pref = request.form['derivative']
    storage = float(request.form['storage'])  # Assume the storage is already in GB
    budget = float(request.form['budget'])


    if (budget is not None) and (storage is not None):

        base_query = """
        SELECT g.Game_Title, g.Genre, g.Average_Rate_Type, g.Current_Price, g.Discount, sr.Storage
		FROM ONLY Games g
		JOIN System_Requirement sr ON g.Game_id = sr.Game_id
		""" 

        derivative_clause = "WHERE g.Current_Price <= :budget"
        if derivative_pref == "yes":
            derivative_clause = """
			JOIN Derivative_games dg ON g.Game_id = dg.Game_id 
			WHERE g.Current_Price <= :budget
		"""
        elif derivative_pref == "no":
            derivative_clause = """
			LEFT JOIN Derivative_games dg ON g.Game_id = dg.Game_id 
			WHERE dg.Game_id IS NULL 
			AND g.Current_Price <= :budget
			"""

        storage_clause ="""
			AND sr.Storage != 'NULL'
			AND(
				CASE
					WHEN sr.Storage LIKE '%% MB %%' THEN CAST(REPLACE(sr.Storage, ' MB available space', '') AS NUMERIC) / 1024
					WHEN sr.Storage LIKE '%% GB %%' THEN CAST(REPLACE(sr.Storage, ' GB available space', '') AS NUMERIC)
				END
			) <= :storage	
	    """	
	

        cursor = g.conn.execute(text(base_query + derivative_clause + storage_clause), {'budget': budget, 'storage': storage})
        multiple_games = cursor.fetchall()
        cursor.close()
        return render_template("multiple_search_results.html", multiple_games = multiple_games)
    return redirect('/')


@app.route('/')
def index():
    # Other code...
    return render_template("multiple_search.html")


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