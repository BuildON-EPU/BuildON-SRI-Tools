import json
from .models import *
from django.db.models import *
from django.db.models import Sum, Max, F, Q, IntegerField
from django.db.models.functions import Coalesce
from django.db.models import Subquery, OuterRef
import re
import pandas as pd
import ast
from itertools import combinations, product, chain

final_total_SR_cur_list = []  # Initialize as an empty list globally
Imax_d_ic = {}
I_d_ic = {}
SR_f_d_total_cur ={}
impact_w = []
    
def fetch_costs_table():
    # Use .values() to retrieve specific fields, not the whole model instance
    costs_data = Costs.objects.values('name', 'services', 'cost','desc','img', 'con')
    
    df = pd.DataFrame(costs_data) 
    
    df['services'] = df['services'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
     
    # Check if 'cost' exists in columns
    if 'cost' in df.columns:
       
        df['cost'] = pd.to_numeric(df['cost'], errors='coerce')
        df = df.sort_values(by='cost', ascending=True).reset_index(drop=True)
    else:
        print("The 'cost' column is missing from the DataFrame columns:", df.columns)
    #print("DataFrame Preview:\n", df.head())
      # To verify structure
    #print("DOMAINNNNNNNNNNNNNNNN====================",domain)  
    for index, row in df.iterrows():
        servicesnew = row['services']
        
        # Iterate through each service in the services list
        for service in servicesnew:
            service_name = service.get('service')
            
            # Fetch the domain for each service from the Services model
            if service_name:
                try:
                    service_obj = Services.objects.get(code=service_name)  # Assuming 'name' links to Services
                    service_domain = service_obj.domain  # Get the domain from the Services model
                except Services.DoesNotExist:
                    service_domain = None  # In case the service is not found
            
                # Add the domain to the service dictionary
                service['domain'] = service_domain  # Add domain to the service
            
        # After updating the services, we update the row in the DataFrame
        df.at[index, 'services'] = servicesnew    
    return df
#df = fetch_costs_table()


def find_greatest_levels(df):
    domain_max_levels = {}

    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        services = row['Services']
        
        # Iterate through the list of services for each row
        for service in services:
            domain = service.get('domain')
            level = service.get('service')  # Assuming 'service' represents the level

            # Update the max level for the domain
            if domain in domain_max_levels:
                if level > domain_max_levels[domain]:
                    domain_max_levels[domain] = level
            else:
                domain_max_levels[domain] = level

    return domain_max_levels


# Function to calculate SR values based on input data and goal SRI
def calculate_SR(input_data, goal_sri):
    results = {}  # Dictionary to store the results
    criteria_num = 7 # Number of criteria
    # Dictionary to store services for each domain
    domain_services = {}

    # Wrap the transformed data under the 'data' key
    input_data = {
         "data": [input_data]
    }
    
    for user_data in input_data['data']:
        user = user_data.get('user', None)
        input_sri = user_data['input_sri']
        building_type = user_data['building_type']
        zone = user_data['zone']
        services = user_data['services']

        user_results = {}  # Dictionary to store the results for the user

        # Calculate the denominator A for the fraction d of the methodology
        A = []  # Initialize an empty array to store the results
        for service_data in services:
           
            #service = service_data['service']
            service = service_data['service_code']
            domain = service_data['domain']
            level = service_data['level']

            # Execute a query to count the number of levels of each service
            result = Levels.objects.filter(code=service).count()

            # Get the value for the maximum level of each service
            max_level = result -1

            # Check if the domain is already in the dictionary
            if domain not in domain_services:
                domain_services[domain] = []

            # Append the service to the list of services for each domain
            domain_services[domain].append(service)
       
        #### Initialize a dictionary to store Imax_d_ic, I_d_ic for each domain
        global Imax_d_ic , I_d_ic
        Imax_d_ic = {}
        I_d_ic = {}
        srplus=[]

        #### Initialize a dictionary to store SR_d_ic values for each domain
        SR_d_ic_domain = {}
        #### Initialize a dictionary to store total scores for each domain and criterion
        total_scores_per_domain = {}
 
        # Iterate over domains and run the query for each domain
        for domain, services_for_domain in domain_services.items():
            #### Initialize the sum of A values for the current domain to 0
            sum_Imax_d_ic = [0] * criteria_num  # List to store sum of max_score_k for each criterion in domain
            sum_I_d_ic = [0] * criteria_num  # List to store sum of score_k for each criterion in domain
            
            #### Initialize a list to store SR_d_ic values for the current domain
            SR_d_ic_list = [0] * criteria_num
            ### Initialize the total scores for the current domain
            total_scores = {
            'score_cr1': 0,
            'score_cr2': 0,
            'score_cr3': 0,
            'score_cr4': 0,
            'score_cr5': 0,
            'score_cr6': 0,
            'score_cr7': 0,
            }

            # Construct the subquery to get the maximum level for each service
            max_level_subquery = Levels.objects.filter(
                code=OuterRef('code')
                
            ).values('code').annotate(
                max_level=Max('level')
            ).values('max_level')[:1]

            services_max_levels = Services.objects.annotate(
            max_level=Subquery(max_level_subquery)
            ).values('code', 'max_level')

            max_scores_dom = Levels.objects.filter(
                Q(domain=domain) &
                Q(level=Coalesce(Subquery(max_level_subquery), F('level'))) &
                (Q(mandatory=1) | Q(code__in=services_for_domain))
            ).values(
                'domain'
            ).annotate(
                sum_score_cr1=Sum('score_cr1'),
                sum_score_cr2=Sum('score_cr2'),
                sum_score_cr3=Sum('score_cr3'),
                sum_score_cr4=Sum('score_cr4'),
                sum_score_cr5=Sum('score_cr5'),
                sum_score_cr6=Sum('score_cr6'),
                sum_score_cr7=Sum('score_cr7')
            ).order_by('domain')

            # Extracting sums from the queryset ( Imax (d,ic))
            max_scores = [
                max_scores_dom[0]['sum_score_cr1'],
                max_scores_dom[0]['sum_score_cr2'],
                max_scores_dom[0]['sum_score_cr3'],
                max_scores_dom[0]['sum_score_cr4'],
                max_scores_dom[0]['sum_score_cr5'],
                max_scores_dom[0]['sum_score_cr6'],
                max_scores_dom[0]['sum_score_cr7']
            ]
            max_scores = [float(item) for item in max_scores]
            ####
            #print("Mmax_scores:", domain, max_scores)

            if max_scores is None:
                continue  # Skip the calculation if data for the current level and service is not found

            # Execute a query to get the weights for each domain
            q_weights_d = DomainWeight.objects.filter(building_type=building_type, zone=zone, domain=domain)
            #print(q_weights_d)
            l_weights_d = q_weights_d.values_list('dw_cr1', 'dw_cr2', 'dw_cr3', 'dw_cr4', 'dw_cr5', 'dw_cr6', 'dw_cr7')
            #print(l_weights_d)

            # Convert the QuerySet to a list
            weights_d = list(l_weights_d[0])

            if weights_d is None:
                continue  # Skip the calculation if data is not found

            # For each criteria
            for k in range(0, criteria_num):
                # Loop through the elements of weights_d and max_scores and 
                # Multiply the weights of each critetion to max scores of each criterion
                weight_d = float(weights_d[k])  # Convert decimal to float
                max_score_k = float(max_scores[k])  # Convert decimal to float
                A.append(weight_d * max_score_k)
                ####Imax_d_ic
                ##Imax_d_ic.append(max_score_k)
                sum_Imax_d_ic[k] += max_score_k  # Accumulate the score for each criterion

            #### Store the sum of max_score_k values for each criterion in the dictionary for the current domain
            Imax_d_ic[domain] = sum_Imax_d_ic

        total_impact_cur_list = []  # List to store total SR_cur values for all services
        total_SR_cur_list = []  # List to store SR_cur values for each service
        
        # Calculate the percentage of the SRI gain for each level upgrade
        services_level={} # Dictionary to store service levels
        pre_domain = ""
       
        for service_data in services:
            #service = service_data['service']
            service = service_data['service_code']
            domain = service_data['domain']
            level = service_data['level']

            # Get the weight scoce per domain for each criteria
            weights = DomainWeight.objects.filter(building_type=building_type, zone=zone, domain=domain).values('dw_cr1', 'dw_cr2', 'dw_cr3', 'dw_cr4', 'dw_cr5', 'dw_cr6', 'dw_cr7').first()
            weights = list(weights.values())

            if weights is None:
                continue  # Skip the calculation if data for the current level and service is not found

            # Get the impact scoce for each criteria
            global impact_w
            impact_w = ImpactWeight.objects.values('imp_cr1', 'imp_cr2', 'imp_cr3', 'imp_cr4', 'imp_cr5', 'imp_cr6', 'imp_cr7').first()
            impact_w = list(impact_w.values())

            # Count the number of levels
            result = Levels.objects.filter(code=service).count()

            # Get the count value from the result
            max_level = result-1
            services_level[service]=[level,max_level]

            # Fetch the values for the current level
            current_scores = Levels.objects.filter(code=service, level=level).values('score_cr1', 'score_cr2', 'score_cr3', 'score_cr4', 'score_cr5', 'score_cr6', 'score_cr7').first()
            current_scores = list(current_scores.values())
            #print(f"Service:{service} Curr Score:{current_scores}")

            if current_scores is None:
                continue  # Skip the calculation if data for the current level and service is not found
        
            SR_ic_cur = [] # list to store impact SR values

            if domain != pre_domain:
                #### Initialize the sum of values for the current domain to 0
                sum_I_d_ic = [0] * criteria_num  # List to store sum of score_k for each criterion in domain
                #sum_I_d_ic_up = [0] * criteria_num  # List to store sum of score_k for each criterion in domain

            i = level 

            if i == level: 
                scores_cur = Levels.objects.filter(code=service, level=i).values('score_cr1', 'score_cr2', 'score_cr3', 'score_cr4', 'score_cr5', 'score_cr6', 'score_cr7').first()
                scores_cur = list(scores_cur.values())
                #print(f"Service:{service} level:{level} Scores:{scores_cur}")

                if scores_cur is None:
                    continue  # Skip the calculation if data for the current level is not found 

                # Initialize the list to store SR_cur values for the current service
                SR_cur_list = [0] * criteria_num
               
                for k in range(0, criteria_num): 
                    # Calculate SR_ic gain (fraction d)
                    if sum(A[k::7]) != 0:
                        SR_cur = (weights[k] * (current_scores[k]) * 100) / sum(A[k::7])
                    else:
                        SR_cur = 0 

                    ####I_d_ic
                    sum_I_d_ic[k] += current_scores[k]  # Accumulate the score for each criterion

                    #### Store the sum of score_k values for each criterion in the dictionary for the current domain
                    I_d_ic[domain] = sum_I_d_ic 
                    #print("I_d_c", I_d_ic)
                    pre_domain = domain

                    SR_cur_list[k] += SR_cur                 
      
            #Append the list of SR_cur values for the current service to the total list
            total_SR_cur_list.append(SR_cur_list)
            #print("Τotal_SR_cur_list ", service, total_SR_cur_list)
           
            SR_values = []  # List to store the SR values for the current service
            SR_ic = [] # list to store impact SR values
            I_d_ic_up = [] 

            for i in range(level+1, max_level+1):  # Calculate SR1, SR2, SR3, ... until max(level)
                scores = Levels.objects.filter(code=service, level=i).values('score_cr1', 'score_cr2', 'score_cr3', 'score_cr4', 'score_cr5', 'score_cr6', 'score_cr7').first()
                scores = list(scores.values())
                #print(f"Service:{service} Scores:{scores}")

                if scores is None:
                    continue  # Skip the calculation if data for the current level is not found 

                SR_f = 0
                SR_icc = []  # list to store impact SR values for each impact criterion
                #I_d_ic_up = [] # # list to store impact values for each impact criterion

                # Reset I_d_ic_up_diff for each level iteration
                I_d_ic_up_diff = [0] * criteria_num

                for k in range(0, criteria_num): 
                    next_level_score = scores[k]
                    # Calculate SR_ic gain (fraction d)
                    if sum(A[k::7]) != 0:
                        SR = (weights[k] * (next_level_score - current_scores[k]) * 100) / sum(A[k::7])
                    else:
                        SR = 0 
                    # Append the calculated SR value to the impact score list
                    SR_icc.append(SR)           

                    # Calculate SR_f gain (fraction e)
                    SR_f += SR * impact_w[k]

                    #######################################################    
                    ####I_d_ic_up
                    I_d_ic_up_diff[k] += next_level_score - current_scores[k]  # Accumulate the score for each criterion

                SR_values.append(SR_f)
                
                SR_ic.append(SR_icc)  # Append the list of impact SR values for each impact criterion 
                I_d_ic_up.append(I_d_ic_up_diff)
   
            # Append the sum_I_d_ic_up list to SR_values
            SR_values.append(I_d_ic_up)
            SR_values.append(SR_ic) 

            ###print("SSSSSSSSSSSSSSSSSSSSR_ic",SR_values)

            user_results[service] = SR_values

        # Calculate SR_d_ic - table detail scores - SRd,ic​=I(d,ic)x100/Imax(d,ic)​
        SR_d_ic = {}
        for domain in I_d_ic:
            SR_d_ic[domain] = []
            for i in range(len(I_d_ic[domain])):
                if Imax_d_ic[domain][i] != 0:
                    SR_value = (I_d_ic[domain][i] * 100) / Imax_d_ic[domain][i]
                else:
                    SR_value = 0  # Avoid division by zero
                SR_d_ic[domain].append(SR_value)

        # Calculate SR_f,d using the formula SR_f,d = W_f(ic) × SR_d,ic
        SR_f_d = {}
        for domain, scores in SR_d_ic.items():
            SR_f_d[domain] = []
            for i in range(len(scores)):
                SR_f_value = impact_w[i] * scores[i]
                SR_f_d[domain].append(SR_f_value)

        # Calculate SR_f,d using the formula SR_f,d = W_f(ic) × SR_d,ic / sum(W_f(ic)) with the given condition
        #  that if Imaxd,ic[i]=0Imaxd,ic​[i]=0 then Wf(ic)=0Wf​(ic)=0
        global SR_f_d_total_cur
        SR_f_d_total_cur = {}
        for domain, scores in SR_d_ic.items():
            weighted_sum = 0
            weight_sum = 0
            for i in range(len(scores)):
                weight = impact_w[i] if Imax_d_ic[domain][i] != 0 else 0
                weighted_sum += weight * scores[i]
                weight_sum += weight
            if weight_sum != 0:
                SR_f_total = weighted_sum / weight_sum
            else:
                SR_f_total = 0  # Avoid division by zero
            SR_f_d_total_cur[domain] = SR_f_total

        global final_total_SR_cur_list  # Declare final_total_SR_cur_list as a global variable
        final_total_SR_cur_list = [sum(values) for values in zip(*total_SR_cur_list)]
        #print("final_total_SR_cur_list:", final_total_SR_cur_list) 

        user_results = foo(services_level, user_results, input_sri, goal_sri)     
        results[user]=user_results  
    
    final_result1 = calculate_sri_scenario(results)
    #print("Final Result 1:", final_result1)
    final_result = sorted(final_result1, key=lambda x: x['Total_SRI_gain'], reverse=False)
    # Update the "Scenario" field with sequential numbers
    counter_success=1
    counter_failure=1
    for i, item in enumerate(final_result, start=1):        
        final_result[i-1]["Scenario"] = i
        if final_result[i-1]["Total_SRI_gain"] >= goal_sri:
            final_result[i-1]["sc_index"] = counter_success
            counter_success += 1
        else:
            final_result[i-1]["sc_index"] = counter_failure
            counter_failure += 1

    return final_result

# Function to transform the results into a specific JSON format
def foo(levels, res, input_sri, goal_sri):
    d = {}
    # Include the input_sri in the JSON output  
    d['input_sri'] = input_sri
    d['goal_sri'] = goal_sri 
    for service in levels:
        start_level = levels[service][0]
        max_level = levels[service][1]
        temp = {}
        temp[f"current_level"]=start_level
        d[service]=temp
        for k,l in enumerate(range(start_level+1,max_level+1)):
                temp[f"level_{l}"]=res[service][k]
                # Include the sr_ic list for each level in the temporary dictionary
                temp[f"sr_ic_level_{l}"] = res[service][-1][k] 
                # Include the I_d_ic_up list for each level in the temporary dictionary
                temp[f"I_d_ic_up_level_{l}"] = res[service][-2][k]  # Assuming I_d_ic_up is stored in the same structure as sr_ic_level  
        d[service]= temp  
    return d

# Function to calculate SRI scenarios based on input data
def calculate_sri_scenario(data):

    global final_total_SR_cur_list , Imax_d_ic, I_d_ic ,SR_f_d_total_cur, impact_w # Access the global variable
    key_f = []

    result_data = [] # List to store the resulting scenario data
    #print(type(data)) 
    user_name = list(data.keys())[0] # Get the user's name from the data dictionary
    user_data = data[user_name] # Extract the user's data
    sri = user_data['input_sri'] # Get the user's initial SRI value
    goal_sri = user_data['goal_sri'] # Get the user's goal SRI value
    #print("input_sri:", sri)
    #print("goal_sri:", goal_sri)
    # Pop the SRI values from the user's data dictionary
    sri_value = user_data.pop("input_sri")
    sri_goal = user_data.pop("goal_sri")
    services = [] # List to store the user's services and their levels
    serv2=[]
    serv3={}
    
    # Extract service names and their levels from the user's data
    for service_name, service_levels in user_data.items():
        service = {
            "service": service_name
        }
        service.update(service_levels)
        services.append(service)
        serv2.append(service_name)
        serv3[service_name] = service_levels
    
    levels = ["level_1", "level_2", "level_3", "level_4"] # List of upgrade levels
    
    
    sorted_values = [[] for _ in range(len(levels))] # List to store sorted service values at each level
    # Sort services at each level based on their values in descending order
    for level_idx, level in enumerate(levels):
       
        sorted_values[level_idx] = sorted([(service.get(level, 0), service.get("service"), service.get("current_level")) for service in services], reverse=True)
  
    counter = 0 # Counter for scenario numbering
    new_counter = 1 # Counter for scenario success/failure numbering
    success_counter = 1
   
    df =  fetch_costs_table()   
    print(df.columns)
    techs={}
    techs2={}
    for _, row  in df.iterrows():
        namenew = row['name']
        servicesnew = row['services']
        costnew = row['cost']
        desc2=row["desc"]
        img = row["img"]
        con = row["con"]
     
        for ij in servicesnew:
            if ij['service'] in serv2:
                if  ij['level'] > serv3[ij['service']].get('current_level'):
                    if namenew not in techs:
                        techs[namenew] = []
                        techs2[namenew] = (costnew,desc2,img, con)

                    for kl in sorted_values[ij['level']-1]:
                        if kl[1] == ij['service']:
                            value= kl[0]
                    techs[namenew].append((value, ij['service'], serv3[ij['service']].get('current_level'),ij['level'],namenew))
    
    maxsuc =30
    techsnew =techs
    keys = sorted(
        techsnew.keys(),
        key=lambda k: sum(entry[0] for entry in techsnew[k]),
        reverse=True
    )

    alltechs = {}
    success_count = 0

    for r in range(1, 5):  # Start with subsets of size 1
        for subset in combinations(keys, r):  
            common_services = set()
            """for key in subset:
                for entry in techsnew[key]:
                    service = entry[1]
                    common_services.add(service)

            # Skip this subset if it has more than 3 services in common
            if len(common_services) > 5 and r>1 :
                continue  # Skip further processing for this subset
"""
            # Combine services
            combined_services = {}
            
            for key in subset:
                for entry in techsnew[key]:
                    score, service, *rest, level,tech = entry
                    if service in combined_services:
                        # Keep only the entry with the highest level
                        existing_entry = combined_services[service]
                        
                        _, _, *_, existing_level,tech = existing_entry

                        if level > existing_level:
                            combined_services[service] = entry
                        else: 
                            combined_services[service] = existing_entry
                    else:
                        # Add new entry
                        combined_services[service] = [score, service, *rest, level,tech]
            
            # Calculate total score
            total_score = sri + sum(entry[0] for entry in combined_services.values())
           
            if total_score >= goal_sri:
                success_count += 1
                alltechs[tuple(sorted(subset))] = (list(combined_services.values()))
            if success_count >= maxsuc:
                break
            
        # Early exit
        if success_count >= maxsuc:
            break
    unique_alltechs = {}

    # Track services and their associated keys to identify overlaps
    services_to_keys = {}

    for key, value in alltechs.items():
        combined_services = value

        # Create a unique identifier for services
        services_set = frozenset(service[1] for service in combined_services)

        # If the services_set already exists, check for common technologies
        if services_set in services_to_keys:
            existing_key = services_to_keys[services_set]
            
            # Check for overlapping technologies
            if any(tech in existing_key for tech in key):
                # Skip adding this entry, keeping the first one encountered
                continue
        else:
            # Add the services set to the mapping
            services_to_keys[services_set] = key
            unique_alltechs[key] = combined_services
     
    for  techs1 in unique_alltechs:
        scenario_data = {
                "Scenario": counter,
                "new_counter": new_counter,
                "input_sri": sri,
                "goal_sri": goal_sri,
                "Services": [], 
            }
        tech22={}
        teco ={}
        tech=[]
        costs=[]
        imgs=[]
        descs=[]
        cons = []
        sri_gain=0
        for techname in techs1:
            
            sr_ic_level_total = [0.0] * 7
            SR_domain_total = SR_f_d_total_cur.copy()  # Initialize SR_domain_total with the current SR_f_d_total_cur
            counter += 1
            cost,desc,imge, con = techs2[techname]
            con = float(con)
            tech22[techname] = (cost,desc,imge, con)
            costs.append(cost)
            descs.append(desc)
            imgs.append(imge)
            tech.append(techname)
            cons.append(con) 
        for i in range(len(alltechs[techs1])):
            #print(len(alltechs[techs1]))
           # sr_ic_level_total = [0.0] * 7
            #SR_domain_total = SR_f_d_total_cur.copy()  # Initialize SR_domain_total with the current SR_f_d_total_cur

            max_value, max_service, max_current_level,level_num,techname1 = alltechs[techs1][i]
               
            sri_gain += max_value
            
            used_services = [max_service] # List to track used services in the scenario
            # Select info to update scenarios
            # Fetch the values for the current level
            cur_functionality = Levels.objects.filter(code=max_service, level=max_current_level).values('desc').first()

            if cur_functionality is None:
                continue  # Skip 

            up_functionality = Levels.objects.filter(code=max_service, level=level_num).values('desc').first()

            if up_functionality is None:
                continue  # Skip 

            service_info = Services.objects.filter(code=max_service).values('domain', 'service_desc').first()
            
            if service_info:
                domain, service_desc = list(service_info.values())

            # Extract SR_ic_level_i values from user_data
            sr_ic_values = user_data.get(f"{max_service}", {}).get(f"sr_ic_level_{level_num}", [])
            I_d_ic_diff = user_data.get(max_service, {}).get(f"I_d_ic_up_level_{level_num}", [])
            #print("xxxxxxxxxxxxxxxxxx",I_d_ic_diff)
            
            domain_s = domain
            I_d_ic_new = {}  # Initialize an empty dictionary for the new I_d_ic values

            for domain, values in I_d_ic.items():
                if domain == domain_s:
                    # Update the corresponding list in the I_d_ic_new dictionary
                    I_d_ic_new[domain] = [x + y for x, y in zip(values, I_d_ic_diff)]

            # Calculate SR_d_ic - table detail scores - SRd,ic​=I(d,ic)x100/Imax(d,ic)​
            SR_d_ic_new = {}
            for domain in I_d_ic_new:
                SR_d_ic_new[domain] = []
                for i in range(len(I_d_ic_new[domain])):
                    if Imax_d_ic[domain][i] != 0:
                        SR_value = (I_d_ic_new[domain][i] * 100) / Imax_d_ic[domain][i]
                    else:
                        SR_value = 0  # Avoid division by zero
                    SR_d_ic_new[domain].append(SR_value)
            
            SR_f_d_total_new = {}
            for domain, scores in SR_d_ic_new.items():
                weighted_sum = 0
                weight_sum = 0
                for i in range(len(scores)):
                    weight = impact_w[i] if Imax_d_ic[domain][i] != 0 else 0
                    weighted_sum += weight * scores[i]
                    weight_sum += weight
                if weight_sum != 0:
                    SR_f_total = weighted_sum / weight_sum
                else:
                    SR_f_total = 0  # Avoid division by zero
                SR_f_d_total_new[domain] = SR_f_total

            SR_f_d_service_diff = {}
            for domain, value_new in SR_f_d_total_new.items():
                if value_new != 0:
                    value_old = SR_f_d_total_cur.get(domain, 0)
                    diff = value_new - value_old
                    SR_f_d_service_diff[domain] = diff

            SR_domain_total = {domain: total + SR_f_d_service_diff.get(domain, 0) for domain, total in SR_domain_total.items()}
            #print("New SR_f_d_total:", SR_domain_total)

            sr_ic_values = user_data.get(f"{max_service}", {}).get(f"sr_ic_level_{level_num}", [])
            # Calculate SR_ic_level_total and add it to the entry dictionary
            
            sr_ic_level_total = [sum(x) for x in zip(sr_ic_level_total, sr_ic_values)] 
            sr_ic_level_total_with_final = [sum(x) for x in zip(sr_ic_level_total, final_total_SR_cur_list)]
            print( user_data.get(f"{max_service}"))
            # Create the key_f list 
            if len(sr_ic_level_total_with_final) == 7: 
                key_f = [
                    (sr_ic_level_total_with_final[0] + sr_ic_level_total_with_final[5]) * 0.5,
                    (sr_ic_level_total_with_final[2] + sr_ic_level_total_with_final[3] + sr_ic_level_total_with_final[4] + sr_ic_level_total_with_final[6]) * 0.25,
                    sr_ic_level_total_with_final[1]
                ]
            print("KKKKKKKKey_f", key_f)
                        
            cost1,desc1,imge1, con = techs2[techname1]
            con = float(con)
            entry = {
                "Service": max_service,
                "Service_description": service_desc,
                "Domain": domain,
                "Current_level": max_current_level,
                "Current_functionality": cur_functionality,
                "Upgrade_level": level_num,
                "Upgrade_functionality": up_functionality,
                "SR_ic_level_i": sr_ic_values if sr_ic_values is not None and any(sr_ic_values) else [0.0] * 7,  # Include zeros
                "SR_domain_diff":SR_f_d_service_diff,
                "SRI_gain": max_value,
                "serte" : (techname1,cost1,desc1,imge1, con),
                'Tech' :techname1,
                'Cost': cost1,
                'desc' :desc1,
                'img' : imge1,
                'con': con
            }

            scenario_data["Services"].append(entry)
        
        scenario_data["Techs"] = tech22
        #scenario_data["paird"]: 
        scenario_data["Costs"] = costs
        scenario_data["descs"] = descs
        scenario_data["Img"] = imgs
        scenario_data["tech"] = tech
        
        totalcost = sum(costs)
        totalcon = sum(cons)
        totalcon = totalcon*0.2

        scenario_data["Total_SRI_gain"] = sri_gain + sri
        

        
        scenario_data["sri_gain"] = sri_gain
        
        if sri_gain>0:
         ce = totalcost/sri_gain
        else:
            ce =0
        scenario_data["TotalCost"] = totalcost
        scenario_data["CE"] = ce
        scenario_data["TotalCarbon"] = totalcon
        # Update scenario result based on SRI gain meeting the goal or not
        if sri_gain >= goal_sri - sri:
            scenario_data["result_scenario"] = "Success!"
            scenario_data["new_counter"] = success_counter
            scenario_data["SR_ic_level_total"] = sr_ic_level_total
            scenario_data["SR_ic_level_total_FINAL"] = sr_ic_level_total_with_final
            scenario_data["SR_domain_total_cur"] = SR_f_d_total_cur
            scenario_data["SR_domain_total_new"] = SR_domain_total 
            scenario_data["KEY_F"] = key_f
            #print(key_f)
            # Remove "SR_ic_level_total" from the individual services
            for service_entry in scenario_data["Services"]:
                service_entry.pop("SR_ic_level_total", None)
            
            result_data.append(scenario_data)
            success_counter += 1
       
    
    return result_data



# Example usage
input_data = [
    {
        'user': 'user1',
        'input_sri': 40,
        'building_type': 'Residential',
        'zone': 'North Europe', 
        'services': [
           {'service': 'H-1a', 'level': 0, 'domain': 'Heating'},
            {'service': 'H-1b', 'level': 2, 'domain': 'Heating'},
           {'service': 'DHW-1a', 'level': 1, 'domain': 'Domestic hot water'},
            {'service': 'C-1a', 'level': 1, 'domain': 'Cooling'},
            {'service': 'L-2', 'level': 0, 'domain': 'Lighting'}
        ]
    }    
]
