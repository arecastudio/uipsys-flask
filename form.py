from flask_wtf import FlaskForm
from wtforms import  TextField, IntegerField, TextAreaField, SelectField, StringField, SubmitField, BooleanField, PasswordField, HiddenField, FileField
from wtforms import validators, ValidationError
from wtforms.validators import InputRequired, Email
from wtforms.fields.html5 import EmailField

class FormLogin(FlaskForm):
	tx_user = TextField('Username',[validators.Required("Masukkan username.")])
	tx_pass = PasswordField('Password', [validators.Required("Masukkan password.")])

class FormDataBarang(FlaskForm):
	tx_id = HiddenField()
	tx_nama = TextField('Nama Barang', [validators.Required("Masukkan nama.")])
	tx_harga = IntegerField('Harga', [validators.Required("Masukkan harga (numerik).")])
	tx_satuan = TextField('Satuan', [validators.Required("Masukkan satuan.")])
	tx_ket = TextAreaField('Keterangan', [validators.Required("Masukkan keterangan.")])
	file_foto = FileField('Foto produk')

class FormDataVendor(FlaskForm):
	tx_id = HiddenField()
	tx_nama = TextField('Nama perusahaan', [validators.Required("Masukkan nama perusahaan.")])
	tx_alamat = TextField('Alamat', [validators.Required("Masukkan alamat.")])
	tx_telp = TextField('Telepon', [validators.Required("Masukkan nomor telepon.")])
	tx_email = TextField('Email', [validators.Required("Masukkan email.")])
	tx_pemilik = TextField('Nama pemilik', [validators.Required("Masukkan nama pemilik.")])

class FormDataBidang(FlaskForm):
	tx_id = HiddenField()
	tx_nama = TextField('Nama Bidang', [validators.Required("Masukkan nama bidang / divisi.")])	
	tx_ket = TextAreaField('Keterangan', [validators.Required("Masukkan keterangan.")])

class FormManUser(FlaskForm):
	tx_id = HiddenField()
	tx_user = TextField('Username', [validators.Required("Masukkan nama lengkap.")])
	tx_nik = TextField('NIK', [validators.Required("Masukkan NIK.")])
	tx_nama = TextField('Nama Karyawan', [validators.Required("Masukkan nama lengkap.")])
	tx_pass = PasswordField('Password', [validators.optional()])
	tx_telp = TextField('Telepon', [validators.Required("Masukkan nomor telepon.")])
	tx_mail = EmailField('Email', [validators.Required("Masukkan email.")])
	op_divisi = SelectField('Bidang',[validators.optional()], coerce=int)
	op_role = SelectField('Hak Pakai',[validators.optional()], coerce=int)
	tx_jabatan = TextField('Jabatan', [validators.Required("Masukkan jabatan.")])

class FormOrder(FlaskForm):
	tx_id = HiddenField()
	op_periode = SelectField('Periode permintaan',[validators.optional()], coerce=str)
	tx_nomor = TextField('Nomor Surat',[validators.required('Masukkan nomor surat.')])
	tx_alasan = TextAreaField('Perihal', [validators.Required("Masukkan perihal.")])
	tx_operator = TextField('Yang membuat', [validators.Required("Masukkan nama.")])
	op_atasan = SelectField('Penanggung Jawab (Atasan)',[validators.optional()], coerce=str)
	op_plh = SelectField('Pelaksana/pengganti',[validators.optional()], coerce=str)
	#tx_jab1 = TextField('Jabatan', [validators.Required("Masukkan perihal.")])
	#tx_jab2 = TextField('Jabatan', [validators.Required("Masukkan perihal.")])
