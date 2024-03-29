'''
Interface to the dot language
=============================

The B{Dot} module provides a simple interface to the
file format used in the U{graphviz<http://www.research.att.com/sw/tools/graphviz/>}
program. The module is intended to offload the most tedious part of the process
(the B{dot} file generation) while transparently exposing most of its features.

To display the graphs or to generate image files the U{graphviz<http://www.research.att.com/sw/tools/graphviz/>}
package needs to be installed on the system, moreover the C{dot} and C{dotty} programs must
be accesible in the program path so that they can be ran from processes spawned
within the module. See the L{Dot} documentation for further information on the setup.

Example usage
-------------

Here is a typical usage::

    from altgraph import Graph, Dot

    # create a graph
    edges = [ (1,2), (1,3), (3,4), (3,5), (4,5), (5,4) ]
    graph = Graph.Graph(edges)

    # create a dot representation of the graph
    dot = Dot.Dot(graph)

    # display the graph
    dot.display()

    # save the dot representation into the mydot.dot file
    dot.save_dot(file_name='mydot.dot')

    # save dot file as gif image into the graph.gif file
    dot.save_img(file_name='graph', file_type='gif')

Directed graph and non-directed graph
-------------------------------------

Dot class can use for both directed graph and non-directed graph
by passing B{graphtype} parameter.

Example::
    # create directed graph(default)
    dot = Dot.Dot(graph, graphtype="digraph")

    # create non-directed graph
    dot = Dot.Dot(graph, graphtype="graph")

Customizing the output
----------------------

The graph drawing process may be customized by passing
valid B{dot} parameters for the nodes and edges. For a list of all
parameters see the U{graphviz<http://www.research.att.com/sw/tools/graphviz/>}
documentation.

Example::
    # customizing the way the overall graph is drawn
    dot.style(size='10,10', rankdir='RL', page='5, 5' , ranksep=0.75)

    # customizing node drawing
    dot.node_style(1, label='BASE_NODE',shape='box', color='blue' )
    dot.node_style(2, style='filled', fillcolor='red')

    # customizing edge drawing
    dot.edge_style(1, 2, style='dotted')
    dot.edge_style(3, 5, arrowhead='dot', label='binds', labelangle='90')
    dot.edge_style(4, 5, arrowsize=2, style='bold')


B{Observation}: dotty (invoked via L{Dot.display}) may not be able to
display all graphics styles. To verify the output save it to an image file
and look at it that way.

Valid attributes
----------------

    - dot styles, passed via the L{Dot.style} method::
        rankdir = 'LR'   (draws the graph horizontally, left to right)
        ranksep = number (rank separation in inches)

    - node attributes, passed via the L{Dot.node_style} method::
        style = 'filled' | 'invisible' | 'diagonals' | 'rounded'
        shape = 'box' | 'ellipse' | 'circle' | 'point' | 'triangle'

    - edge attributes, passed via the L{Dot.edge_style} method::
        style     = 'dashed' | 'dotted' | 'solid' | 'invis' | 'bold'
        arrowhead = 'box' | 'crow' | 'diamond' | 'dot' | 'inv' | 'none' | 'tee' | 'vee'
        weight    = number (the larger the number the closer the nodes will be)

    - valid U{graphviz colors<http://www.research.att.com/~erg/graphviz/info/colors.html>}

    - for more details on how to control the graph drawing process see the
    U{graphviz reference <http://www.research.att.com/sw/tools/graphviz/refs.html>}.

'''
import os

from altgraph import GraphError
from altgraph.compat import *

