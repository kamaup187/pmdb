from app.v1.views.helperfuncs import account_validation,account_pesalink_transfer,ins_api_account_subscription, generate_hash

testkey = "IlcPPVkyc0mKe3jeufo9bjII6Mwa"
testsec = "Def5yXFOSgKNJAzJshxDE8YkvSca"

prodkey = "8vnRuq9m3OmxliAJn1WfgmogagYa"
prodsec = "CEMIEl7b2IMn8NlTlg7qVcY74Joa"


# account_validation("IlcPPVkyc0mKe3jeufo9bjII6Mwa","Def5yXFOSgKNJAzJshxDE8YkvSca","01148173864900")

# account_validation(prodkey,prodsec,"01148173864900")

ins_api_account_subscription(prodkey,prodsec,"01148173864900","622521Pt#")

# account_pesalink_transfer(prodkey,prodsec,"01148173864900","01148173864901")

# print(generate_hash("merit","q150c2bf1c4ee7da42yt"))

