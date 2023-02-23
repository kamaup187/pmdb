'''Tests product resource.'''
import json
from app import db
from flask_login import login_user,current_user
from app.v1.models.operations import *

from tests.base_test import BaseTest


class SomeTest(BaseTest):

    def test_something(self):

        region = LocationOp("Tumoi","Home")

        db.session.add(region)
        db.session.commit()

        self.assertEqual(region.name, "Tumoi")


    def test_something2(self):

        datum = {
        "region" : "fhkdhf",
        "description" :"hdshgh"
        }

        response = self.client.post("/add/location", data=datum)
        result = response.data
        self.assertEqual(response.status_code, 200)

    def test_that_something_works(self):

        usergroup = UserGroupOp("Manager","desc")
        usergroup.save()

        company = CompanyOp("Test Co","","","","","")
        company.save()

        group1 = CompanyUserGroupOp("Manager","administrator","1")
        group1.save()

        user = UserOp("John Doe","00","testuser","00","00","james@mail.com","1234","1","1","1")
        user.save()

        with self.client:
            response = self.client.post('/signin', data = { "identifier": '00', "password": '1234' })
            self.assertEquals(current_user.username, 'testuser')

    def test_add_tenant(self):
        usergroup = UserGroupOp("Manager","desc")
        usergroup.save()

        company = CompanyOp("Test Co","","","","","")
        company.save()

        group1 = CompanyUserGroupOp("Manager","administrator","1")
        group1.save()

        user = UserOp("John Doe","00","testuser","00","00","james@mail.com","1234","1","1","1")
        user.save()

        with self.client:
            self.client.post('/signin', data = { "identifier": '00', "password": '1234' })


            region = LocationOp("Tumoi","Home")
            region.save()

            landlord = OwnerOp("Owner",None,None,"N/A","1")
            landlord.save()

            prop = ApartmentOp("Test Apartment","",region.id,landlord.id,True,"1")
            prop.save()

            datum = {
            "propid" : "1",
            "name" :"Test Tenant",
            "target" :"test",
            "current_user":current_user.id
            }

            response = self.client.post("/add/tenant", data=datum)
            result = response.data
            self.assertEqual(response.status_code, 201)

# class TestEditIncident(BaseCase):
#     """class to test EDIT functionality"""

#     def test_can_create_incident(self):
#         """Test the POST functionality."""
#         response = self.client.post(POST_URL, data=json.dumps(self.data))
#         result = json.loads(response.data)
#         expected = "Incident reported successfully"
#         self.assertEqual(result["message"], expected)
#         self.assertEqual(response.status_code, 201)
    
    # def test_can_get_incidents(self):
    #     """Test the GET functionality."""
    #     self.client.post(POST_URL, data=json.dumps(self.data))
    #     self.client.post(POST_URL, data=json.dumps(self.data2))
    #     response = self.client.get('/v1/user/get/incidents')
    #     result = json.loads(response.data)
    #     expected = "Incidents found"
    #     self.assertEqual(result["message"], expected)
    #     self.assertEqual(response.status_code, 200)
    
    # def test_can_get_specific_incident(self):
    #     """Test the GET functionality for viewing a single incident."""
    #     self.client.post(POST_URL, data=json.dumps(self.data))
    #     response = self.client.get(GET_URL)
    #     result = json.loads(response.data)
    #     expected = "Incident found"
    #     self.assertEqual(result["message"], expected)
    #     self.assertEqual(response.status_code, 200)

    # def test_can_edit_incidences(self):
    #     resp = self.client.post(POST_URL, data=json.dumps(self.data))
    #     response = self.client.patch('/v1/user/put/incident/1', data=json.dumps(self.data2))
    #     result = json.loads(response.data)
    #     expected = "Record updated successfully"
    #     self.assertEqual(result["message"], expected)
    #     self.assertEqual(response.status_code, 200)

    #     response2 = self.client.patch('/v1/user/put/incident/1', data=json.dumps(self.invalid_type))
    #     result = json.loads(response2.data)
    #     expected2 = "Description must be a string and not integer"
    #     self.assertEqual(result["message"], expected2)
    #     self.assertEqual(response2.status_code, 401)
    
    # def test_can_delete_incidences(self):
    #     """Test the DELETE functionality of deleting an incident."""
    #     self.client.post(POST_URL, data=json.dumps(self.data))
    #     response = self.client.delete('/v1/user/del/incident/1')
    #     result = json.loads(response.data)
    #     expected = 'Record deleted successfully'
    #     self.assertEqual(result["message"], expected)
    #     self.assertEqual(response.status_code, 200)
    #     response = self.client.get(GET_URL)
    #     result = json.loads(response.data)
    #     expected = "Incident not found"
    #     self.assertEqual(result["message"], expected)
    #     self.assertEqual(response.status_code, 404)

    # def test_can_catch_invalid_data_input_error(self):
    #     """Test the robustness  if invalid data type is supplied."""
    #     response = self.client.post(POST_URL, data=json.dumps(self.invalid_type))
    #     result = json.loads(response.data)
    #     expected = "Description must be a string and not integer"
    #     self.assertEqual(result["message"], expected)
    #     self.assertEqual(response.status_code, 401)

    # def test_can_reject_special_char_input(self):
    #     response = self.client.post(POST_URL, data=json.dumps(self.specialchar_data))
    #     result = json.loads(response.data)
    #     expected = "Special characters not allowed!"
    #     self.assertEqual(result["message"], expected)
    #     self.assertEqual(response.status_code, 401)

    # def test_can_reject_empty_strings(self):
    #     response = self.client.post(POST_URL, data=json.dumps(self.empty_field_data))
    #     result = json.loads(response.data)
    #     expected = "Location cannot be blank"
    #     self.assertEqual(result["message"], expected)
    #     self.assertEqual(response.status_code, 401)

    # def test_can_reject_whitespaces(self):
    #     response = self.client.post(POST_URL, data=json.dumps(self.whitespace_data))
    #     result = json.loads(response.data)
    #     expected = "Location cannot be left blank"
    #     self.assertEqual(result["message"], expected)
    #     self.assertEqual(response.status_code, 401)

