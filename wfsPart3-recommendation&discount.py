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



@app.route('/find_recommend_games', methods=['POST'])
def find_recommend_games():
    user_id = request.form['user_id']
    formatted_user_id = f'"{user_id}"'
    if user_id:
        similar_tags_query = """
        SELECT DISTINCT g.Game_Title
        FROM Games g
        JOIN Tags t ON g.Game_id = t.Game_id
        WHERE t.Tag IN (
            SELECT DISTINCT t1.Tag
            FROM Tags t1
            JOIN Library_Stored ls ON t1.Game_id = ls.Game_id
            WHERE ls.User_id = :user_id
        ) AND g.Game_id NOT IN (
            SELECT Game_id
            FROM Library_Stored
            WHERE User_id = :user_id
        )
        """

        same_publisher_query = """
        SELECT g.Game_Title
        FROM ONLY Games g
        WHERE g.Game_id IN (
            SELECT gp.Game_id
            FROM Games_Publishers gp
            JOIN Games_Publishers gp_user ON gp.Publisher_id = gp_user.Publisher_id
            WHERE gp_user.Game_id IN (
                SELECT Game_id
                FROM Library_Stored
                WHERE User_id = :user_id
            ) AND g.Game_id NOT IN (
                SELECT Game_id
                FROM Library_Stored
                WHERE User_id = :user_id
			)
        )
        """

        same_developer_query = """
        SELECT g.Game_Title
        FROM ONLY Games g
        WHERE g.Game_id IN (
            SELECT gd.Game_id
            FROM Games_Developers gd
            JOIN Games_Developers gd_user ON gd.Developer_id = gd_user.Developer_id
            WHERE gd_user.Game_id IN (
                SELECT Game_id
                FROM Library_Stored
                WHERE User_id = :user_id
            ) AND g.Game_id NOT IN (
                SELECT Game_id
                FROM Library_Stored
                WHERE User_id = :user_id
			)
        )
        """

        friends_games_query = """
        SELECT g.Game_Title
        FROM ONLY Games g
        WHERE g.Game_id IN (
            SELECT Game_id
            FROM Library_Stored
            WHERE User_id IN (
                SELECT friUser_id
                FROM Friended_Users
                WHERE User_id = :user_id
            ) AND g.Game_id NOT IN (
                SELECT Game_id
                FROM Library_Stored
                WHERE User_id = :user_id
			)
        )
        """
        wishlist_games_query = """
        SELECT DISTINCT g.Game_Title
        FROM ONLY Games g
        WHERE g.Game_id IN (
            SELECT Game_id
            FROM WishList_Cart
            WHERE User_id = :user_id
        )
        """
        mostLikely_like_games_query = """
        WITH All_Games AS (
            SELECT DISTINCT g.Game_Title, g.Original_Price
            FROM ONLY Games g
            JOIN Tags t ON g.Game_id = t.Game_id
            WHERE t.Tag IN (
                SELECT DISTINCT t1.Tag
                FROM Tags t1
                JOIN Library_Stored ls ON t1.Game_id = ls.Game_id
                WHERE ls.User_id = :user_id
            ) AND g.Game_id NOT IN (
                SELECT Game_id
                FROM Library_Stored
                WHERE User_id = :user_id
            )
            UNION ALL
            SELECT g.Game_Title, g.Original_Price
            FROM ONLY Games g
            WHERE g.Game_id IN (
                SELECT gp.Game_id
                FROM Games_Publishers gp
                JOIN Games_Publishers gp_user ON gp.Publisher_id = gp_user.Publisher_id
                WHERE gp_user.Game_id IN (
                    SELECT Game_id
                    FROM Library_Stored
                 WHERE User_id = :user_id
                ) AND g.Game_id NOT IN (
                    SELECT Game_id
                    FROM Library_Stored
                    WHERE User_id = :user_id
				)
            )
            UNION ALL
            SELECT g.Game_Title, g.Original_Price
            FROM ONLY Games g
            WHERE g.Game_id IN (
                SELECT gd.Game_id
                FROM Games_Developers gd
                JOIN Games_Developers gd_user ON gd.Developer_id = gd_user.Developer_id
                WHERE gd_user.Game_id IN (
                    SELECT Game_id
                    FROM Library_Stored
                    WHERE User_id = :user_id
                ) AND g.Game_id NOT IN (
                    SELECT Game_id
                    FROM Library_Stored
                    WHERE User_id = :user_id
				)
            )
            UNION ALL
            SELECT g.Game_Title, g.Original_Price
            FROM ONLY Games g
            WHERE g.Game_id IN (
                SELECT Game_id
                FROM Library_Stored
                WHERE User_id IN (
                    SELECT friUser_id
                    FROM Friended_Users
                    WHERE User_id = :user_id
                ) AND g.Game_id NOT IN (
                    SELECT Game_id
                    FROM Library_Stored
                    WHERE User_id = :user_id
				)
            )
            UNION ALL
            SELECT g.Game_Title, g.Original_Price
            FROM ONLY Games g
            WHERE g.Game_id IN (
                SELECT Game_id
                FROM WishList_Cart
                WHERE User_id = :user_id
            )
        ),
        Filtered_Games AS (
            SELECT Game_Title, Original_Price
            FROM All_Games
            
        ),
        Frequency_Counts AS (
            SELECT Game_Title, COUNT(*) AS Frequency, Original_Price
            FROM Filtered_Games
            GROUP BY Game_Title, Original_Price
        ),
        Max_Frequency AS (
            SELECT MAX(Frequency) AS MaxFreq
            FROM Frequency_Counts
        )
        SELECT f.Game_Title, f.Original_Price, 
               ROUND(f.Original_Price * 0.7, 2) AS Discounted_Price, 
               ROUND(f.Original_Price * 0.3, 2) AS Discount_Amount
        FROM Frequency_Counts f, Max_Frequency mf
        WHERE f.Frequency = mf.MaxFreq
        ORDER BY f.Game_Title
        
        """        
		#SELECT Game_Title, COUNT(*) AS Frequency
        #FROM All_Games
        #WHERE Game_Title NOT ILIKE '%Not Included%'
        #GROUP BY Game_Title
        #HAVING Frequency = MAX(Frequency)
		
        #ORDER BY Frequency DESC
        similar_tags_cursor = g.conn.execute(text(similar_tags_query), {'user_id': formatted_user_id})
        similar_tags_games = [row[0] for row in similar_tags_cursor]
        similar_tags_cursor.close()

        same_publisher_cursor = g.conn.execute(text(same_publisher_query), {'user_id': formatted_user_id})
        same_publisher_games = [row[0] for row in same_publisher_cursor]
        same_publisher_cursor.close()

        same_developer_cursor = g.conn.execute(text(same_developer_query), {'user_id': formatted_user_id})
        same_developer_games = [row[0] for row in same_developer_cursor]
        same_developer_cursor.close()

        friends_games_cursor = g.conn.execute(text(friends_games_query), {'user_id': formatted_user_id})
        friends_games = [row[0] for row in friends_games_cursor]
        friends_games_cursor.close()

        wishlist_cursor = g.conn.execute(text(wishlist_games_query), {'user_id': formatted_user_id})
        wishlist_games = [row[0] for row in wishlist_cursor]
        wishlist_cursor.close()
		
        mostLikely_like_cursor = g.conn.execute(text(mostLikely_like_games_query), {'user_id': formatted_user_id})
        mostLikely_like_games = [{
            'title': row[0],  
            'original_price': row[1], 
            'discounted_price': row[2],
            'discount_amount': row[3]
        } for row in mostLikely_like_cursor]
        mostLikely_like_cursor.close()


        return render_template("recommend_games.html", 
                               similar_tags_games=similar_tags_games, 
                               same_publisher_games=same_publisher_games, 
                               same_developer_games=same_developer_games, 
                               friends_games=friends_games,
							   wishlist_games=wishlist_games,
							   mostLikely_like_games=mostLikely_like_games)
    return redirect('/')



@app.route('/')
def index():
    # Other code...
    return render_template("useridLogin.html")


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