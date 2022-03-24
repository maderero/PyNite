'''
This example shows how to use the repair_model function to automatically detect
and insert intermediate member nodes when generating a 2d braced frame . All
units in this model are expressed in terms of kips (force) and inches (length).
'''

from PyNite import FEModel3D

# Create a new finite element model
f = FEModel3D()

# Define Shape
length_verticals = 10*12
length_horizontals = 10*12
count_horizontals = 10
count_verticals = 10
strong_params = {'E': 999999, 'G': 100, 'Iy': 1000, 'Iz': 1000, 'J': 100, 'A': 100}

# Add Horizontals
releases_horizontals = {'Ryi': True, 'Rzi': True, 'Ryj': True, 'Rzj': True, }
names_horizontals = []
for i in range(count_horizontals):
    y = i / (count_horizontals - 1) * length_verticals
    name_node_left = f.add_node(None, 0, y, 0)
    name_node_right = f.add_node(None, length_horizontals, y, 0)
    name_member = f.add_member(f'H{i}', name_node_left, name_node_right, **strong_params)
    f.def_releases(name_member, **releases_horizontals)
    names_horizontals.append(name_member)

# Add Verticals
names_verticals = []
for i in range(count_verticals):
    x = i / (count_verticals - 1) * length_horizontals
    name_node_low = f.add_node(None, x, 0, 0)
    name_node_high = f.add_node(None, x, length_verticals, 0)
    name_member = f.add_member(f'V{i}', name_node_low, name_node_high, **strong_params)
    names_verticals.append(name_member)

# Add and define supports
support_node_left = f.find_node_by_coordinates((0, 0, 0))
support_node_right = f.find_node_by_coordinates((length_horizontals, 0, 0))
f.def_support(
    support_node_left.name,
    support_DX=True, support_DY=True, support_DZ=True,
    support_RX=True, support_RY=True, support_RZ=True)
f.def_support(
    support_node_right.name,
    support_DX=True, support_DY=True, support_DZ=True,
    support_RX=True, support_RY=True, support_RZ=True)

# Clean-up
f.repair(
    merge_duplicates=True,  # must be run to avoid duplicate nodes
    tolerance_node=1e-3,  # maximum 3d distance between coordinates to determine duplicate node
    tolerance_intersection=1e-3)  # maximum 3d distance between lines to determine member intersection

# Analyze
f.analyze(log=False, check_statics=False)

# Display the deformed shape of the structure magnified 50 times with the text
# height 5 model units (inches) high.
from PyNite import Visualization
Visualization.render_model(f, annotation_size=5, deformed_shape=True, deformed_scale=50)
