"""
ASD2VTK version 2.0
Rajgowrav Cheenikundil, Orebro University, Sweden. 

( visit https://github.com/karpathyan/ASD2VTK/ for instructions and help )  

License: GNU Affero General Public License version 3.0 (GNU AGPLv3)
SPDX-License-Identifier: AGPL-3.0

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/agpl-3.0.html>

written: 20/06/2023

* Python script to read the data from the restart
file and to create a VTU file, UnstructuredGrid 
* Usage: run  this code in the directory which contains the
restart.*.out and coord.*.out files
* Make sure there are only ONE restart and coord files in
the running directory
* Number of points in the VTU file will be 8 times the number of atoms
  as 8 points are needed for each cube

Version 1.1 : 11/Aug/2023
* Added the option to plot the dynamics by reading the data from moment.*.out file
* TODO: right now, the entire line in the moment/restart file is passed to the "CreateVTU"
  function, which is un-necesary. we need only the X,Y,Z components. Edit the function for this. 

Version 2.0 : 13/Nov/2023
* (done) TODO: right now, the entire line in the moment/restart file is passed to the "CreateVTU"
  function, which is un-necesary. we need only the X,Y,Z components. Edit the function for this. 
* Added an argparse to read the filename and sourcetool name
 example $ python ASD2VTK.py moment.fcc.out uppasd

* Made the code more flexible for improvements 

version 3.0: 17/Nov/2023
* Introduced parallel process, the code is 5 times faster now.
"""


import vtk, glob
import numpy as np
import argparse, os
from multiprocessing import Pool
import time as tm

dx = 0.5
dy = 0.5


def get_args():
    parser = argparse.ArgumentParser(description='Process command line arguments.')
    parser.add_argument('--filename', default='restart.bcc_Fe_T.out', help='Name of the file')
    parser.add_argument('--toolname', default='uppasd', help='Name of the tool')
    # Parse the arguments
    args = parser.parse_args()
    return str(args.filename), str(args.toolname).lower()

def get_args_pos():
    """get arguments by position, no flags"""
    # Create the parser
    parser = argparse.ArgumentParser(description='Process command line arguments.')
    parser.add_argument('filename', nargs='?', default='restart.bcc_Fe_T.out', help='Name of the file')
    parser.add_argument('toolname', nargs='?', default='uppasd', help='Name of the tool')
    # Parse the arguments
    args = parser.parse_args()
    return args.filename, args.toolname


def get8pnts(pp):
    px, py, pz = pp[0], pp[1], pp[2]
    pnts = []
    for dz in [0, 1]:
        for dy in [0, 1]:
            for dx in [0, 1]:
                my_p = [px+dx-0.5, py+dy-0.5, pz+dz-0.5]
                pnts.append(my_p)
    # Reorder points to match vtkHexahedron's expectations
    pnts = [pnts[i] for i in [0, 1, 3, 2, 4, 5, 7, 6]]
    return pnts


