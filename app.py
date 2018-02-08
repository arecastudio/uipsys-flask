import os
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template,url_for,redirect,request, escape, session,json,jsonify,flash
from flaskext.mysql import MySQL
from flask_sendmail import Mail, Message
from werkzeug import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug import secure_filename
from functools import wraps
from form import FormLogin,FormDataBarang,FormDataVendor,FormDataBidang,FormManUser,FormOrder



app = Flask(__name__)

mail = Mail(app)

mysql = MySQL()
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'pdamjpr.123'
app.config['MYSQL_DATABASE_DB'] = 'db_uipsys'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

UPLOAD_FOLDER=app.root_path+'/static/foto/'

app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['jpg'])

# blok fungsi=============================================================================================
def formatBulan(args):
	#args harus string
	hasil=args
	if len(args)<2:
		hasil='0'+str(args)
	#print(hasil)
	return hasil

def getPeriode():
	periode=[]
	now=date.today()
	prd1 = date.today()
	prd2 = date.today() + relativedelta(months=+1)
	prd3 = date.today() + relativedelta(months=+2)
	prd0 = date.today() + relativedelta(months=-1)
	periode.append(str(prd0.year)+str(formatBulan(str(prd0.month))))
	periode.append(str(prd1.year)+str(formatBulan(str(prd1.month))))
	periode.append(str(prd2.year)+str(formatBulan(str(prd2.month))))
	periode.append(str(prd3.year)+str(formatBulan(str(prd3.month))))
	print('Tanggal: '+str(periode[0]))
	#formatBulan('3')
	return periode

# blok fungsi=============================================================================================

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

def insertDataBarang(nama,satuan,harga,ket,nama_foto):
	if nama_foto == 'no-image.png':
		cursor.execute("INSERT INTO barang(nama,satuan,harga,ket)VALUES(%s,UCASE(%s),%s,%s);",(nama,satuan,harga,ket))
	else:
		cursor.execute("INSERT INTO barang(nama,satuan,harga,ket,nama_foto)VALUES(%s,UCASE(%s),%s,%s,%s);",(nama,satuan,harga,ket,nama_foto))
	return 'Data barang berhasil ditambahkan.'

def updateDataBarang(nama,satuan,harga,ket,sid,nama_foto):
	if nama_foto == 'no-image.png':
		cursor.execute("UPDATE barang SET nama=%s,satuan=UCASE(%s),harga=%s,ket=%s WHERE id=%s;",(nama,satuan,harga,ket,sid))
	else:
		cursor.execute("UPDATE barang SET nama=%s,satuan=UCASE(%s),harga=%s,ket=%s,nama_foto=%s WHERE id=%s;",(nama,satuan,harga,ket,nama_foto,sid))
	return  'Data barang berhasil diubah.'

class ClassOrder(object):
	"""docstring for ClassOrder"""
	def __init__(self, _id,_nama,_satuan):
		super(ClassOrder, self).__init__()
		self._id = _id
		self._nama = _nama
		self._satuan = _satuan
		

# blok fungsi=============================================================================================

#print('ROOT PATH: '+app.root_path)

username=None
fullname=None
#barang_dipilih=[]

