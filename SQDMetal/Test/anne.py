from PALACE.Eigenmode_Simulation import PALACE_Eigenmode_Simulation
from SQDMetal.PALACE.SQDGmshRenderer import Palace_Gmsh_Renderer

from qiskit_metal import draw, Dict, designs, MetalGUI
from qiskit_metal.toolbox_metal import math_and_overrides
from qiskit_metal.qlibrary.core import QComponent
import qiskit_metal as metal
# ?metal.qlibrary.core.QComponent.add_qgeometry

design = metal.designs.design_planar.DesignPlanar()
#gui = metal.MetalGUI(design)
design.overwrite_enabled = True

# dir(QComponent)
cpw_width = '11.7um'

design._chips.main.size.size_x = '5mm'
design._chips.main.size.size_y = '5mm'
from qiskit_metal.qlibrary.terminations.launchpad_wb import LaunchpadWirebond
from qiskit_metal.qlibrary.terminations.short_to_ground import ShortToGround
from qiskit_metal.qlibrary.tlines.straight_path import RouteStraight
from qiskit_metal.qlibrary.tlines.anchored_path import RouteAnchors
from qiskit_metal.qlibrary.tlines.mixed_path import RouteMixed
from qiskit_metal.qlibrary.qubits.transmon_cross import TransmonCross
from qiskit_metal.qlibrary.tlines.meandered import RouteMeander
from qiskit_metal.qlibrary.terminations.open_to_ground import OpenToGround
from qiskit_metal.qlibrary.couplers.coupled_line_tee import CoupledLineTee
from qiskit_metal.qlibrary.couplers.cap_n_interdigital_tee import CapNInterdigitalTee
from qiskit_metal.qlibrary.couplers.line_tee import LineTee

from collections import OrderedDict

import numpy as np

xmon1_options = dict(
    connection_pads=dict(
        # a = dict( connector_location = '0', connector_type = '0'),
        # b = dict(connector_location = '90', connector_type = '0'),
        c = dict(connector_location = '90', 
                 connector_type = '0', 
                 claw_length = '215um',
                 ground_spacing = '10um', 
                 claw_gap = '5.1um', 
                 claw_width = '15um',
                 claw_cpw_length = '0um'
                 ),
        # d = dict(connector_location = '270', connector_type = '0'),
    ),
    cross_width = '30um',
    cross_length = '240um',
    cross_gap = '30um',
    orientation = '-90',
    pos_x = '-1500um',
    pos_y = '1200um',
    aedt_hfss_inductance = 9.686E-9
)

# Create a new Transmon Cross object with name 'Q1'
q1 = TransmonCross(design, 'Q1', options=xmon1_options)

otg_options = dict(width = '5.85um', 
                   gap = '5.1um', 
                #    termination_gap = '500um',
                   pos_x='-1200um',  
                   pos_y='1200um', 
                   orientation='180')

otg1 = OpenToGround(design, 'otg1', options=otg_options)


clt1_opts = Dict(prime_width = cpw_width,
                prime_gap = '5.1um',
                second_width = cpw_width,
                second_gap = '5.1um',
                coupling_space = '7.9um',
                coupling_length = '225um',
                open_termination = False,
                orientation = '-90',
                pos_y = '1200um',
                down_length = '50um')

clt1 = CoupledLineTee(design, 'clt1', clt1_opts)

cpw_total_length = 5160 + 716 + 300 + 1881.18568
cpw_total_length = str(cpw_total_length) + 'um'
cpw1_opts = Dict(pin_inputs = Dict(start_pin = Dict(component = 'clt1',
                                                    pin = 'second_end'),
                                   end_pin = Dict(component = 'otg1',
                                                  pin = 'open')),
                lead = Dict(end_straight = '70um',
                            # start_jogged_extension = jogsS),
                ),
                fillet = '49.9um',
                total_length = '3900um',#'3893.8166um', # '6776um',
                trace_width = cpw_width,
                meander = Dict(spacing = '100um',
                               asymmetry = '-150um'),
                trace_gap = '5.1um',)
cpw1 = RouteMeander(design, 'cpw1', options = cpw1_opts)

#Eigenmode Simulation Options
user_defined_options = {
                 "mesh_refinement":  0,                             #refines mesh in PALACE - essetially divides every mesh element in half
                 "dielectric_material": "silicon",                  #choose dielectric material - 'silicon' or 'sapphire'
                 "starting_freq": 7.5,                              #starting frequency in GHz 
                 "number_of_freqs": 4,                              #number of eigenmodes to find
                 "solns_to_save": 4,                                #number of electromagnetic field visualizations to save
                 "solver_order": 2,                                 #increasing solver order increases accuracy of simulation, but significantly increases sim time
                 "solver_tol": 1.0e-8,                              #error residual tolerance foriterative solver
                 "solver_maxits": 100,                              #number of solver iterations
                 "comsol_meshing": "Extremely fine",                #level of COMSOL meshing: 'Extremely fine', 'Extra fine', 'Finer', 'Fine', 'Normal'
                 "mesh_max": 120e-3,                                #maxiumum element size for the mesh in mm
                 "mesh_min": 10e-3,                                 #minimum element size for the mesh in mm
                 "mesh_sampling": 130,                              #number of points to mesh along a geometry
                 "sim_memory": '300G',                              #amount of memory for each HPC node i.e. 4 nodes x 300 GB = 1.2 TB
                 "sim_time": '20:00:00',                            #allocated time for simulation 
                 "HPC_nodes": '4',                                  #number of Bunya nodes. By default 20 cpus per node are selected, then total cores = 20 x HPC_nodes
                }

#Creat the Palace Eigenmode simulation
eigen_sim = PALACE_Eigenmode_Simulation(name ='single_resonator_example_eigen',                     #name of simulation
                                        metal_design = design,                                      #feed in qiskit metal design
                                        sim_parent_directory = "/project/shaas_31/acwhelan",            #choose directory where mesh file, config file and HPC batch file will be saved
                                        mode = 'HPC',                                               #choose simulation mode 'HPC' or 'simPC'                                          
                                        meshing = 'GMSH',                                           #choose meshing 'GMSH' or 'COMSOL'
                                        user_options = user_defined_options,                        #provide options chosen above
                                        view_design_gmsh_gui = False,                               #view design in GMSH gui 
                                        create_files = True)                                        #create mesh, config and HPC batch files
eigen_sim.add_metallic(1)
eigen_sim.add_ground_plane()
#eigen_sim.create_port_CPW_on_Launcher('LP1', 20e-3)
#eigen_sim.create_port_CPW_on_Launcher('LP2', 20e-3)
eigen_sim.prepare_simulation()