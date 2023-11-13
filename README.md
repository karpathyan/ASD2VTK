
# ASD2VTK - Atomistic Spin Dynamics simulation data to VTK Converter
<img src="./images/Logo.png" alt="Logo" width="150" height="150"> <img src="./images/ExB_setup-AFM_coupled.png" alt="nice_image" width="253" height="192">


Author: Rajgowrav Cheenikundil, Orebro University.




ASD2VTK is a Python script that enables easy conversion of Atomistic Spin Dynamics (ASD) simulation data from UppASD simulations to Visualization Toolkit (VTK) files, for visualization in software such as ParaView. This tool simplifies the process of generating VTK files, allowing users to visualize atomistic simulation results efficiently.

## Features
- Converts UppASD simulation outputs (coord.*.out and restart.*.out) to VTK files.



## Requirements
- Python 3.x
- VTK library (`pip install vtk --user`)
- ParaView installed for visualization 

## Usage
1. Ensure that the UppASD simulation outputs, "coord.*.out" and "restart.*.out," "moment.*.output" etc are in the same directory as the script.
2. Run the Python script "ASD2VTK.py" followed by the input file name and the tool-name in the directory containing the aforementioned simulation outputs.               
   ```python ASD2VTK.py inputfile source-tool-name```
    example
   ``` python ASD2VTK.py moment.bcc_Fe.out uppasd```
   deffault is restart.*.out and UppASD
4. The script will generate a VTU file named "v_*.vtu" in the same directory.
5. Open the output file with Paraview and click on "Apply"
6. In ParaView, choose `Cell_vector_3D` as the visualization field
7. If you want to plot the magnetization with arrows, choose the "Glyph" tool in Paraview, and choose `Cell_Vector_3D` as the orientation array.

( The outputs written using version 1.0 of  ASD2VTK.py are tested and working/opening without errors on Paraview version 5.11.0 on Ubuntu  version 23  )

**Note:**
- Make sure that there is only one "coord.*.out" and one "restart.*.out" file in the running directory.
- The number of points in the VTU file will be 8 times the number of atoms, as 8 points are needed for each cube.

## Contributing
Contributions to improve ASD2VTK are welcome! Feel free to open issues, suggest enhancements, or submit pull requests. Let's collaborate and make this tool even better.

## License
ASD2VTK is released under the GNU Affero General Public License version 3.0 (GNU AGPLv3). Please see the `LICENSE` file for more details.

## Disclaimer
This software is provided as-is and comes with no warranty. 

---
