"""table"""
from flask_table import Table, Col

# Declare your table
class BugTable(Table):
    """table for user info"""
    classes = ['table', 'th','td']
    id = Col('Bug id')
    description = Col('Description')
    created_by = Col('Reported by')

class ApartmentTable(Table):
    """table for user info"""
    classes = ['table', 'th','td']
    Apartment_Id = Col('Apartment id')
    Name = Col('Name')
    Location = Col('Location')
    Owner = Col('Owner')

class ClientTable(Table):
    """table for user info"""
    classes = ['table', 'th','td']
    member_id = Col('Client Id')
    username = Col('Client Username')
    apartments = Col('Apartment(s)')

class BalanceTable(Table):
    """table"""
    classes = ['table', 'th','td']
    name = Col('Name')
    house = Col('House')
    id_no = Col('Id No')
    balance = Col('Balance')

class MonthlyBillTable(Table):
    """table"""
    classes = ['table', 'th','td']
    id = Col('Id')
    apartment = Col('Aparment')
    house = Col('House')
    tenant = Col('Tenant')
    date = Col('Date')
    amount = Col('Amount')
    billedby = Col('Billedby')
