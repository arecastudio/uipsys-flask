from flask import Flask, render_template,url_for,redirect,request, escape, session,json,flash
from flaskext.mysql import MySQL
from flask.ext.sendmail import Mail
from flask.ext.sendmail import Message
from werkzeug import generate_password_hash, check_password_hash

app = Flask(__name__)

mail = Mail(app)

mysql = MySQL() 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'rail'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'db_uipsys'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

@app.route('/')
def main():
	if 'username' in session:
		username=session['username']
		return render_template('home.html')
	return redirect(url_for('login'))

@app.route('/loginsubmit',methods=['POST','GET'])
def loginsubmit():
	if request.method=='POST':
		user=request.form['username']
		session['username']=user
		return redirect(url_for('main',username=user))
	else:
		user=request.arg.get('username')
		session['username']=user
		return redirect(url_for('main',username=user))

@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/logout')
def logout():
	session.pop('username',None)
	return redirect(url_for('main'))

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/dataBarang')
def dataBarang():
	cursor.execute("SELECT id,nama,satuan,harga,ket from barang ORDER BY id ASC;")
	data = cursor.fetchall()
	return render_template('data-barang.html',data=data)

@app.route('/insertDataBarang',methods=['POST'])
def insertDataBarang():
	try:		
		#baca kiriman data dari form
		_nama=request.form['tx_nama']
		_harga=request.form['tx_harga']
		_satuan=request.form['tx_satuan']
		_ket=request.form['tx_ket']
		cursor.execute("INSERT INTO barang(nama,satuan,harga,ket)VALUES(%s,%s,%s,%s);",(_nama,_satuan,_harga,_ket))		
	finally:
		flash('You were successfully logged in')
	return redirect(url_for('dataBarang'))


if __name__ == '__main__':
	app.secret_key = "f25a2fc72690b780b2a14e140ef6a9e0"
	app.run(debug = True)
