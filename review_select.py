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


@app.route('/find_reviews', methods=['POST'])
def reviews_search():
    GameName = request.form['GameName']
    P_N = request.form['P_N']
    agreed = request.form['agreed']


    if GameName is not None:

        base_query = """
        SELECT g.Game_Title, r.ReviewText, R.Rating, R.Liked
		FROM Reviews_Ratings r
		JOIN ONLY Games g ON r.Game_id = g.Game_id
		WHERE g.Game_Title = :GameName
		""" 

        PN_clause = ""
        if P_N == "Positive":
            PN_clause = """
			AND r.Rating >= 3 AND r.Recommend = 1  
		"""
        elif P_N == "Negative":
            PN_clause = """
			AND r.Rating <= 3 AND r.Recommend = 0
		"""

        
        agreed_clause =""
        if agreed == "yes":
            agreed_clause = """
			AND r.Liked >= 50  
		"""
	

        cursor = g.conn.execute(text(base_query + PN_clause + agreed_clause), {'GameName': GameName})
        multiple_reviews = cursor.fetchall()
        cursor.close()
        return render_template("review_results.html", multiple_reviews = multiple_reviews)
    return redirect('/')


@app.route('/')
def index():
    # Other code...
    return render_template("review_search.html")


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