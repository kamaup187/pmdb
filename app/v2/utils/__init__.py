def validate(data, Resource):
    resource = Resource(data)
    valid_fields = resource.validate_fields()

    if valid_fields:
        return valid_fields
        
    valid_name = resource.valid_name([data.get('property_name')])

    if valid_name:
        return valid_name