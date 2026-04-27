from .models import Services, Levels

def readcsv(csv_data):
    # Convert given list of list in JSON
    d = {}
    #d["user"] = int(csv_data[1][0]) if len(csv_data) > 1 else None
    d["input_sri"] = int(csv_data[1][1]) if len(csv_data) > 1 else None
    d["building_type"] = csv_data[1][2] if len(csv_data) > 1 else None
    d["zone"] = csv_data[1][3] if len(csv_data) > 1 else None

    # Initialize an empty list to store services
    d["services"] = []

    # Iterate through the CSV data and fetch service information
    for row in csv_data[1:]:
        service = row[4]
        level = int(row[5])

        # Fetch the service information from the Services model
        service_query1 = Services.objects.filter(code=service).values('domain', 'service_desc').first()

        if service_query1:
            service_desc = service_query1.get('service_desc')
            domain = service_query1.get('domain')
        else:
            service_desc = None
            domain = None

        # Fetch the functionality description from the Levels model
        service_query2 = Levels.objects.filter(code=service, level=level).values('desc').first()

        if service_query2:
            desc = service_query2.get('desc')
        else:
            desc = None
    
        # Create a dictionary for the service
        service_dict = {
            "service_code": service,
            "service": service_desc,
            "level": level,
            "domain": domain,
            "functionality": desc,
            #"service_desc": service_desc,
        }

        d["services"].append(service_dict)

    return d
