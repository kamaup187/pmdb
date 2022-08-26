class UserValidator:
    
    def __init__(self, data):
        if not data:
            return {
                'status': 400,
                'message': 'No data provided'
            }, 400

        self.data = {
            "target": data.get('target'), # target can be -> 'update prop billing info' | 'update property'
            "property_id": data.get('property_id'),
            "property_name": data.get('property_name'),
            "colltype": data.get('colltype'),
            "commission_type": data.get('commission_type'),
            "commission": data.get('commission'),
            "estate": data.get('estate'),
            "landlord": data.get('landlord'),
            "phone_number": data.get('phone_number')
        }
        self.optionals = [
            'estate',
            'phone_number',
            'landlord'
        ]

    def validate_fields(self):
        for key, value in self.data.items():
            print(key, ' in self.optionals', key in self.optionals)
            if not value and key not in self.optionals:
                return {"msg": "{} is required".format(key)}, 400
            pass

    def valid_name(self, name_list):
        for name in name_list:
            if len(name) < 3:
                return {"msg": "name too short"}, 400
            elif len(name) > 60:
                return {"msg": "name too long"}, 400
            pass