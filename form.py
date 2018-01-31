#from flask_wtf import Form
from wtforms import  Form, TextField, IntegerField, TextAreaField, StringField, SubmitField, BooleanField, PasswordField, HiddenField, FileField
from wtforms import validators, ValidationError
class FormDataBarang(Form):
	tx_id = HiddenField()
	tx_nama = TextField('Nama Barang', [validators.Required("Masukkan nama.")])
	tx_harga = IntegerField('Harga', [validators.Required("Masukkan harga (numerik).")])
	tx_satuan = TextField('Satuan', [validators.Required("Masukkan satuan.")])
	tx_ket = TextField('Keterangan', [validators.Required("Masukkan keterangan.")])
        file_foto = FileField('Foto produk')
