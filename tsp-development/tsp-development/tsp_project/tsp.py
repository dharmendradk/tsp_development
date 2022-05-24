from statistics import mode
import math
from django.forms import NullBooleanField
from itsdangerous import NoneAlgorithm
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from flask import Flask, send_from_directory, render_template
from flask import request
from pyparsing import null_debug_action
import requests
 
app = Flask(__name__)

@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/api')
def abc():
  global cord,cordStr
  cord=request.args.get('loc')[:-1]
  cordStr=convCords(cord)
  # #print(type(cord))
  main_func() 
  # #print(cord)
  return {'cord':cord}


@app.route('/result')
def xyz():
  # data=request.args.get('data')
  # #print(data)
  return render_template('result.html')

def convCords(crd):
  new_crd=list(crd.split(";"))
  return new_crd

def createNewCords(route):
  temp=""
  for i in route:
    temp+=cordStr[int(i)]+";"
  #print("ooooo",temp)
  cord=temp
  
#floors every value in the datamatrix   
def refineDataMatrix(dataMat):
    n=len(dataMat)
    for i in range(n):
        temp=[]
        for j in dataMat[i]:
            temp.append(math.floor(j))
        dataMat[i]=temp
    # print(dataMat)
    return dataMat  

def findDistMatrix(mode="driving"):
  URL = "https://api.mapbox.com/directions-matrix/v1/mapbox/driving/"+cord+"?access_token=pk.eyJ1Ijoia3VzaDc4IiwiYSI6ImNsMzVqZHF3djBmMWMza3A1c2MzY3Y1NjkifQ.-PI6HfCVSnQVi5MguiQISQ"

  # sending get request and saving the response as response object
  r = requests.get(url = URL) 
  
  # extracting data in json format
  data = r.json()
  print(data['distances'])
  return data['distances']

# def routrFinder(disMatrix):

def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data['distance_matrix'] = refineDataMatrix(findDistMatrix())  # yapf: disable
    data['num_vehicles'] = 1
    data['depot'] = 0
    print("data=",data)
    return data


def print_solution(manager, routing, solution):
    """#prints solution on console."""
    # #print('Objective: {} miles'.format(solution.ObjectiveValue()))
    index = routing.Start(0)
    plan_output = ''
    route_distance = 0
    while not routing.IsEnd(index):
        plan_output += '{}'.format(manager.IndexToNode(index))
        previous_index = index
        index = solution.Value(routing.NextVar(index))
        route_distance += routing.GetArcCostForVehicle(previous_index, index, 0)

    plan_output += '{}'.format(manager.IndexToNode(index))
    createNewCords(plan_output)    
    # print(plan_output)
    plan_output += 'Route distance: {}miles\n'.format(route_distance)
    #print(plan_output)


def main_func():
    """Entry point of the program."""
    # Instantiate the data problem.
    data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)
    
    def distance_callback(from_index, to_index):
        # #print("routing",routing)
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)
    print(routing)
    # #print solution on console.
    if solution:
        print_solution(manager, routing, solution)

if __name__ == '__main__':
  app.run(debug=True)