def create_vtu_file (cord_data, field_data, out_filename):
    cord_file = cord_data
    mag_file = field_data

    my_vtk_dataset = vtk.vtkUnstructuredGrid()
    points = vtk.vtkPoints()
    cell = vtk.vtkHexahedron()

    id = 0
    my_vtk_dataset.Allocate(len(cord_file)*8)
    for ln in cord_file:
                pnts = get8pnts([ln[1],ln[2],ln[3]])
                point_ids = []
                for myp in pnts:
                    points.InsertPoint(id, myp)
                    point_ids.append(id)
                    id +=1
                # Setting 8 points for each cube
                cell.GetPointIds().SetId(0, point_ids[0])
                cell.GetPointIds().SetId(1, point_ids[1])
                cell.GetPointIds().SetId(2, point_ids[2])
                cell.GetPointIds().SetId(3, point_ids[3])
                cell.GetPointIds().SetId(4, point_ids[4])
                cell.GetPointIds().SetId(5, point_ids[5])
                cell.GetPointIds().SetId(6, point_ids[6])
                cell.GetPointIds().SetId(7, point_ids[7])
                # vtk.VTK_HEXAHEDRON means cube
                my_vtk_dataset.InsertNextCell(vtk.VTK_HEXAHEDRON, cell.GetPointIds())
            
    my_vtk_dataset.SetPoints(points)

    #print ('length of restart_file = ', len(mag_file))
    #print ('length of coord_file = ', len(cord_file))
    #print ('number of points in VTU file = ' , points.GetNumberOfPoints()," (x8) \n")

    # Create an array for the point vectors
    point_vectors = vtk.vtkDoubleArray()
    point_vectors.SetNumberOfComponents(3)
    point_vectors.SetNumberOfTuples(points.GetNumberOfPoints())
    point_vectors.SetName('Magnetization')
    # Add vectors to each point, 
    for i,ln in enumerate(mag_file):
            point_vectors.SetTuple(i*8, [ln[4], ln[5], ln[6]] )
            # adding an 8 to the index, as the number of points is x8 thye number of atoms
    # Add the point vectors to the point data
    my_vtk_dataset.GetPointData().AddArray(point_vectors)

    # adding vector data for cells
    cell_vectors = vtk.vtkDoubleArray()
    cell_vectors.SetNumberOfComponents(3)
    cell_vectors.SetNumberOfTuples(points.GetNumberOfPoints())
    cell_vectors.SetName('Cell_Magnetization')
    ci =0
    for i,ln in enumerate(mag_file):
            cell_vectors.SetTuple(i, [ln[4], ln[5], ln[6]])
            # don't have to add 8 here as the number of cells = number of atoms
    my_vtk_dataset.GetCellData().AddArray(cell_vectors)

    writer = vtk.vtkXMLUnstructuredGridWriter()
    my_filename =  out_filename #"outfile_ASD.vtu"
    writer.SetFileName(my_filename)
    writer.SetInputData(my_vtk_dataset)
    writer.Write()
    print (f'File written: "{my_filename}"')
    return 0

def write_vtu_vector (cord_data, field_data, out_filename):
    """provide data in the form carestian points ([px,py,pz]*N),
     vector data([mx, my, mz]*N), file_name: Where N is the number
     of nodes/points"""
    cord_file = cord_data
    mag_file = field_data

    my_vtk_dataset = vtk.vtkUnstructuredGrid()
    points = vtk.vtkPoints()
    cell = vtk.vtkHexahedron()

    id = 0
    my_vtk_dataset.Allocate(len(cord_file)*8)
    for ln in cord_file:
                pnts = get8pnts([ln[0],ln[1],ln[2]])
                point_ids = []
                for myp in pnts:
                    points.InsertPoint(id, myp)
                    point_ids.append(id)
                    id +=1
                # Setting 8 points for each cube
                cell.GetPointIds().SetId(0, point_ids[0])
                cell.GetPointIds().SetId(1, point_ids[1])
                cell.GetPointIds().SetId(2, point_ids[2])
                cell.GetPointIds().SetId(3, point_ids[3])
                cell.GetPointIds().SetId(4, point_ids[4])
                cell.GetPointIds().SetId(5, point_ids[5])
                cell.GetPointIds().SetId(6, point_ids[6])
                cell.GetPointIds().SetId(7, point_ids[7])
                # vtk.VTK_HEXAHEDRON means cube
                my_vtk_dataset.InsertNextCell(vtk.VTK_HEXAHEDRON, cell.GetPointIds())
            
    my_vtk_dataset.SetPoints(points)

    #print ('length of restart_file = ', len(mag_file))
    #print ('length of coord_file = ', len(cord_file))
    #print ('number of points in VTU file = ' , points.GetNumberOfPoints()," (x8) \n")

    # Create an array for the point vectors
    point_vectors = vtk.vtkDoubleArray()
    point_vectors.SetNumberOfComponents(3)
    point_vectors.SetNumberOfTuples(points.GetNumberOfPoints())
    point_vectors.SetName('volume_vector_field')
    # Add vectors to each point, 
    for i,ln in enumerate(mag_file):
            point_vectors.SetTuple(i*8, [ln[0], ln[1], ln[2]] )
            # adding an 8 to the index, as the number of points is x8 thye number of atoms
    # Add the point vectors to the point data
    my_vtk_dataset.GetPointData().AddArray(point_vectors)

    # adding vector data for cells
    cell_vectors = vtk.vtkDoubleArray()
    cell_vectors.SetNumberOfComponents(3)
    cell_vectors.SetNumberOfTuples(points.GetNumberOfPoints())
    cell_vectors.SetName('Cell_vector_3D')
    ci =0
    for i,ln in enumerate(mag_file):
            cell_vectors.SetTuple(i, [ln[0], ln[1], ln[2]])
            # don't have to add 8 here as the number of cells = number of atoms
    my_vtk_dataset.GetCellData().AddArray(cell_vectors)

    writer = vtk.vtkXMLUnstructuredGridWriter()
    my_filename =  out_filename #"outfile_ASD.vtu"
    writer.SetFileName(my_filename)
    writer.SetInputData(my_vtk_dataset)
    writer.Write()
    print (f'File written: "{my_filename}"')
    return 0

