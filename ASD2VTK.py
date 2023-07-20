"""
ASD2VTK version 1.0
Rajgowrav Cheenikundil, Orebro University, Sweden. 

(visit https://github.com/karpathyan/ASD2VTK/ for instructions and help )  

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
"""


import vtk, glob
import numpy as np

dx = 0.5
dy = 0.5

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

#coord_file_name = glob.glob("coord.*.out")[0]
#restart_file_name = glob.glob("restart.*.out")[0]

print (":::.:::.:::.:::.:::\n")
print ("ASD2VTK version 1.0  ")
print (" visit https://github.com/karpathyan/ASD2VTK/ for instructions and help\n")
print (":::.:::.:::.:::.:::\n")
try:
    coord_file_name = glob.glob("coord.*.out")[0]
except IndexError:
    print("No 'coord.*.out' files found. Make sure that you copy it here. Exiting. \n")
    coord_file_name = None
    quit()

try:
    restart_file_name = glob.glob("restart.*.out")[0]
except IndexError:
    print("No 'restart.*.out' files found. Make sure that you copy it here. Exiting. \n")
    restart_file_name = None
    quit()

if coord_file_name and restart_file_name:
    print(f'reading data from: "{coord_file_name}" and "{restart_file_name}" \n ')

cord_file = np.loadtxt(coord_file_name)
mag_file = np.loadtxt(restart_file_name)

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

print ('length of restart_file = ', len(mag_file))
print ('length of coord_file = ', len(cord_file))
print ('number of points in VTU file = ' , points.GetNumberOfPoints()," (x8) \n")

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
my_filename = "outfile_ASD.vtu"
writer.SetFileName(my_filename)
writer.SetInputData(my_vtk_dataset)
writer.Write()
print (f'File written: "{my_filename}" \n')
