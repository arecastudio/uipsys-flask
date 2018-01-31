from wtforms import Form, BooleanField, StringField, PasswordField, TextAreaField, IntegerField, RadioField, SelectField, SubmitField
from wtforms import validators, ValidationError

class FormDataBarang(Form):
    tx_nama=StringField('Nama barang',[validators.Length(min=1,max=100)])
    tx_harga=IntegerField('Harga',[validators.DataRequired()])
    tx_satuan=StringField('Satuan',[validators.Length(min=1,max=100)])
    tx_ket=StringField('Keterangan',[validators.Length(min=1,max=200)])
