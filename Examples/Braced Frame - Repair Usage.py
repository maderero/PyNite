'''
This example shows how to use the repair_model function to automatically detect
and insert intermediate member nodes when generating a 2d braced frame . All
units in this model are expressed in terms of kips (force) and inches (length).
'''

from PyNite import FEModel3D

# Create a new finite element model
f = FEModel3D()

# Define Shape
length_verticals = 25*12
length_horizontals = 14*12
count_horizontals = 6
count_verticals = 2
count_mullions = 1
strong_params = {'E': 29000, 'G': 11200, 'Iy': 11.4, 'Iz': 118, 'J': 0.239, 'A': 6.49}  # W10X22
windload_psf = 32
windload_ksi = windload_psf / 144 / 1000  # ksi
girt_weight_lbpf = 22  # lb/ft
girt_weight = girt_weight_lbpf / 12 / 1000 # kip/in
# Add Horizontals
releases_horizontals = {'Ryi': True, 'Rzi': True, 'Ryj': True, 'Rzj': True, }
names_horizontals = []
names_mullions = []
for i in range(count_horizontals):
    y = i / (count_horizontals - 1) * length_verticals
    name_node_left = f.add_node(None, 0, y, 0)
    name_node_right = f.add_node(None, length_horizontals, y, 0)
    name_member = f.add_member(f'H{i}', name_node_left, name_node_right, **strong_params)
    f.def_releases(name_member, **releases_horizontals)
    w1 = w2 = -girt_weight
    f.add_member_dist_load(name_member, 'Fy', w1, w2, 0)
    names_horizontals.append(name_member)

for i in range(count_horizontals):
    index_low = max(i-1, 0)
    index_high = min(i+1, count_horizontals-1)
    member_low = f.Members[names_horizontals[index_low]]
    member_high = f.Members[names_horizontals[index_high]]

    tributary_width = abs(member_high.i_node.Y - member_low.i_node.Y)/2
    w1 = w2 = windload_ksi * tributary_width
    f.add_member_dist_load(names_horizontals[i], 'Fz', w1, w2, 0)

# Add Verticals
names_verticals = []
for i in range(count_verticals):
    x = i / (count_verticals - 1) * length_horizontals
    name_node_low = f.add_node(None, x, 0, 0)
    name_node_high = f.add_node(None, x, length_verticals, 0)
    name_member = f.add_member(f'V{i}', name_node_low, name_node_high, **strong_params)
    names_verticals.append(name_member)

for i in range(count_verticals):
    index_left = max(i-1, 0)
    index_right = min(i+1, count_verticals-1)
    name_left = names_verticals[index_left]
    name_right = names_verticals[index_right]
    tributary_width = abs(f.Members[name_left].i_node.X - f.Members[name_right].i_node.X)/2
    w1 = w2 = windload_ksi * tributary_width
    f.add_member_dist_load(names_verticals[i], 'Fz', w1, w2, 0)

# add mullions
mullion_releases = {'Ryi': True, 'Rzi': True, 'Ryj': True, 'Rzj': True, }
for ih in range(1, count_horizontals):
    for iv in range(count_verticals-1):
        for im in range(count_mullions):
            start_x = iv / (count_verticals - 1) * length_horizontals
            end_x = (iv + 1) / (count_verticals - 1) * length_horizontals
            span = abs(end_x - start_x)
            x = start_x + (im + 1) / (count_mullions + 1) * span
            y_low = f.Members[names_horizontals[ih-1]].i_node.Y
            y_high = f.Members[names_horizontals[ih]].i_node.Y
            node_low = f.add_node(None, x, y_low, 0)
            node_high = f.add_node(None, x, y_high, 0)
            mullion_name = f.add_member(None, node_low, node_high, **strong_params)
            f.def_releases(mullion_name, **mullion_releases)

# Add and define supports
support_ll = f.add_node(None, 24, 0, 0)
support_lr = f.add_node(None, length_horizontals-24, 0, 0)
# support_ul = f.add_node(None, 30, length_verticals, 0)
# support_ur = f.add_node(None, length_horizontals-30, length_verticals, 0)

f.def_support(
    support_ll,
    support_DX=True, support_DY=True, support_DZ=True,
    support_RX=False, support_RY=True, support_RZ=True)
f.def_support(
    support_lr,
    support_DX=True, support_DY=True, support_DZ=True,
    support_RX=False, support_RY=True, support_RZ=True)
# f.def_support(
#     support_ul,
#     support_DX=True, support_DY=True, support_DZ=True,
#     support_RX=False, support_RY=True, support_RZ=True)
# f.def_support(
#     support_ur,
#     support_DX=True, support_DY=True, support_DZ=True,
#     support_RX=False, support_RY=True, support_RZ=True)

_, right = f.split_member_at_node(names_horizontals[0], support_ll)
f.split_member_at_node(right.name, support_lr)
# _, right = f.split_member_at_node(names_horizontals[-1], support_ul)
# f.split_member_at_node(right.name, support_ur)


# Clean-up
f.repair(
    merge_duplicates=True,  # must be run to avoid duplicate nodes
    tolerance=1e-3,  # maximum 3d distance between coordinates to determine duplicate node
    )  # maximum 3d distance between lines to determine member intersection

# Analyze
f.analyze(log=False, check_statics=True)

# Display the deformed shape of the structure magnified 1 times with the text
# height 2 model units (inches) high.
from PyNite import Visualization
Visualization.render_model(f, annotation_size=2, deformed_shape=True, deformed_scale=100)