def login_required(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if 'username' in session:
			return f(*args,**kwargs)
		else:
			flash('Anda harus login terlebih dahulu.')
			return redirect(url_for('login'))
	return wrap


@app.route('/')
@login_required
def main():
	#print(str(getPeriodes()))
	getPeriode()
	return render_template('home.html')

@app.route('/login',methods=['POST','GET'])
def login():
	form=FormLogin(request.form)
	if request.method=='POST':
		uname=request.form['tx_user']
		upass=request.form['tx_pass']
		if form.validate_on_submit():
			cursor.execute("SELECT u.uname,u.nik,u.nama,u.id_divisi,d.nama,u.id_role,r.nama,u.jabatan,u.telp,u.email FROM user AS u LEFT OUTER JOIN divisi AS d ON d.id=u.id_divisi LEFT OUTER JOIN role AS r ON r.id=u.id_role WHERE u.uname=%s AND password=MD5(%s) LIMIT 1;",(uname,upass))
			row=cursor.fetchone()
			if row:
				session['username']=row[0]
				session['nik']=row[1]
				session['fullname']=row[2]
				session['id_divisi']=row[3]
				session['nama_divisi']=row[4]
				session['id_role']=row[5]
				session['nama_role']=row[6]
				session['jabatan']=row[7]
				session['barang_dipilih']=''
				flash('Berhasil login.')
				return redirect(url_for('main'))
			else:
				print('Login gagal.')
				flash('Login gagal.')
				return redirect(url_for('login'))
		else:
			flash('Lengkapi informasi login anda.')
	return render_template('login.html',form=form)

@app.route('/logout')
@login_required
def logout():
	session.pop('username',None)
	session.pop('nik',None)
	session.pop('fullname',None)
	session.pop('id_divisi',None)
	session.pop('nama_divisi',None)
	session.pop('id_role',None)
	session.pop('nama_role',None)
	session.pop('jabatan',None)
	#session.pop('pilih_item',None)
	session.pop('barang_dipilih',None)
	#barang_dipilih=[]
	return redirect(url_for('main'))

@app.route('/about')
@login_required
def about():
	return render_template('about.html')

# blok modul==========================================================================
@app.route('/getVendorById',methods=['POST','GET'])
def getVendorById():
	if request.method=='POST':
		cid=request.get_json().get('id')
		cursor.execute("SELECT id,nama,alamat,telp,email,pemilik FROM vendor WHERE id=%s LIMIT 1;",(cid))
		row=cursor.fetchone();
		return jsonify(row)
	return ('', 204)
# blok modul==========================================================================

@app.route('/tableDataVendor',methods=['GET'])
@login_required
def tableDataVendor():
	cursor.execute("SELECT id,nama,alamat,telp,email,pemilik FROM vendor WHERE 1 ORDER BY nama ASC;")
	data = cursor.fetchall()
	if data:
		return render_template('data-vendor-tabel.html',data=data)
# blok modul==========================================================================
@app.route('/getVendor',methods=['POST','GET'])
def getVendor():
	if request.method=='POST':
		cursor.execute("SELECT id,nama,alamat,telp,email,pemilik FROM vendor WHERE 1;")
		row=cursor.fetchall()
		if row:
			print('getVendor berhasil.')
			return jsonify({'sukses':row})
		else:
			print('getVendor berhasil.')
			return jsonify({'gagal':'Gagal mengambil data Vendor.'})
		#print('getVendor berhasil.')
		#return jsonify(row)
	return ('', 204)
# blok modul==========================================================================
@app.route('/dataVendor',methods=['GET','POST'])
@login_required
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
				return jsonify({'success':'Data vendor berhasil diubah.'})
				#return redirect(url_for('dataVendor')) #agar dokumen refresh setelah submit
			else:
				cursor.execute("INSERT INTO vendor(nama,alamat,telp,email,pemilik)VALUES(UCASE(%s),%s,%s,%s,UCASE(%s));",(cnama,calamat,ctelp,cemail,cmilik))
				return jsonify({'success':'Data vendor berhasil ditambahkan.'})
				#return redirect(url_for('dataVendor')) #agar dokumen refresh setelah submit
		else:
			return jsonify({'error':'Lengkapi form terlebih dahulu.'})
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
		flash('Data berhasil dihapus.')
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
		flash('Data berhasil dihapus.')
		return tableDataBarang()

@app.route('/dataBarang',methods=['POST','GET'])
@login_required
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
		if form.validate_on_submit():
			#if request.files['file_foto'].filename!='':# and allowed_file(request.files['file_foto'].filename):
			if 'file_foto' in request.files:
				print('ada foto')
				foto=request.files['file_foto']
				if allowed_file(foto.filename):
					filename = secure_filename(foto.filename)
					foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			else:
				print('tidak ada foto.')
			if _id:
				updateDataBarang(_nama,_satuan,_harga,_ket,_id,filename)#tambah fungsi seleksi di def query, jika filename not 'no-image.png'
			else:
				insertDataBarang(_nama,_satuan,_harga,_ket,filename)
			return jsonify({'success':'Data Barang berhasil disimpan.'})#redirect(url_for('dataBarang')) #agar dokumen refresh setelah submit
		else:
			return jsonify({'error':'Lengkapi data terlebih dahulu.'})
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

@app.route('/tableDataBarang',methods=['GET'])
@login_required
def tableDataBarang():
	cursor.execute("SELECT id,nama,satuan,ROUND(harga,0),ket,nama_foto from barang ORDER BY id ASC;")
	data = cursor.fetchall()
	if data:
		return render_template('data-barang-tabel.html',data=data)

# blok modul==========================================================================
@app.route('/tableDataBidang',methods=['GET'])
@login_required
def tableDataBidang():
	cursor.execute("SELECT id,nama,ket from divisi ORDER BY nama ASC;")
	data = cursor.fetchall()
	if data:
		return render_template('data-bidang-tabel.html',data=data)

@app.route('/dataBidang',methods=['GET','POST'])
@login_required
def dataBidang():
	form=FormDataBidang(request.form)
	cursor.execute("SELECT id,nama,ket from divisi ORDER BY nama ASC;")
	data = cursor.fetchall()
	if request.method=='POST':
		cid=request.form['tx_id']
		cnama=request.form['tx_nama']
		cket=request.form['tx_ket']
		if form.validate_on_submit():
			if cid:
				cursor.execute("UPDATE divisi SET nama=UCASE(%s),ket=%s WHERE id=%s;",(cnama,cket,cid))
				return jsonify({'success':'Berhasil ubah data bidang.'})#redirect(url_for('dataBidang')) #agar dokumen refresh setelah submit
			else:
				cursor.execute("INSERT INTO divisi(nama,ket)VALUES(UCASE(%s),%s);",(cnama,cket))
				return jsonify({'success':'Berhasil simpan data bidang.'})#redirect(url_for('dataBidang')) #agar dokumen refresh setelah submit
		else:
			return jsonify({'error':'Gagal simpan data bidang.'})
	else:
		if request.args.get('id'):
			cid=request.args.get('id')
			cursor.execute("SELECT id,nama,ket FROM divisi WHERE id=%s;",(cid))
			row=cursor.fetchone()
			if row:
				print('Data Perubahan Barang: '+str(row[1]))#cetak nama
				form.tx_id.default=row[0]
				form.tx_nama.default=row[1]
				form.tx_ket.default=row[2]
				form.process()
			else:
				print('Data tidak ditemukan.')
				flash('Data tidak ditemukan.')
	return render_template('data-bidang.html',data=data,form=form)


@app.route('/hapusBidang',methods=['GET','POST'])
def hapusBidang():
	if request.method=='GET':
		sid=request.args.get('id')
		cursor.execute("SELECT id,nama,ket FROM divisi WHERE id=%s;",(sid))
		data=cursor.fetchall()
		#return about()
		return render_template('hapus-bidang.html',data=data)
	else:
		sid=request.form['sid']
		cursor.execute("DELETE FROM divisi WHERE id=%s;",(sid))
		flash('Data berhasil dihapus.')
		return redirect(url_for('tableDataBidang'))

# blok modul==========================================================================
@app.route('/hapusUser',methods=['GET','POST'])
def hapusUser():
	if request.method=='GET':
		sid=request.args.get('id')
		cursor.execute("SELECT nik,nama,telp,email,jabatan FROM user WHERE uname=%s;",(sid))
		data=cursor.fetchall()
		#return about()
		return render_template('hapus-user.html',data=data)
	else:
		sid=request.form['sid']
		cursor.execute("DELETE FROM user WHERE uname=%s;",(sid))
		flash('Data berhasil dihapus.')
		return redirect(url_for('manUserTabel'))

@app.route('/manUser',methods=['GET','POST'])
@login_required
def manUser():
	form=FormManUser(request.form)
	cursor.execute("SELECT u.uname,u.nik,u.nama,u.password,u.telp,u.email,d.nama,r.nama,u.jabatan from user AS u LEFT OUTER JOIN divisi AS d ON d.id=u.id_divisi LEFT OUTER JOIN role AS r ON r.id=u.id_role ORDER BY u.nama ASC;")
	data = cursor.fetchall()
	cursor.execute("SELECT id,nama FROM divisi;")
	tdivisi=cursor.fetchall()
	sdivisi=[(int(i[0]), i[1]) for i in tdivisi]
	form.op_divisi.choices=sdivisi
	cursor.execute("SELECT id,nama FROM role;")
	trole=cursor.fetchall()
	srole=[(int(i[0]), i[1]) for i in trole]
	form.op_role.choices=srole
	if request.method=='POST':
		cid=request.form['tx_id']#tetap ada untuk membedakan data baru dan data update
		cuser=request.form['tx_user']
		cnik=request.form['tx_nik']
		cnama=request.form['tx_nama']
		cpass=request.form['tx_pass']
		ctelp=request.form['tx_telp']
		cmail=request.form['tx_mail']
		cdiv=request.form['op_divisi']
		crole=request.form['op_role']
		cjab=request.form['tx_jabatan']
		if form.validate_on_submit():
			if cid:
					if len(cpass):
						cursor.execute("UPDATE user SET nik=%s,nama=%s,password=%s,telp=%s,email=%s,id_divisi=%s,id_role=%s,jabatan=%s WHERE uname=%s;",(cnik,cnama,cpass,ctelp,cmail,cdiv,crole,cjab,cid))
					else:
						cursor.execute("UPDATE user SET nama=%s,nik=%s,telp=%s,email=%s,id_divisi=%s,id_role=%s,jabatan=%s WHERE uname=%s;",(cnama,cnik,ctelp,cmail,cdiv,crole,cjab,cid))
						#flash('Berhasil mengubah informasi user.')
					return jsonify({'success':'Informasi user berhasil diubah.'})#redirect(url_for('manUser'))#refresh
			else:
				cursor.execute("INSERT INTO user(uname,nik,nama,password,telp,email,id_divisi,id_role,jabatan)VALUES(%s,%s,%s,MD5(%s),%s,%s,%s,%s,%s);",(cuser,cnik,cnama,cpass,ctelp,cmail,cdiv,crole,cjab))
				#flash('Berhasil menambahkan user baru.')
				return jsonify({'success':'User baru telah ditambahkan.'})#redirect(url_for('manUser'))#refresh
		else:
			return jsonify({'error':'Lengkapi isian form terlebih dahulu.'})#flash('Data belum lengkap.')
	else:
		if request.args.get('id'):
		#if 'id' in request.args and request.method=='GET':
			sid=request.args.get('id')
			cursor.execute("SELECT uname,nik,nama,password,telp,email,id_divisi,id_role,jabatan FROM user WHERE uname=%s LIMIT 1;",(sid))
			row=cursor.fetchone()
			if row:
				print('Data Perubahan User: '+str(row[2]))#cetak nama
				form.tx_id.default=row[0]
				form.tx_user.default=row[0]
				form.tx_nik.default=row[1]
				form.tx_nama.default=row[2]
				form.tx_pass.default=row[3]
				form.tx_telp.default=row[4]
				form.tx_mail.default=row[5]
				form.op_divisi.default=row[6]
				form.op_role.default=row[7]
				form.tx_jabatan.default=row[8]
				form.process()
				print('Untuk mengubah informasi user, pastikan untuk mengupdate password terbaru.')
			else:
				print('Data tidak ditemukan.')
	return render_template('man-user.html',data=data,form=form)


@app.route('/manUserTabel',methods={'GET','POST'})
def manUserTabel():
    if request.method=='GET':
        cursor.execute("SELECT u.uname,u.nik,u.nama,u.password,u.telp,u.email,d.nama,r.nama,u.jabatan from user AS u LEFT OUTER JOIN divisi AS d ON d.id=u.id_divisi LEFT OUTER JOIN role AS r ON r.id=u.id_role ORDER BY u.nama ASC;")
        row=cursor.fetchall()
        return render_template('man-user-tabel.html',data=row)


# blok modul==========================================================================
class orderan():
	def __init__(self,id):
		self.id=id


#@staticmethod
def buatOrderan(id):
	mengorder=[]#deklarasi list object
	ord=orderan(id)
	mengorder.append(ord)



@app.route('/assets/foto/<filename>')
def getFotoURL(filename):
	pass


# blok modul==========================================================================
@app.route('/buatPermintaan',methods=['POST','GET'])
@login_required
def buatPermintaan():
	cursor.execute('SELECT id,nama,UCASE(satuan),harga,nama_foto FROM barang ORDER BY nama ASC;')
	row=cursor.fetchall()
	return render_template('buat-permintaan.html',data=row)


# blok modul==========================================================================
def getBarangCount():
	cursor.execute('SELECT COUNT(id) FROM barang;')
	row=cursor.fetchone()
	if row:
		return row[0]
	else:
		return 0
# blok modul==========================================================================
@app.route('/postSession',methods=['POST','GET'])
def postSession():
	#global barang_dipilih
	isMatch=0
	barang_dipilih=''
	if session['barang_dipilih']:
		val=session['barang_dipilih']
		barang_dipilih=val
	print('postSession start: '+str(barang_dipilih))
	if request.method=='POST':
		pil=request.get_json().get('id')
		nama=request.get_json().get('nama')
		satuan=request.get_json().get('satuan')
		print('Item dipilih: '+pil)
		#barang_dipilih.append(pil)
		if len(barang_dipilih):
			str_barang_dipilih=barang_dipilih.split(',')#split hanya berlaku untuk tipe data string
			for brg in str_barang_dipilih:
				if brg==pil:
					isMatch=1
					print(str(pil)+' sudah ada')
		if isMatch==0:
			#dt={pil:{'id':pil,'nama':nama,'satuan':satuan}}
			if barang_dipilih!='':
				barang_dipilih+=','+pil
			#barang_dipilih.append({'id':int(pil)})
			else:
				barang_dipilih=pil
		session['barang_dipilih']=barang_dipilih
		print('postSession end:'+str(session['barang_dipilih']))
		return jsonify(barang_dipilih)
	return ('', 204)
# blok modul==========================================================================
@app.route('/klirSession',methods=['POST','GET'])
def klirSession():
	#session.pop('pilih_item',None)
	#global barang_dipilih
	session['barang_dipilih']=''
	return 'SERVER_LOG: Berhasil klir session.'
# blok modul==========================================================================
@app.route('/formPermintaanDelItem',methods=['POST','GET'])
def formPermintaanDelItem():
	#global barang_dipilih
	if request.method=='POST':
		tmp=''
		idx=request.get_json().get('id')
		#session['barang_dipilih'].remove(int(idx))
		for i in session['barang_dipilih'].split(','):
			print('formPermintaanDelItem split:'+str(i))
			if i!=idx:
				if tmp=='':
					tmp=i
				else:
					tmp+=','+i
			else:
				print('hapus item: '+str(i))
		session['barang_dipilih']=tmp
		print('formPermintaanDelItem :'+str(tmp))
		if idx not in session['barang_dipilih']:
			return jsonify({'success':'Berhasil'})
		else:
			return jsonify({'error':'Gagal'})
	return jsonify({'error':'Gagal kirim data POST'})
# blok modul==========================================================================
@app.route('/resetPermintaan',methods=['POST'])
def resetPermintaan():
	print('rest permintaan')
	#global barang_dipilih
	session['barang_dipilih']=''
	return jsonify({'success':'reset permintaan'})


def getUserPermintaan(nik):
	cursor.execute("SELECT nama,jabatan FROM user WHERE nik=%s LIMIT 1;",(nik))
	row=cursor.fetchone()
	tmp=[]
	tmp.append(row[0])
	tmp.append(row[1])
	return tmp

@app.route('/formPermintaan',methods=['POST','GET'])
def formPermintaan():
	barang_dipilih=''
	if session['barang_dipilih']!='':
		barang_dipilih=session['barang_dipilih']
	data=None
	print('formPermintaan:'+str(barang_dipilih))
	msg=''
	if request.method=='POST':
		statis=request.get_json().get('statis')
		dinamis=request.get_json().get('dinamis')
		if statis and dinamis:
			sql=''
			#--------------------------------------
			nomor=statis['nomor']
			periode=statis['periode']
			alasan=statis['alasan']
			id_divisi=statis['id_divisi']
			nama_divisi=statis['nama_divisi']
			operator=statis['operator']
			nik_operator=statis['nik_operator']
			nama_operator=statis['nama_operator']
			jab_operator=statis['jab_operator']
			nik_atasan=statis['atasan']
			xatasan=getUserPermintaan(str(nik_atasan))
			nama_atasan=xatasan[0]
			jab_atasan=xatasan[1]
			isplh=statis['isplh']
			nik_plh=statis['plh']
			xplh=getUserPermintaan(str(nik_plh))
			nama_plh=xplh[0]
			jab_plh=xplh[1]
			#--------------------------------------
			print('jumlah item: '+str(len(dinamis)))
			#--------------------------------------
			if int(isplh)==0:
				sql="INSERT INTO permintaan(nomor,periode,alasan,id_divisi,nama_divisi,nik_operator,nama_operator,jab_operator,nik_atasan,nama_atasan,jab_atasan)"
				sql+="VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
				try:
					cursor.execute(sql,(nomor,int(periode),alasan,int(id_divisi),nama_divisi,nik_operator,nama_operator,jab_operator,nik_atasan,nama_atasan,jab_atasan))
				except Exception as e:
					#raise e
					return jsonify({'error':'<h6>Terjadi kesalahan dalam penyimpanan data.</h6>Apakah nomor surat sudah pernah dipakai sebelumnya?<br/>Apakah permintaan untuk periode ini sudah ada?<hr/>'+str(e)})
				else:
					for d in range(len(dinamis)):
						if dinamis[d]:
							try:
								#nomor_permintaan,id_barang,user_nama,nama_barang,satuan_barang,harga_barang
								sql="INSERT INTO permintaan_d(nomor_permintaan,id_barang,jml_minta,user_nama,nama_barang,satuan_barang,harga_barang)"
								sql+="VALUES(%s,%s,%s,%s,%s,%s,%s);"
								cursor.execute(sql,(nomor,dinamis[d]['id'],dinamis[d]['jml'],operator,dinamis[d]['nama'],dinamis[d]['satuan'],dinamis[d]['harga']))
							except Exception as e:
								return jsonify({'error':'Terjadi kesalahan penyimpanan list pilihan item.'})
					return jsonify({'success':'Berhasil simpan data'})
			else:
				try:
					sql="INSERT INTO permintaan(nomor,periode,alasan,id_divisi,nama_divisi,nik_operator,nama_operator,jab_operator,nik_atasan,nama_atasan,jab_atasan,isplh,nik_plh,nama_plh,jab_plh)"
					sql+="VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
					cursor.execute(sql,(nomor,int(periode),alasan,int(id_divisi),nama_divisi,nik_operator,nama_operator,jab_operator,nik_atasan,nama_atasan,jab_atasan,int('1'),nik_plh,nama_plh,jab_plh))
				except Exception as e:
					return jsonify({'error':'<h6>Terjadi kesalahan dalam penyimpanan data.</h6>Apakah nomor surat sudah pernah dipakai sebelumnya?<br/>Apakah permintaan untuk periode ini sudah ada?<hr/>'+str(e)})
				else:
					for d in range(len(dinamis)):
						if dinamis[d]:
							try:
								#nomor_permintaan,id_barang,user_nama,nama_barang,satuan_barang,harga_barang
								sql="INSERT INTO permintaan_d(nomor_permintaan,id_barang,jml_minta,user_nama,nama_barang,satuan_barang,harga_barang)"
								sql+="VALUES(%s,%s,%s,%s,%s,%s,%s);"
								cursor.execute(sql,(nomor,dinamis[d]['id'],dinamis[d]['jml'],operator,dinamis[d]['nama'],dinamis[d]['satuan'],dinamis[d]['harga']))
							except Exception as e:
								return jsonify({'error':'Terjadi kesalahan penyimpanan list pilihan item.'})
					return jsonify({'success':'Berhasil simpan data'})
			print(str(nama_atasan))
			return jsonify(nama_plh)
		else:
			return(jsonify({'error':'Terjadi kesalahan penyimpanan data.\nApakah form belum dilengkapi?'}))
	else:
		form=FormOrder()
		cursor.execute("SELECT nik,CONCAT(nama,'  [',jabatan,']') AS nmx FROM user;")
		tuser=cursor.fetchall()
		suser=[(i[0], i[1]) for i in tuser]
		form.op_atasan.choices=suser
		cursor.execute("SELECT nik,nama FROM user;")
		tuser=cursor.fetchall()
		suser=[(i[0], i[1]) for i in tuser]
		form.op_plh.choices=suser
		#for ix in getPeriode():
		#	print(ix)
		prd=[(str(i),str(i)) for i in getPeriode()]
		form.op_periode.choices=prd
		if barang_dipilih:
			bdp=','.join(str(e) for e in barang_dipilih)
			#bdp.replace('[','')
			#bdp.replace(']','')
			#print(bdp)
			#brg=str(session['barang_dipilih'])
			#print(brg)
			sql="SELECT DISTINCT id,nama,satuan,harga,nama_foto,ket FROM barang WHERE id IN("+ str(barang_dipilih) +");"
			#print(sql)
			cursor.execute(sql)
			data=cursor.fetchall()
			print(sql+'\n'+str(barang_dipilih))
		return render_template('form-permintaan.html',form=form,data=data)
# blok modul==========================================================================

# blok modul==========================================================================

# blok modul==========================================================================

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