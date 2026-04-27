from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from .singularhandle import singular_data, transform_dst_format
from .scenarios import calculate_SR
from .forms import *
from .csvhandle import *
from .models import *
import json
import csv
from django.views.decorators.csrf import csrf_exempt
from .forms import SriForm
from .singularhandle import singular_data
from .scenarios import calculate_SR
from django.middleware.csrf import get_token

# Create your views here.

def landing_page(request):
    if request.method == 'POST':
        form = HandleUploadFile(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data['csvFile']
            csv_text = uploaded_file.read().decode('utf-8')
            csv_data = list(csv.reader(csv_text.splitlines()))
            data = readcsv(csv_data)
            request.session['csv_data'] = data
            return redirect("/smurf/set/srigoal/csv")
    else:
        return render(request, 'landing_page.html')

@csrf_exempt
def set_sri_goal(request, building_id):
    if request.method == 'POST':
        form = SriForm(request.POST)
        if form.is_valid():
            sri_goal = form.cleaned_data["sri_goal"]
            request.session["sri_goal"] = sri_goal
            input_data = request.session.get('data')
            scenarios_data = calculate_SR(input_data, sri_goal)
            return render(request, 'upgrade_scenarios.html', {
                "scenarios_dict": scenarios_data,
                "input_data": input_data
            })
        else:
            print("Invalid form data:", form.errors)
            return HttpResponse("Invalid form data", status=400)
    else:
        # Fetch data from FastAPI and transform it
        dst_format = singular_data(building_id)
        if 'error' in dst_format:
            print(f"Error loading data from FastAPI: {dst_format}")
            return HttpResponse("Failed to load data from FastAPI", status=500)

        # Transform the dst_format to the expected format
        data = transform_dst_format(dst_format)
        
        # Store the transformed data in session
        request.session["data"] = data

        # Pass services separately to the template
        services = data.get('services', [])

        #print ("data:" ,data,"sssservicessss" ,services)

        #print(data)

        return render(request, 'set_sri_goal.html', {
            'data': data  # For the SRI score and other info
            #'services': services  # Pass services separately
        })
        
        #return render(request, 'set_sri_goal.html', {'data': data})


    
def upgrade_scenarios(request):
    sri_goal = request.session.get("sri_goal", None)
    data = request.session.get("data", None)
    print(f"SRI GOAL:{sri_goal}")
    print(f"Data:{data}")
    return render(request, 'upgrade_scenarios.html')
    
def error_404(request, exception):
    return render(request, '404.html', status=404)

def error_500(request):
    return render(request, '500.html', status=500)

def custom_error_404(request):
    return render(request, '404.html', status=404)

def about(request):
    return render(request, 'about.html')
