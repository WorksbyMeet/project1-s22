#project1part 3 implement
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'part3templates')
app = Flask(__name__, template_folder=tmpl_dir)


DB_USER = "cam2404"
DB_PASSWORD = "7307"

DB_SERVER = "w4111project1part2db.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/proj1part2"

engine = create_engine(DATABASEURI)

engine.execute('DROP TABLE IF EXISTS test;')
engine.execute('''CREATE TABLE IF NOT EXISTS test (id serial,name text);''')

engine.execute('DROP TABLE IF EXISTS carry;')
engine.execute('''CREATE TABLE IF NOT EXISTS carry (id serial,sites text);''')



user = ''

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

    def check(a,b,x,y):
      for i in range(len(y)):
        if a == x[i] and b==y[i]:
          return True
        else: False

    if request.method == 'POST':
        userthis = request.form['username']
        engine.execute("INSERT INTO test(name) VALUES (%s)",userthis)
        if check(userthis,request.form['password'],userids,passwords):
          return redirect('/another')
        else:
          error = 'Invalid Credentials. Please try again.' 

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

  return render_template("index.html", **context,)





@app.route('/another',methods=['GET', 'POST'])
def another():

  category = request.args.get('type')

  cursor = g.conn.execute("SELECT name FROM test")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()


  balanceuser = g.conn.execute('SELECT balance FROM users WHERE userid = (%s)',names[-1])
  balance = []
  for i in balanceuser:
    balance.append(i[0])  # can also be accessed using result[0]
  balanceuser.close()

  sitesall = g.conn.execute("SELECT name FROM business")
  sites = []
  for result in sitesall:
    sites.append(result['name'])  # can also be accessed using result[0]
  sitesall.close()

  descriptions = g.conn.execute("SELECT description FROM business")
  description = []
  for result in descriptions:
    description.append(result['description'])  # can also be accessed using result[0]
  descriptions.close()
  

  context = dict(data = balance[0])

  zipped=zip(sites,description)

  engine.execute("INSERT INTO carry(sites) VALUES (%s)",category)


  return render_template("anotherfile.html",**context,both=zipped)










@app.route('/site',methods=['GET', 'POST'])
def site():

  cursor = g.conn.execute("SELECT sites FROM carry")
  names = []
  for result in cursor:
    names.append(result[0])  # can also be accessed using result[0]
  cursor.close()

  category = request.args.get('type')

  description_unique = g.conn.execute('SELECT description FROM business WHERE name = (%s)',category)
  description_u = []
  for i in description_unique:
    description_u.append(i[0])  # can also be accessed using result[0]
  description_unique.close()

  description_unique = g.conn.execute('SELECT description FROM business WHERE name = (%s)',category)
  description_u = []
  for i in description_unique:
    description_u.append(i[0])  # can also be accessed using result[0]
  description_unique.close()

  street_unique = g.conn.execute('SELECT number,street,city,state,zip from (SELECT * FROM address INNER JOIN has ON has.aid=address.aid) as t Where name = (%s)',category)
  street_u = []
  for i in street_unique:
    street_u.append(i)  # can also be accessed using result[0]
  street_unique.close()

  discount_unique = g.conn.execute('SELECT type from (SELECT * FROM offer INNER JOIN discount ON offer.did=discount.did) as t WHERE name =  (%s)',category)
  discount_u = []
  for i in discount_unique:
    discount_u.append(i[0])  # can also be accessed using result[0]
  discount_unique.close()

  sells_unique = g.conn.execute('SELECT t2.name FROM business t1 JOIN sells t2 ON (t1.bid=t2.bid) WHERE t1.name = (%s)',category)
  sell_u = []
  for i in sells_unique:
    sell_u.append(i[0])  # can also be accessed using result[0]
  sells_unique.close()

  sellsdescription_unique = g.conn.execute('SELECT t2.description FROM business t1 JOIN sells t2 ON (t1.bid=t2.bid) WHERE t1.name = (%s)',category)
  sellsdescription_u = []
  for i in sellsdescription_unique:
    sellsdescription_u.append(i[0])  # can also be accessed using result[0]
  sellsdescription_unique.close()

  cost_unique = g.conn.execute('SELECT t2.cost FROM business t1 JOIN sells t2 ON (t1.bid=t2.bid) WHERE t1.name = (%s)',category)
  cost_u = []
  for i in cost_unique:
    cost_u.append(i[0])  # can also be accessed using result[0]
  cost_unique.close()

  type_unique = g.conn.execute('SELECT t1.type FROM Discount t1 JOIN offer t2 ON (t1.did=t2.did) where t2.name = (%s)',category)
  type_u = []
  for i in type_unique:
    type_u.append(i[0])  # can also be accessed using result[0]
  type_unique.close()



  context = dict(data = category)


  return render_template("site.html",**context,des=description_u[0],street=street_u[0],discount=discount_u[0],sell=sell_u[0],sellsdescription=sellsdescription_u[0],cost=cost_u[0],type=type_u[0])















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
