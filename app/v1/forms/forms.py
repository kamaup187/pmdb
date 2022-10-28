# from flask_wtf import FlaskForm
# from wtforms import StringField, TextField, SubmitField,SelectField,PasswordField,DateField,TextAreaField,HiddenField,DecimalField,BooleanField
# from wtforms.fields.html5 import EmailField
# from wtforms.validators import DataRequired, Length, Email,EqualTo,Length,URL

# class ContactForm(FlaskForm):
#     """Contact form."""
#     name = StringField('Name', [DataRequired()])

#     email = StringField('Email', [DataRequired(),Email(message=('Not a valid email address.'))])
#     password = PasswordField('Password', [DataRequired(message="Please enter a password.")])
#     confirm_password = PasswordField('Repeat Password',[EqualTo('password', message='Passwords must match.')])
#     title = SelectField('Title', [DataRequired()],choices=[('Farmer', 'farmer'),('Corrupt Politician', 'politician'),('No-nonsense City Cop', 'cop'),('Professional Rocket League Player', 'rocket'),('Lonely Guy At A Diner', 'lonely'),('Pokemon Trainer', 'pokemon')])
#     website = StringField('Website', validators=[URL()])
#     birthday = DateField('Your Birthday')

#     # email = EmailField('Email', validators=[DataRequired(), Email(message=('Not a valid email address.'))])

#     body = TextField('Message', [DataRequired(),Length(min=4, message=('Your message is too short.'))])

#     submit = SubmitField('Submit')

# class CreateHouseForm(FlaskForm):
#     """class"""
#     apartment = SelectField('Apartment:',validate_choice=False,id='select_apartment')
#     house = StringField('House', [DataRequired()],id='enter_house')
#     desc = StringField('description')
#     submit = SubmitField('Add House')

# class UserRegForm(FlaskForm):
#     """class"""
#     owner = SelectField('Owner',validate_choice=False,id='select_owner')
#     apartment = SelectField('Apartment:',validate_choice=False,id='select_apartment')
#     usergroup = SelectField('Usergroup', validate_choice=False,id='select_usergroup')

# class ReadingForm(FlaskForm):
#     apartment = SelectField('Apartment:',validate_choice=False,id='select_apartment')
#     house = SelectField('House:',validate_choice=False,id='select_house')
#     # reading = DecimalField('Reading', [DataRequired()],id='reading')
#     submit = SubmitField('Submit reading')

# class MeterAllocForm(FlaskForm):
#     apartment = SelectField('apartment:',validate_choice=False,id='select_apartment')
#     house = SelectField('house:',validate_choice=False,id='select_house')
#     meter = SelectField('meter:',validate_choice=False,id='select_meter')
#     desc = StringField('description')
#     submit = SubmitField('Allocate')

# class TenantAllocForm(FlaskForm):
#     apartment = SelectField('apartment:',validate_choice=False,id='select_apartment')
#     house = SelectField('house:',validate_choice=False,id='select_house')
#     tenant = SelectField('tenant:',validate_choice=False,id='select_tenant')
#     desc = StringField('description')
#     submit = SubmitField('Allocate')

# class ChargeDescForm(FlaskForm):
#     apartment = SelectField('apartment:',validate_choice=False,id='select_apartment')
#     house = SelectField('house:',validate_choice=False,id='select_house')
#     chargetype = SelectField('chargetype:',validate_choice=False,id='select_chargetype')
#     amount = DecimalField('amount', [DataRequired()])
#     submit = SubmitField('Submit')

# class AmendChargeForm(FlaskForm):
#     apartment = SelectField('apartment:',validate_choice=False,id='select_apartment')
#     tenant = SelectField('tenant:',validate_choice=False,id='select_tenant')
#     chargetype = SelectField('chargetype:',validate_choice=False,id='select_chargetype')
#     month = SelectField('month:',validate_choice=False,id='select_month')
#     amount = DecimalField('amount', [DataRequired()])
#     desc = StringField('description')
#     submit = SubmitField('Submit')

# class PaymentForm(FlaskForm):
#     apartment = SelectField('apartment:',validate_choice=False,id='select_apartment')
#     # tenant = SelectField('tenant:',validate_choice=False,id='select_tenant')
#     house = SelectField('house:',validate_choice=False,id='select_house')
#     chargetype = SelectField('chargetype:',validate_choice=False,id='select_chargetype')
#     paymode = SelectField('paymode:',validate_choice=False,id='select_paymode')  
#     # month = SelectField('month:',validate_choice=False,id='select_month')
#     bill_ref = StringField('bill_ref')
#     amount = DecimalField('amount', [DataRequired()])
#     desc = StringField('description')
#     submit = SubmitField('Submit')

# class ModifyAccessRightForm(FlaskForm):
#     usergroup = SelectField('usergroup',validate_choice=False,id='select_usergroup')
#     grouprole = SelectField('grouprole',validate_choice=False,id='select_grouprole')
#     accessright = BooleanField('accessright',id='access_right')
#     submit = SubmitField('Submit')

