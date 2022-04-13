#project1part 3 implement
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'part3templates')
app = Flask(__name__, template_folder=tmpl_dir)


DB_USER = "cam2404"
DB_PASSWORD = "7307"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/proj1part2"

engine = create_engine(DATABASEURI)

engine.execute('DROP TABLE IF EXISTS test;')
engine.execute('''CREATE TABLE IF NOT EXISTS test (id serial,name text);''')
engine.execute('''INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');''')


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
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
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    usernames = g.conn.execute("SELECT userid FROM users")
    userids =[]
    for i in usernames:
      userids.append(i['userid'])
    usernames.close()

    passwordssearch = g.conn.execute("SELECT password FROM users")
    passwords =[]
    for i in passwordssearch:
      passwords.append(i['password'])
    passwordssearch.close()

    def check(x,y):
      for i in range(len(y)):
        if x == y[i]:
          return True
        else: False

    if request.method == 'POST':
        if check(request.form['username'],userids) or check(request.form['password'],passwords) :
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect('/')


    context = dict(data = [userids[0],passwords[0]])

    return render_template('login.html', error=error,**context)


@app.route('/')
def index():

  print (request.args)

  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT name FROM business")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

 
  context = dict(data = names)

  return render_template("index.html", **context)


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
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