class Dot(object):
    '''
    A  class providing a B{graphviz} (dot language) representation
    allowing a fine grained control over how the graph is being
    displayed.

    If the C{dot} and C{dotty} programs are not in the current system path
    their location needs to be specified in the L{constructor<__init__>}.

    For detailed example usage see the L{Dot} module documentation.
    '''

    def __init__(self, graph=None, nodes=None, edgefn=None, nodevisitor=None, edgevisitor=None, name="G", dot='dot', dotty='dotty', neato='neato', graphtype="digraph"):
        '''
        Initialization.
        '''
        self.name, self.attr = name, {}
        
        assert graphtype in ['graph', 'digraph']
        self.type = graphtype

        self.temp_dot = "tmp_dot.dot"
        self.temp_neo = "tmp_neo.dot"

        self.dot, self.dotty, self.neato = dot, dotty, neato
        self.nodes, self.edges = {}, {}

        if graph is not None and nodes is None:
            nodes = graph
        if graph is not None and edgefn is None:
            def edgefn(node, graph=graph):
                return imap(graph.tail, graph.out_edges(node))
        if nodes is None:
            nodes = ()

        seen = set()
        for node in nodes:
            if nodevisitor is None:
                style = {}
            else:
                style = nodevisitor(node)
            if style is not None:
                self.node_style(node, **style)
                seen.add(node)
        if edgefn is not None:
            for head in seen:
                for tail in ifilter(seen.__contains__, edgefn(head)):
                    if edgevisitor is None:
                        edgestyle = {}
                    else:
                        edgestyle = edgevisitor(head, tail)
                    if edgestyle is not None:
                        self.edge_style(head, tail, **edgestyle)

    def style(self, **attr):
        '''
        Changes the overall style
        '''
        self.attr = attr

    def display(self, mode='dot'):
        '''
        Displays the current graph via dotty
        '''

        if  mode == 'neato':
            self.save_dot(self.temp_neo)
            neato_cmd = "%s -o %s %s" % (self.neato, self.temp_dot, self.temp_neo)
            os.system(neato_cmd)
        else:
            self.save_dot(self.temp_dot)

        plot_cmd = "%s %s" % (self.dotty, self.temp_dot)
        os.system(plot_cmd)

    def node_style(self, node, **kwargs):
        '''
        Modifies a node style to the dot representation.
        '''
        if node not in self.edges:
            self.edges[node] = {}
        self.nodes[node] = kwargs

    def all_node_style(self, **kwargs):
        '''
        Modifies all node styles
        '''
        for node in self.nodes:
            self.node_style(node, **kwargs)

    def edge_style(self, head, tail, **kwargs):
        '''
        Modifies an edge style to the dot representation.
        '''
        try:
            if tail not in self.edges[head]:
                self.edges[head][tail]= {}
            self.edges[head][tail] = kwargs
        except KeyError:
            raise GraphError("invalid edge  %s -> %s " % (head, tail) )

    def iterdot(self):
        # write graph title
        if self.type == 'digraph':
            yield 'digraph %s {\n' % (self.name,)
        elif self.type == 'graph':
            yield 'graph %s {\n' % (self.name,)

        # write overall graph attributes
        for attr_name, attr_value in self.attr.iteritems():
            yield '%s="%s";' % (attr_name, attr_value)
        yield '\n'

        # some reusable patterns
        cpatt  = '%s="%s",'      # to separate attributes
        epatt  = '];\n'          # to end attributes

        # write node attributes
        for node_name, node_attr in self.nodes.iteritems():
            yield '\t"%s" [' % (node_name,)
            for attr_name, attr_value in node_attr.iteritems():
                yield cpatt % (attr_name, attr_value)
            yield epatt

        # write edge attributes
        for head in self.edges:
            for tail in self.edges[head]:
                if self.type == 'digraph':
                    yield '\t"%s" -> "%s" [' % (head, tail)
                else:
                    yield '\t"%s" -- "%s" [' % (head, tail)
                for attr_name, attr_value in self.edges[head][tail].iteritems():
                    yield cpatt % (attr_name, attr_value)
                yield epatt

        # finish file
        yield '}\n'

    def __iter__(self):
        return self.iterdot()

    def save_dot(self, file_name=None):
        '''
        Saves the current graph representation into a file
        '''

        if not file_name:
            file_name = self.temp_dot

        fp   = open(file_name, "w")
        write = fp.write
        for chunk in self.iterdot():
            write(chunk)
        fp.close()

    def save_img(self, file_name="out", file_type="gif", mode='dot'):
        '''
        Saves the dot file as an image file
        '''

        if  mode == 'neato':
            self.save_dot(self.temp_neo)
            neato_cmd = "%s -o %s %s" % (self.neato, self.temp_dot, self.temp_neo)
            os.system(neato_cmd)
            plot_cmd = self.neato
        else:
            self.save_dot(self.temp_dot)
            plot_cmd = self.dot

        file_name  = "%s.%s" % (file_name, file_type)
        create_cmd = "%s -T%s %s -o %s" % (plot_cmd, file_type, self.temp_dot, file_name)
        os.system(create_cmd)
