from build123d import *
from ocp_vscode import show, show_object, reset_show, set_port, set_defaults, get_defaults
set_port(3939)

with BuildPart() as p:
    Box(40, 40, 28)
    
    fillet(edges().filter_by(Axis.Z),
           radius=4)
    topw = faces().sort_by(Axis.Z)[-1].outer_wire()
    with BuildSketch(Plane(topw@0, z_dir=topw%0, x_dir=(1, 0, 0))):
        Rectangle(3, 3,
                  align=(Align.MIN, Align.MIN))
    sweep(path=topw)

show_object(p.part)

