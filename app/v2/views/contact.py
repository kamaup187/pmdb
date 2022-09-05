# from flask_login import login_required, current_user
# from flask_restful import Resource
# from flask import render_template,Response,request,flash,redirect,url_for,session
# from app.v1.models.operations import *
# from .helperfuncs import *
# from ..forms.forms import ContactForm,ReadingForm

# class ContactUs(Resource):
#     def get(self):
#         form = ContactForm()
#         form.name.data = "Name"
#         return Response(render_template('contactus.html',form=form))
#     def post(self):
#         form = ContactForm()
#         if form.validate_on_submit():
            
#             return redirect(url_for('success'))
#         import pdb; pdb.set_trace()
#         return Response(render_template('contactus.html',form=form))

# class SelectCounty(Resource):
#     @login_required
#     def get(self):
#         form = ReadingForm()
#         apartment_list = fetch_all_apartments()
#         place_holder_item = '--Select Apartment--'
#         apartment_list.insert(0,place_holder_item)
#         form.state.choices = apartment_list
#         # form.state.choices = ['select country','Kenya','Uganda']
#         try:
#             stor = store
#             house = county
#             last_readin = last_reading
#             reading_now = curr_reading
#             consumed_units = units_consumed
#             print("found finally")
            
#         except:
#             stor = None
#             house = None
#             last_readin = None
#             reading_now = None
#             consumed_units = None
#             print("not found initially")
            

#         if stor:
            
#             house_list = filtered_house_list(stor)

#             place_holder_item = '--Select House--'
#             house_list.insert(0,place_holder_item)
#             form.county.choices = house_list
#             form.selected_apartment.data = f"current apartment: {stor}, House : {county}"
#             form.prev_reading.data = f"Previous reading : {last_readin}, Current reading : {reading_now}"
#             form.units.data = f"Units consumed : {units_consumed}"
#         else:
            
#             form.county.choices = []
        
        
#         return Response(render_template('pick_county.html', form=form,name=current_user.username))
#     def post(self):
#         global store

#         form = ReadingForm()

#         state = form.data.get('state')
#         if state:
#             if state == '--Select Apartment--':
#                 pass
#             else:
#                 store = state
#         global county
#         county = form.data.get('county')
#         name = form.data.get('name')
#         description = "bill"

#         if not county:
#             house_list = filtered_house_list(store)
#             place_holder_item = '--Select House--'
#             house_list.insert(0,place_holder_item)
#             form.county.choices = house_list
            

#             return render_template('options.html', form=form)

#         house_list_compare = filtered_house_list(store)
#         house_obj = None
#         for house in house_list_compare:
#             if str(house) == county:
#                 house_obj = house

#         house_id = house_obj.id
#         meter_obj_alloc = house_obj.meter_allocated
#         tenant_obj_alloc = house_obj.tenant_allocated

#         if not meter_obj_alloc or not tenant_obj_alloc:
#             msg = "This house has no assigned meter or is not occupied"
#             flash(msg)
#             house_list = filtered_house_list(store)
#             return Response(render_template('readings.html',house_list=house_list))

#         #lets get meter_id from meter obj
#         meter_obj = meter_obj_alloc.meter
#         tenant_obj = tenant_obj_alloc.tenant

#         meter_id = meter_obj.id
#         apartment_id = get_apartment_id(store)
#         user_id = current_user.id


#         previous_reading = getlast_reading(meter_id)
#         global last_reading
#         if previous_reading:
#             last_reading = previous_reading
        
#         current_reading = float(name)
#         global curr_reading
#         curr_reading = current_reading
#         units = current_reading
#         if previous_reading:
#             units = current_reading-previous_reading
#         global units_consumed
#         units_consumed = units

#         reading_obj = MeterReadingOp(description,name,units,apartment_id,house_id,meter_id,user_id)
#         reading_obj.save()

#         msg = f"Readings for house number {county} has been captured successfully"

#         flash(msg,"is-success")
#         return redirect(url_for('api.selectcounty'))

        