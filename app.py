import os
from flask import Flask, render_template,url_for,redirect,request, escape, session,json,flash
from flaskext.mysql import MySQL
from flask_sendmail import Mail, Message
from werkzeug import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug import secure_filename
from form import FormDataBarang, FormDataVendor,FormDataBidang

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

UPLOAD_FOLDER=app.root_path+'/assets/foto/'

app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['jpg'])

# blok fungsi=============================================================================================

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

def insertDataBarang(nama,satuan,harga,ket,nama_foto):
	if nama_foto == 'no-image.png':
		cursor.execute("INSERT INTO barang(nama,satuan,harga,ket)VALUES(%s,UCASE(%s),%s,%s);",(nama,satuan,harga,ket))
	else:
		cursor.execute("INSERT INTO barang(nama,satuan,harga,ket,nama_foto)VALUES(%s,UCASE(%s),%s,%s,%s);",(nama,satuan,harga,ket,nama_foto))
	return flash('Data barang berhasil ditambahkan.')

def updateDataBarang(nama,satuan,harga,ket,sid,nama_foto):
	if nama_foto == 'no-image.png':
		cursor.execute("UPDATE barang SET nama=%s,satuan=UCASE(%s),harga=%s,ket=%s WHERE id=%s;",(nama,satuan,harga,ket,sid))
	else:
		cursor.execute("UPDATE barang SET nama=%s,satuan=UCASE(%s),harga=%s,ket=%s,nama_foto=%s WHERE id=%s;",(nama,satuan,harga,ket,nama_foto,sid))
	return  flash('Data barang berhasil diubah.')

# blok fungsi=============================================================================================

#print('ROOT PATH: '+app.root_path)

username=None

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
		return redirect(url_for('main'))
#	else:
#		user=request.arg.get('username')
#		session['username']=user
#		return redirect(url_for('main',username=user))

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

# blok modul==========================================================================
@app.route('/dataVendor',methods=['GET','POST'])
def dataVendor():
	form=FormDataVendor(request.form)
	cursor.execute("SELECT id,nama,alamat,telp,email,pemilik FROM vendor WHERE 1;")
	data1=cursor.fetchall()
	if request.method=='POST':
		cid=request.form['tx_id']
		cnama=request.form['tx_nama']
		calamat=request.form['tx_alamat']
		ctelp=request.form['tx_telp']
		cemail=request.form['tx_email']
		cmilik=request.form['tx_pemilik']
		if form.validate_on_submit():
			if cid:
				cursor.execute("UPDATE vendor SET nama=UCASE(%s),alamat=%s,telp=%s,email=%s,pemilik=UCASE(%s) WHERE id=%s;",(cnama,calamat,ctelp,cemail,cmilik,cid))
				flash('Data vendor berhasil diubah.')
				return redirect(url_for('dataVendor')) #agar dokumen refresh setelah submit
			else:
				cursor.execute("INSERT INTO vendor(nama,alamat,telp,email,pemilik)VALUES(UCASE(%s),%s,%s,%s,UCASE(%s));",(cnama,calamat,ctelp,cemail,cmilik))
				flash('Data vendor berhasil ditambahkan.')
				return redirect(url_for('dataVendor')) #agar dokumen refresh setelah submit
	else:
		if request.args.get('id'):			
			sid=request.args.get('id')
			cursor.execute("SELECT id,nama,alamat,telp,email,pemilik FROM vendor WHERE id=%s;",(sid))
			row=cursor.fetchone()
			if row:
				print('Data Perubahan Vendor: '+str(row[1]))#cetak nama
				form.tx_id.default=row[0]
				form.tx_nama.default=row[1]
				form.tx_alamat.default=row[2]
				form.tx_telp.default=row[3]
				form.tx_email.default=row[4]
				form.tx_pemilik.default=row[5]
				form.process()
			else:
				print('Data tidak ditemukan.')
				flash('Data tidak ditemukan.')
	return render_template('data-vendor.html',form=form,data1=data1)

@app.route('/hapusVendor',methods=['GET','POST'])
def hapusVendor():
	if request.method=='GET':
		sid=request.args.get('id')
		cursor.execute("SELECT id,nama,alamat,telp,email,pemilik FROM vendor WHERE id=%s;",(sid))
		data=cursor.fetchall()
		#return about()
		return render_template('hapus-vendor.html',data=data)
	else:
		sid=request.form['sid']
		cursor.execute("DELETE FROM vendor WHERE id=%s;",(sid))
		return redirect(url_for('dataVendor')) #agar dokumen refresh setelah submit

# blok modul==========================================================================

@app.route('/hapusBarang',methods=['GET','POST'])
def hapusBarang():
	if request.method=='GET':
		sid=request.args.get('id')
		cursor.execute("SELECT id,nama,satuan,harga,ket FROM barang WHERE id=%s;",(sid))
		data=cursor.fetchall()
		#return about()
		return render_template('hapus-barang.html',data=data)
	else:
		sid=request.form['sid']
		cursor.execute("DELETE FROM barang WHERE id=%s;",(sid))
		return tableDataBarang()

@app.route('/dataBarang',methods=['POST','GET'])
def dataBarang():
	row = None
	filename = 'no-image.png'
	form=FormDataBarang(request.form)
	#print (form.errors)
	if request.method=='POST':		
		_id=request.form['tx_id']
		_nama=request.form['tx_nama']
		_harga=request.form['tx_harga']
		_satuan=request.form['tx_satuan']
		_ket=request.form['tx_ket']
		#print('xxxxxxxxxxxxxxxxxxxxx'+_ket)
		#foto=request.files['file_foto']
		if form.validate_on_submit():
			#if request.files['file_foto'].filename!='':# and allowed_file(request.files['file_foto'].filename):
			if 'file_foto' in request.files:
				#print('ada foto')
				foto=request.files['file_foto']
				if allowed_file(foto.filename):
					filename = secure_filename(foto.filename)
					foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			if _id:
				updateDataBarang(_nama,_satuan,_harga,_ket,_id,filename)#tambah fungsi seleksi di def query, jika filename not 'no-image.png'
			else:
				insertDataBarang(_nama,_satuan,_harga,_ket,filename)			
			return redirect(url_for('dataBarang')) #agar dokumen refresh setelah submit
		#else:
		#	flash('Silahkan lengkapi terlebih dahulu.')
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
				flash('Data tidak ditemukan.')
	return render_template('data-barang.html',form=form,data=row)

@app.route('/tableDataBarang')
def tableDataBarang():
	cursor.execute("SELECT id,nama,satuan,ROUND(harga,0),ket from barang ORDER BY id ASC;")
	data = cursor.fetchall()
	#return redirect(url_for('dataBarang'))
	return render_template('data-barang-tabel.html',data=data)

# blok modul==========================================================================

@app.route('/dataBidang',methods=['GET','POST'])
def dataBidang():
	form=FormDataBidang(request.form)
	cursor.execute("SELECT id,nama,ket from divisi ORDER BY nama ASC;")
	data = cursor.fetchall()
	return render_template('data-bidang.html',data=data,form=form)



# blok modul==========================================================================

'''
Running aplikasi**********************************************************************************
'''
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


if __name__ == '__main__':
	app.secret_key = "f25a2fc72690b780b2a14e140ef6a9e0"
	app.run(debug = True)
