from flask_wtf import Form
from wtforms import  TextField, IntegerField, TextAreaField, SelectField, StringField, SubmitField, BooleanField, PasswordField, HiddenField, FileField
from wtforms import validators, ValidationError
from wtforms.validators import InputRequired, Email
from wtforms.fields.html5 import EmailField

class FormLogin(Form):
	tx_user = TextField('Username',[validators.Length(min=1,max=20)])
	tx_pass = PasswordField('Password', [validators.Required("Masukkan password.")])

class FormDataBarang(Form):
	tx_id = HiddenField()
	tx_nama = TextField('Nama Barang', [validators.Required("Masukkan nama.")])
	tx_harga = IntegerField('Harga', [validators.Required("Masukkan harga (numerik).")])
	tx_satuan = TextField('Satuan', [validators.Required("Masukkan satuan.")])
	tx_ket = TextAreaField('Keterangan', [validators.Required("Masukkan keterangan.")])
	file_foto = FileField('Foto produk')

class FormDataVendor(Form):
	tx_id = HiddenField()
	tx_nama = TextField('Nama perusahaan', [validators.Required("Masukkan nama perusahaan.")])
	tx_alamat = TextField('Alamat', [validators.Required("Masukkan alamat.")])
	tx_telp = TextField('Telepon', [validators.Required("Masukkan nomor telepon.")])
	tx_email = TextField('Email', [validators.Required("Masukkan email.")])
	tx_pemilik = TextField('Nama pemilik', [validators.Required("Masukkan nama pemilik.")])

class FormDataBidang(Form):
	tx_id = HiddenField()
	tx_nama = TextField('Nama Bidang', [validators.Required("Masukkan nama bidang / divisi.")])	
	tx_ket = TextAreaField('Keterangan', [validators.Required("Masukkan keterangan.")])

class FormManUser(Form):
	tx_id = HiddenField()
	tx_user = TextField('Username', [validators.Length(min=5, max=20)])
	tx_nama = TextField('Nama Karyawan', [validators.Required("Masukkan nama lengkap.")])
	tx_pass = PasswordField('Password', [validators.Required("Masukkan password.")])
	tx_telp = TextField('Telepon', [validators.Required("Masukkan nomor telepon.")])
	tx_mail = EmailField('Email', [validators.Required("Masukkan email.")])
	op_divisi = SelectField('Bidang',[validators.optional()], coerce=int)
	op_role = SelectField('Hak Pakai',[validators.optional()], coerce=int)
	tx_jabatan = TextField('Jabatan', [validators.Required("Masukkan jabatan.")])