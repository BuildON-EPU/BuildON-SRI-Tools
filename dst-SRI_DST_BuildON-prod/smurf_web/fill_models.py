import csv
from smurf_web_app.models import *
import json
import ast 

def fill_domain_w():
    with open("excel_files/domain_w.csv", 'r') as file:
        csvreader = csv.reader(file)
        for k,data_list in enumerate(csvreader):
            if k > 0:
                domain_weight_instance = DomainWeight(
                                        building_type=data_list[0],
                                        zone=data_list[1],
                                        domain=data_list[2],
                                        dw_cr1=float(data_list[3]),
                                        dw_cr2=float(data_list[4]),
                                        dw_cr3=float(data_list[5]),
                                        dw_cr4=float(data_list[6]),
                                        dw_cr5=float(data_list[7]),
                                        dw_cr6=float(data_list[8]),
                                        dw_cr7=float(data_list[9])
                                                     )
                domain_weight_instance.save()


def fill_impact_w():
    with open("excel_files/impact_w.csv", 'r') as file:
        csvreader = csv.reader(file)
        for k, data_list in enumerate(csvreader):
            if k > 0:
                impact_weight_instance = ImpactWeight(
                                        building_type=data_list[0],
                                        zone=data_list[1],
                                        imp_cr1=float(data_list[2]),
                                        imp_cr2=float(data_list[3]),
                                        imp_cr3=float(data_list[4]),
                                        imp_cr4=float(data_list[5]),
                                        imp_cr5=float(data_list[6]),
                                        imp_cr6=float(data_list[7]),
                                        imp_cr7=float(data_list[8])
                                                     )                                
                impact_weight_instance.save()


def fill_levels():
    with open("excel_files/levels.csv", 'r') as file:
        csvreader = csv.reader(file)
        for k, data_list in enumerate(csvreader):
            if k > 0:
                levels_instance = Levels(
                                        code=data_list[0],
                                        level_desc=data_list[1],
                                        desc=data_list[2],
                                        score_cr1=int(data_list[3]),
                                        score_cr2=int(data_list[4]),
                                        score_cr3=int(data_list[5]),
                                        score_cr4=int(data_list[6]),
                                        score_cr5=int(data_list[7]),
                                        score_cr6=int(data_list[8]),
                                        score_cr7=int(data_list[9]),
                                        level=int(data_list[10]),
                                        mandatory = int(data_list[11]),
                                        domain = data_list[12]
                                    )
                levels_instance.save()



def fill_services():
    with open("excel_files/services.csv", 'r') as file:
        csvreader = csv.reader(file)
        for k, data_list in enumerate(csvreader):
            if k > 0:
                services_instance = Services(
                                        domain=data_list[0],
                                        code=data_list[1],
                                        service_group=data_list[2],
                                        service_desc=data_list[3]
                                            )                                
                services_instance.save()

def fill_costs():
    with open("excel_files/costtechsnew3.csv", 'r') as file:
        csvreader = csv.reader(file)
        
        for k, data_list in enumerate(csvreader):
            print(data_list)
            if k > 0:
                data = ast.literal_eval(data_list[1])
                print(data)
                costs_instance = Costs(
                    name=data_list[0],
                    services =  data_list[1],
                    cost=data_list[2],
                    desc = data_list[3],
                    img = data_list[4],
                    con =  data_list[5]
                )
                costs_instance.save()
                print(f"Cost saved: {costs_instance}")

# Check if any model has existing data
if not (DomainWeight.objects.exists() or \
        ImpactWeight.objects.exists() or \
        Levels.objects.exists() or \
        Services.objects.exists() or \
        Costs.objects.exists()):
    print("Database tables are empty. Proceeding to fill models...")
    fill_domain_w()
    fill_impact_w()
    fill_levels()
    fill_services()
    fill_costs()
else:
    print("One or more database tables contain data. Skipping filling models.")
