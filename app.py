from flask import Flask, render_template,url_for,redirect,request, escape, session,json,flash
from flaskext.mysql import MySQL
from flask.ext.sendmail import Mail
from flask.ext.sendmail import Message
from werkzeug import generate_password_hash, check_password_hash
from form import FormDataBarang

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

@app.route('/dataVendor')
def dataVendor():
	return redirect(url_for('main'))

@app.route('/dataBarang',methods=['POST','GET'])
def dataBarang():
	#cursor.execute("SELECT id,nama,satuan,harga,ket from barang ORDER BY id ASC;")
	row = None
	form=FormDataBarang(request.form)
	#print (form.errors)
	if request.method=='POST':
		_id=request.form['tx_id']
		_nama=request.form['tx_nama']
		_harga=request.form['tx_harga']
		_satuan=request.form['tx_satuan']
		_ket=request.form['tx_ket']
		#print (_nama)
		if form.validate():
			if _id:
				cursor.execute("UPDATE barang SET nama=%s,satuan=%s,harga=%s,ket=%s)WHERE id=%s);",(_nama,_satuan,_harga,_ket,_id))
				flash('Data barang berhasil diubah.')
			else:				
				cursor.execute("INSERT INTO barang(nama,satuan,harga,ket)VALUES(%s,%s,%s,%s);",(_nama,_satuan,_harga,_ket))
				flash('Data barang berhasil ditambahkan.')
			return redirect(url_for('dataBarang')) #agar dokumen refresh setelah submit
		else:
			flash('Silahkan lengkapi terlebih dahulu.')
	else:
		if request.args.get('id'):
			sid=request.args.get('id')
			cursor.execute("SELECT id,nama,satuan,harga,ket FROM barang WHERE id=%s;",(sid))
			row=cursor.fetchone()
			if row:
				print('Data Perubahan Barang: '+str(row[1]))#cetak nama
				form.tx_id.default=row[0]
				form.tx_nama.default=row[1]
				form.tx_satuan.default=row[2]
				form.tx_harga.default=row[3]
				form.tx_ket.default=row[4]
				form.process()
			else:
				print('Data tidak ditemukan.')
	return render_template('data-barang.html',form=form,data=row)

@app.route('/tableDataBarang')
def tableDataBarang():
	cursor.execute("SELECT id,nama,satuan,harga,ket from barang ORDER BY id ASC;")
	data = cursor.fetchall()
	#return redirect(url_for('dataBarang'))
	return render_template('data-barang-tabel.html',data=data)

@app.route('/dataBarangUbah', methods=['POST', 'GET'])
def dataBarangUbah():
	error = None
	if request.method=='GET':
		sid = request.args.get('id')
		cursor.execute("SELECT id,nama,satuan,harga,ket FROM barang WHERE id=%s;",(sid))
		row=cursor.fetchone()
		if row:
			print('Data Perubahan Barang: '+str(row[1]))#cetak nama
		else:
			print('Data tidak ditemukan.')
	return render_template('home.html')




'''
Running aplikasi**********************************************************************************
'''
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


if __name__ == '__main__':
	app.secret_key = "f25a2fc72690b780b2a14e140ef6a9e0"
	app.run(debug = True)