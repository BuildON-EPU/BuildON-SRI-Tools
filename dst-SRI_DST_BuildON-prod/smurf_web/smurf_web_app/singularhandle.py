from requests import get,post
from .models import Levels, Services
import itertools
import json
import pprint
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from django.http import HttpResponse


def singular_data(building_id):
    # Step 1: Authenticate with FastAPI
    auth_credentials = {
        'username': 'test_ntua',
        'password': '123456789'  # Update as needed
    }

    # to run on server
    login_url = 'http://sri-calculator-backend-service:8000/api/token'
    # to run locally
    #login_url = 'http://buildon.epu.ntua.gr:8003/api/token'
    login_response = requests.post(login_url, data=auth_credentials)

    if login_response.status_code != 200:
        return {"error": f"Authentication failed: {login_response.status_code}"}

    token = login_response.json().get("access_token")
    if not token:
        return {"error": "Failed to retrieve access token"}

    # Step 2: Use token to fetch dst_format from FastAPI
    headers = {'Authorization': f'Bearer {token}'}
    # to run on server
    fastapi_url = f'http://sri-calculator-backend-service:8000/api/upgrade-scenarios/{building_id}/'
    # to run locally
    #fastapi_url = f'http://buildon.epu.ntua.gr:8003/api/upgrade-scenarios/{building_id}/'


    try:
        resp = requests.get(fastapi_url, headers=headers)
    except requests.exceptions.RequestException as e:
        return {"error": f"Request to FastAPI failed: {str(e)}"}

    print(f"FastAPI Response Status Code: {resp.status_code}")
    print(f"FastAPI Response Content: {resp.content}")

    if resp.status_code == 200:
        initial_data = resp.json()
        pprint.pprint(initial_data)  # For debugging
        return initial_data
    elif resp.status_code == 404:
        return {"error": "DST format not found for this building."}
    else:
        return {"error": f"Unexpected FastAPI response: {resp.status_code}"}

    
# # Convert JSON to correct format
# def map_service_code_to_name(service_code):
#     service_mapping = {
#         "H-1a": "Heat emission control",
#         "C-1a": "Cooling emission control",
#         "V-1a": "Supply air flow control at the room level",
#         # Add mappings for other service codes...
#     }
#     return service_mapping.get(service_code, "Unknown Service")

# def map_service_code_to_domain(service_code):
#     domain_mapping = {
#         "H-1a": "Heating",
#         "C-1a": "Cooling",
#         "V-1a": "Ventilation",
#         # Add mappings for other service codes...
#     }
#     return domain_mapping.get(service_code, "Unknown Domain")

# def map_service_code_to_functionality(service_code, level):
#     functionality_mapping = {
#         ("H-1a", 1): "Central automatic control (e.g. central thermostat)",
#         ("C-1a", 2): "Individual room control",
#         ("V-1a", 0): "No ventilation system or manual control",
#         # Add mappings for other service codes and levels...
#     }
#     return functionality_mapping.get((service_code, level), "Unknown Functionality")

# # Function for data transformation
# def transform_dst_format(dst_format):
#     # Transform domain_scores
#     domain_scores = [
#         {"domain": domain, "percentage": value, "score": value}
#         for domain, value in dst_format.get("domain_scores", {}).items()
#     ]
    
#     # Transform impact_scores
#     impact_scores = [
#         {"impact": impact, "percentage": value, "score": value}
#         for impact, value in dst_format.get("impact_scores", {}).items()
#     ]
    
#     # Transform key_functionalities_scores
#     key_functionalities_scores = [
#         {"key_functionality": functionality, "percentage": value}
#         for functionality, value in dst_format.get("key_functionalities_scores", {}).items()
#     ]
    
#     # Transform services
#     services = [
#         {
#             "service": map_service_code_to_name(service["service_code"]),
#             "service_code": service["service_code"],
#             "level": service["level"],
#             "domain": map_service_code_to_domain(service["service_code"]),
#             "functionality": map_service_code_to_functionality(service["service_code"], service["level"])
#         }
#         for service in dst_format.get("services", [])
#     ]

#     # Construct the final transformed data
#     input_data = {
#         "user": dst_format.get("user"),
#         "input_sri": dst_format.get("input_sri"),
#         "building_type": dst_format.get("building_type"),
#         "zone": dst_format.get("zone"),
#         "domain_scores": domain_scores,
#         "impact_scores": impact_scores,
#         "key_functionalities_scores": key_functionalities_scores,
#         "services": services
#     }

#     #print(transformed_data)

#     return input_data


# Function to map service code to name using the Services model
def map_service_code_to_name(service_code):
    try:
        service = Services.objects.get(code=service_code)
        return service.service_desc  # Assuming service_desc is the name of the service
    except Services.DoesNotExist:
        return "Unknown Service"

# Function to map service code to domain using the Services model
def map_service_code_to_domain(service_code):
    try:
        service = Services.objects.get(code=service_code)
        return service.domain  # Assuming domain is the correct field in the Services model
    except Services.DoesNotExist:
        return "Unknown Domain"

# Function to map service code and level to functionality using the Levels model
def map_service_code_to_functionality(service_code, level):
    try:
        level_obj = Levels.objects.get(code=service_code, level=level)
        return level_obj.desc  # Assuming desc is the functionality description in Levels
    except Levels.DoesNotExist:
        return "Unknown Functionality"

# Function for data transformation
def transform_dst_format(dst_format):
    # Ensure all 9 domains are present in the domain_scores list
    all_domains = [
        "Heating", "Domestic hot water", "Cooling", "Ventilation",
        "Lighting", "Electricity", "Dynamic building envelope",
        "Electric vehicle charging", "Monitoring and control"
    ]

    # Get the input domain scores
    input_domain_scores = dst_format.get("domain_scores", {})

    # Ensure every domain is present with default values if missing
    domain_scores = [
        {"domain": domain, "percentage": input_domain_scores.get(domain, 0), "score": input_domain_scores.get(domain, 0)}
        for domain in all_domains
    ]

    # # Transform domain_scores
    # domain_scores = [
    #     {"domain": domain, "percentage": value, "score": value}
    #     for domain, value in dst_format.get("domain_scores", {}).items()
    # ]
    
    # Transform impact_scores
    impact_scores = [
        {"impact": impact, "percentage": value, "score": value}
        for impact, value in dst_format.get("impact_scores", {}).items()
    ]
    
    # Transform key_functionalities_scores
    key_functionalities_scores = [
        {"key_functionality": functionality, "percentage": value}
        for functionality, value in dst_format.get("key_functionalities_scores", {}).items()
    ]
    
    # Transform services using models to dynamically fetch data
    services = [
        {
            "service": map_service_code_to_name(service["service_code"]),
            "service_code": service["service_code"],
            "level": service["level"],
            "domain": map_service_code_to_domain(service["service_code"]),
            "functionality": map_service_code_to_functionality(service["service_code"], service["level"])
        }
        for service in dst_format.get("services", [])
    ]

    # Construct the final transformed data
    input_data = {
        "user": dst_format.get("user"),
        "input_sri": dst_format.get("input_sri"),
        "building_type": dst_format.get("building_type"),
        "zone": dst_format.get("zone"),
        "domain_scores": domain_scores,
        "impact_scores": impact_scores,
        "key_functionalities_scores": key_functionalities_scores,
        "services": services
    }

    return input_data

