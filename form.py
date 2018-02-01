from flask_wtf import Form
from wtforms import  TextField, IntegerField, TextAreaField, StringField, SubmitField, BooleanField, PasswordField, HiddenField, FileField
from wtforms import validators, ValidationError

class FormDataBarang(Form):
	tx_id = HiddenField()
	tx_nama = TextField('Nama Barang', [validators.Required("Masukkan nama.")])
	tx_harga = IntegerField('Harga', [validators.Required("Masukkan harga (numerik).")])
	tx_satuan = TextField('Satuan', [validators.Required("Masukkan satuan.")])
	tx_ket = TextField('Keterangan', [validators.Required("Masukkan keterangan.")])
	file_foto = FileField('Foto produk')

class FormDataVendor(Form):
	tx_id = HiddenField()
	tx_nama = TextField('Nama perusahaan', [validators.Required("Masukkan nama perusahaan.")])
	tx_alamat = TextField('Alamat', [validators.Required("Masukkan alamat.")])
	tx_telp = TextField('Telepon', [validators.Required("Masukkan nomor telepon.")])
	tx_email = TextField('Email', [validators.Required("Masukkan email.")])
	tx_pemilik = TextField('Nama pemilik', [validators.Required("Masukkan nama pemilik.")])