def get_uppasd_cordfile():
    try:
        coord_file_name = glob.glob("coord.*.out")[0]
    except IndexError:
        print("No 'coord.*.out' files found. Make sure that you copy it here. Exiting. \n")
        coord_file_name = None
        quit()
    return coord_file_name

def read_vec_data_uppasd (fname, data_cols=[4, 5, 6]):
    if fname.startswith("restart"):
        data_cols = [4,5,6]
    elif fname.startswith ("moment"):
        data_cols = [4,5,6]
    elif fname.startswith("STT"):
        data_cols = [4,5,6]
    
    vecdata = np.loadtxt(fname, usecols=(data_cols[0],
                                           data_cols[1],
                                           data_cols[2]))
    return vecdata


def extract_inp_data(filename, source_tool):
    if source_tool == "uppasd":
        cord_filename = get_uppasd_cordfile()
        try :
            cord_data = np.loadtxt(cord_filename)
            cord_data = cord_data[:, [1, 2, 3]]
        except IOError as myerror:
            print (myerror)
            print (f'the file {cord_filename} is not readable, exiting.')
              
        vecdata = read_vec_data_uppasd(filename)
        #numb_time_steps = len(vecdata)/number_of_atoms
    # space for adding more file-types

    else :
        print ("  ")
        print ("Error: ")
        print(f'Input files from tool "{source_tool}" are not supported yet,\n'
        'Please make sure that the tool name is typed correctly or \n'
        'please write to me to include this tool.\n')
        quit()
    return cord_data, vecdata

def check_file(file_path):
    """Check if a file exists and is readable."""
    if os.path.isfile(file_path) and os.access(file_path, os.R_OK):
        return True
    else:
        return False

def process_chunk(cord_data, field_data_chunk, out_filename):
    """Process a single chunk of data."""
    write_vtu_vector(cord_data=cord_data, field_data=field_data_chunk, out_filename=out_filename)

if __name__ == '__main__':
    print (":::.:::.:::.:::.:::\n")
    print ("ASD2VTK version 3.0  (17/Nov/2023) ")
    print ("Supported file-types: UppASD, ")
    print ("visit https://github.com/karpathyan/ASD2VTK/ for instructions and help.")
    print ("Rajgowrav Cheenikundil, Orebro University, Sweden.\n ")
    print (":::.:::.:::.:::.:::\n")

    inp_filename, source_tool = get_args_pos()
    print ("chosen file type: ", source_tool)
    print ("reading data from file: ", inp_filename )
    if check_file(inp_filename):
        print ("success.\n")
        print (":::.:::.:::.:::.:::\n")
    else: 
        print("")
        print ("Error:")
        print (f"The file '{inp_filename}' either does not exist or is not readable,")
        print ("make sure that this file is readable.")
        quit()

    cord_data, vec_data = extract_inp_data (inp_filename, source_tool)
    number_of_atoms = len(cord_data)
    numb_time_steps = int(len(vec_data)/number_of_atoms)

    

    #print ("\n ::::::: \n")
    print (f"number of atoms = {number_of_atoms}")
    print (f"number of time-steps = {numb_time_steps}")
    print ("\n:::.:::.:::.:::.:::\n")
   

    ftype_name = inp_filename.split('.')[0]
    out_name = "v_"+ftype_name+"_"
    try:
         assert len(vec_data) == int (number_of_atoms* numb_time_steps)
    except AssertionError as error:
         print ("Number of lines in ", inp_filename,"[", len(vec_data),"]"," \
                not equal to an integer multiple of number of atoms [", number_of_atoms, "].\n" )

    vec_data_chunks = np.array_split(vec_data, numb_time_steps)

    tasks = []

    for indx, field_data_chunk in enumerate(vec_data_chunks):
        fname = f"v_{ftype_name}_{indx}.vtu"
        tasks.append((cord_data, field_data_chunk, fname))

    t0 = tm.time()
    # Using multiprocessing to process chunks in parallel
    with Pool() as pool:
        pool.starmap(process_chunk, tasks)
    t1 = tm.time()
    print ("total time = ", round(t1-t0, 3), "seconds")

    