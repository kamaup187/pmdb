class PropertyValidator:
    
    def __init__(self, data):
        if not data:
            return {
                'status': 400,
                'message': 'No data provided'
            }, 400

        self.data = {
            "property_name": data.get('property_name')
        }
        self.optionals = [] # list of strings

    def validate_fields(self):
        for key, value in self.data.items():
            if not value:
                print('TRUE')
                return {"msg": "{} is required".format(key)}, 400

    def valid_name(self, name_list):
        for name in name_list:
            if len(name) < 3:
                return {"msg": "name too short"}, 400
            elif len(name) > 60:
                return {"msg": "name too long"}, 400
            pass