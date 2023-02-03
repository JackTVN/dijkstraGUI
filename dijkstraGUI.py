import tkinter
import tkinter.messagebox
import time

from copy import deepcopy
import ast

import Maze

# GLOBAL VARIABLE
CANVAS_HEIGHT = 500
CANVAS_WIDTH = 1000

# start and end arguments take position, assumming no duplicate, the function will find the start and end in the list and use it
# Function return list consisted of the position of all the point in the list that lead to the answer
# Update: startConnect and endConnect is the connect of start and end to other note in the polygon. Separated to comply with the current structure
def dijkstra(point, connect, start, end, startConnect, endConnect):
    if start == [] or end == []:
        return []

    if start == end:
        return [start, end]

    # Add start and end to the list of vertices as if it were a normal connect graph
    pointC = deepcopy(point)
    pointC.append(start)
    pointC.append(end)
    startP = len(pointC) - 2
    endP = len(pointC) - 1
    pAmount = len(pointC)

    # Add the connection together for the same reason above
    connectC = deepcopy(connect)

    for i in range(len(connect)):
        connectC[i].append(startConnect[i])
        connectC[i].append(endConnect[i])

    connectC.append(startConnect)
    connectC.append(endConnect)

    # The actual start of Djikstra
    # A set of value that might be usable in the next iteration of Dijkstra
    waitS = set()

    # The previous point that the runner move from to the current
    prev = []

    # Check if point is visited, and basically locked
    visited = []

    # weight of each vertices, all start at infinite, with the start weight at 0
    weight = []

    for i in range(pAmount):
        prev.append(-1)  # Give all point a previous point of nothing
        visited.append(False)  # Give all point a status of not visited
        weight.append(2147483647) # Give all point infinite weight since the program can't get to it yet

    weight[startP] = 0

    # add the start point to the mainQueue
    waitS.add(startP)

    prev[startP] = startP

    while not visited[endP] and len(waitS) > 0:
        # Scuffed way of getting the most prioritized point currently
        cur = waitS.pop()
        waitS.add(cur)

        for p in waitS:
            if weight[p] < weight[cur]:
                cur = p

        waitS.remove(cur)
        visited[cur] = True

        for i in range(pAmount):
            if connectC[cur][i] and not visited[i] and weight[i] > weight[cur] + ((pointC[cur][0] - pointC[i][0]) ** 2 + (pointC[cur][1] - pointC[i][1]) ** 2) ** (1/2):
                weight[i] = weight[cur] + ((pointC[cur][0] - pointC[i][0]) ** 2 + (pointC[cur][1] - pointC[i][1]) ** 2) ** (1/2)
                prev[i] = cur

                waitS.add(i)

    res = []

    if visited[endP]:
        while not prev[endP] == endP:
            res.append(endP)
            endP = prev[endP]

        res.append(endP)

    return res[::-1]

def checkMiddle(a, b, c):
    if (
        (b[0] <= max(a[0], c[0])) and (b[0] >= min(a[0], c[0])) and
        (b[1] <= max(a[1], c[1])) and (b[1] >= min(a[1], c[1]))
    ):
        return True
    return False

# Given 3 point, check if they go in a clockwise/counterclockwise or collinear
# 1. Clockwise
# 2. Counter-clockwise
# 0. Collinear
def checkOrientation(a, b, c):
    # Calculate the change of slope
    val = ((b[1] - a[1]) * (c[0] - b[0])) - ((b[0] - a[0]) * (c[1] - b[1]))

    if val > 0:
        return 1
    if val < 0:
        return 2
    return 0

# 0. No Intersect
# 1. Intersect 100%
# 2. Intersect through a start/end
def checkIntersect(s1, e1, s2, e2):
    if s1 == s2 or e1 == s2 or s1 == e2 or e1 == e2:
        return 0

    o1 = checkOrientation(s1, e1, s2)
    o2 = checkOrientation(s1, e1, e2)
    o3 = checkOrientation(s2, e2, s1)
    o4 = checkOrientation(s2, e2, e1)

    if not o1 == o2 and not o3 == o4:
        return 1

    # All Collinear. Might be good to return 0
    if (o1 == 0) + (o2 == 0) + (o3 == 0) + (o4 == 0) > 1 and (checkMiddle(s1, s2, e1) or checkMiddle(s1, e2, e1)):
        return 0

    if o1 == 0 and checkMiddle(s1, s2, e1):
        return 2
    if o2 == 0 and checkMiddle(s1, e2, e1):
        return 2
    if o3 == 0 and checkMiddle(s2, s1, e2):
        return 2
    if o4 == 0 and checkMiddle(s2, e1, e2):
        return 2

    return 0

def isRouteInPolygon(point, a, b):
    if len(point) < 3:
        return 0

    if a == b:
        return 0

    # bool that check if there's no wall that intersect the path
    smooth = True

    # the midpoint of the two vertices of the path. Used to check if a path that doesn't go through wall is inside the main polygon map
    middlePoint = [b[0]/2 + a[0]/2, b[1]/2 + a[1]/2]
    middleInside = False

    for vert1 in range(len(point)):
        vert2 = (vert1+1) % (len(point))

        if checkMiddle(point[vert1], a, point[vert2]) and checkOrientation(point[vert1], a, point[vert2]) == 0 and checkMiddle(point[vert1], b, point[vert2]) and checkOrientation(point[vert1], b, point[vert2]) == 0:
            return 1

        # Note: Read this till understand
        # TLDR: This help check if point is in a polygon
        # https://wrf.ecse.rpi.edu/Research/Short_Notes/pnpoly.html
        if not ((point[vert1][1] > middlePoint[1]) == (point[vert2][1] > middlePoint[1])):
            if middlePoint[0] < (point[vert2][0] - point[vert1][0]) * (middlePoint[1] - point[vert1][1]) / (point[vert2][1] - point[vert1][1]) + point[vert1][0]:
                middleInside = not middleInside

        # Check for the more obvious: if the current path go through any wall
        # Check middle for edge case where the start/end point is right on top of one of the polygon's edge
        if not checkIntersect(a, b, point[vert1], point[vert2]) == 0 and not (checkMiddle(point[vert1], a, point[vert2]) and not checkOrientation(point[vert1], a, point[vert2])) and not (checkMiddle(point[vert1], b, point[vert2]) and not checkOrientation(point[vert1], b, point[vert2])):
            smooth = False
            break

    if middleInside and smooth:
        return 1

    return 

def GetRouteFromPolygon(point):
    if len(point) < 3:
        return []

    result = []

    # Setting up a new, empty connect list
    for i in range(len(point)):
        resrow = []
        for j in range(len(point)):
            resrow.append(0)
        result.append(resrow)

    # Check if there's an available path from i to j
    for i in range(len(point)):
        for j in range(i + 1, len(point)):
            # return an available route if 2 points make an edge of the polygon
            if j - i == 1 or (i == 0 and j == len(point) - 1):
                result[i][j] = 1
                result[j][i] = 1
            else:
                res = isRouteInPolygon(point, point[i], point[j])
                result[i][j] = res
                result[j][i] = res

    return result

# MAIN CLASS
class DjikstraGUI:
    def __init__(self):
        # Setting up the main window
        self.w_main = tkinter.Tk(className='DijkstraGUI')

        self.cont = tkinter.Frame(self.w_main, padx=20, pady=10, bg='#1c1c1c')
        self.cont.columnconfigure(0, weight=1)

        # The program section, thing that are generally unrelated to tkinter
        self.point = [
            [40, 40], [80, 80], [80, 160], [120, 160], 
            [120, 40], [160, 80], [160, 280], [180, 280], 
            [200, 300], [200, 40], [280, 40], [320, 80], 
            [240, 80], [240, 160], [280, 160], [320, 200], 
            [240, 200], [240, 280], [340, 280], [360, 300], 
            [360, 40], [400, 80], [400, 280], [500, 280], 
            [520, 300], [520, 40], [560, 80], [560, 280], 
            [660, 280], [680, 300], [702, 300], [722, 280], 
            [760, 280], [760, 80], [720, 80], [720, 275], 
            [700, 295], [680, 295], [680, 40], [760, 40], 
            [800, 80],  [800, 320], [120, 320], [120, 200],
            [80, 200], [80, 320], [40, 320]
        ]

        self.pointIn = [[209, 131], [193, 313], [619, 338], [628, 154]]

        self.startP = []
        self.endP = []

        # The two last connection indicate the start and end. Will usually get update after a reload
        self.pointConnect = []

        # Exclusive connect for the start point and end point. This is to reduce wait time on changing them
        self.startConnect = []
        self.endConnect = []

        # The result of a dijkstra run, only update when the user run in order to get the time
        self.path = []
        self.distance = -1

        # Some time-related stuff
        self.graphMapTime = 0
        self.graphSETime = 0
        self.pathTime = 0

        # The Data section, mostly label that say stuff/guiding
        self.f_data = tkinter.Frame(self.cont, padx=10,pady=5, bg='#1c1c1c')

        self.lf_timeLabel = tkinter.LabelFrame(self.f_data, text='Time', bg='#1c1c1c', fg='#ffffff')
        self.l_timePath = tkinter.Label(self.lf_timeLabel, text='Dijkstra: ', bg='#1c1c1c', fg='#ffffff')
        self.l_timeGraph = tkinter.Label(self.lf_timeLabel, text='|    Graph: ', bg='#1c1c1c', fg='#ffffff')
        self.l_timeTotal = tkinter.Label(self.lf_timeLabel, text='|    Total: ', bg='#1c1c1c', fg='#ffffff')
        self.v_timePath = tkinter.StringVar()
        self.v_timeGraph = tkinter.StringVar()
        self.v_timeTotal = tkinter.StringVar()
        self.l_vTimePath = tkinter.Label(self.lf_timeLabel, textvariable=self.v_timePath, bg='#1c1c1c', fg='#ffffff', width=15)
        self.l_vTimeGraph = tkinter.Label(self.lf_timeLabel, textvariable=self.v_timeGraph, bg='#1c1c1c', fg='#ffffff', width=15)
        self.l_vTimeTotal = tkinter.Label(self.lf_timeLabel, textvariable=self.v_timeTotal, bg='#1c1c1c', fg='#ffffff', width=15)

        self.lf_distance = tkinter.LabelFrame(self.f_data, text='Distance', bg='#1c1c1c', fg='#ffffff')
        self.v_distance = tkinter.StringVar()
        self.v_distance.set('-1 pixels')
        self.l_distanceV = tkinter.Label(self.lf_distance, textvariable=self.v_distance, bg='#1c1c1c', fg='#ffffff')

        self.lf_timeLabel.grid(column=0, row=0, sticky=tkinter.W)
        self.l_timePath.grid(column=0, row=0)
        self.l_timeGraph.grid(column=2, row=0)
        self.l_timeTotal.grid(column=4, row=0)
        self.l_vTimePath.grid(column=1, row=0)
        self.l_vTimeGraph.grid(column=3, row=0)
        self.l_vTimeTotal.grid(column=5, row=0)

        self.lf_distance.grid(column=1, row=0, sticky=tkinter.W, padx=10)
        self.l_distanceV.grid(column=0, row=0)

        self.f_controlmain = tkinter.Frame(self.cont, bg='#1c1c1c')

        # The Control section, mostly button for different purpose
        self.f_control1 = tkinter.Frame(self.f_controlmain, bg='#1c1c1c')

        self.v_pathCheck = tkinter.IntVar()
        self.v_pathCheck.set(0)
        self.cbt_run = tkinter.Checkbutton(self.f_control1, text="Path", variable=self.v_pathCheck, command=self.reload_map, padx=20, bg='#1c1c1c', fg='#ffffff', activebackground='#1c1c1c', activeforeground='#ffffff', selectcolor='#1c1c1c')

        self.v_graphCheck = tkinter.IntVar()
        self.v_graphCheck.set(0)
        self.cbt_graph = tkinter.Checkbutton(self.f_control1, text="Graph", variable=self.v_graphCheck, command=self.reload_map, padx=20, bg='#1c1c1c', fg='#ffffff', activebackground='#1c1c1c', activeforeground='#ffffff', selectcolor='#1c1c1c')

        self.v_vertex = tkinter.IntVar()
        self.v_vertex.set(0)
        #self.lb_index = tkinter.Listbox(self.f_control1, bg='#1c1c1c', fg='#ffffff', height=3, width=8, selectbackground="#ffffff", selectforeground='#1c1c1c', activestyle='none', bd=0, font=("TkDefaultFont", 7, 'bold'))
        self.rbt_vertexNone = tkinter.Radiobutton(self.f_control1, text="None", variable=self.v_vertex, value=0, command=self.reload_map, bg='#1c1c1c', fg='#ffffff', activebackground='#1c1c1c', activeforeground='#ffffff', selectcolor='#1c1c1c')
        self.rbt_vertexInd = tkinter.Radiobutton(self.f_control1, text="Index", variable=self.v_vertex, value=1, command=self.reload_map, bg='#1c1c1c', fg='#ffffff', activebackground='#1c1c1c', activeforeground='#ffffff', selectcolor='#1c1c1c')
        self.rbt_vertexPos = tkinter.Radiobutton(self.f_control1, text="Position", variable=self.v_vertex, value=2, command=self.reload_map, bg='#1c1c1c', fg='#ffffff', activebackground='#1c1c1c', activeforeground='#ffffff', selectcolor='#1c1c1c')

        # The 2nd Control section, for action more related to the canvas/map
        self.f_control2 = tkinter.Frame(self.f_controlmain, bg='#1c1c1c')
        self.bt_clear = tkinter.Button(self.f_control2, text="Clear All Vertices", command=self.clear_map, width=15, bg='#1c1c1c', fg='#ffffff')

        self.v_isDrawing = tkinter.StringVar()
        self.v_isDrawing.set("Start Draw Session")
        self.bt_drawPoly = tkinter.Button(self.f_control2, textvariable=self.v_isDrawing, command=self.start_draw_map, width=15, bg='#1c1c1c', fg='#ffffff')

        self.bt_newrandom = tkinter.Button(self.f_control2, text="Generate Map", command=self.random_map, width=15, bg='#1c2c2c', fg='#ffffff')
        self.bt_exportGraph = tkinter.Button(self.f_control2, text="Export Graph", command=self.export_graph, width=15, bg='#1c1c1c', fg='#ffffff')
        self.bt_importGraph = tkinter.Button(self.f_control2, text="Import Graph", command=self.import_graph, width=15, bg='#1c1c1c', fg='#ffffff')
        self.bt_forceRun = tkinter.Button(self.f_control2, text="Full Run/Rerun", command=self.force_evaluation, height=2, width=20, bg='#9c1c1c', fg='#ffffff')

        self.v_exported = tkinter.StringVar()
        self.e_exported = tkinter.Entry(self.f_control2, textvariable=self.v_exported, state='readonly',width=20, readonlybackground='#191919', fg='#ffffff')
        self.e_imported = tkinter.Entry(self.f_control2, width=20, bg='#292929', fg='#ffffff')

        self.l_width = tkinter.Label(self.f_control2, text="Width:", bg='#1c1c1c', fg='#ffffff')
        self.e_width = tkinter.Entry(self.f_control2, width=3, bg='#292929', fg='#ffffff')
        self.e_width.insert(tkinter.END, '10')
        self.l_height = tkinter.Label(self.f_control2, text="Height:", bg='#1c1c1c', fg='#ffffff')
        self.e_height = tkinter.Entry(self.f_control2, width=3, bg='#292929', fg='#ffffff')
        self.e_height.insert(tkinter.END, '5')
        self.v_autoRun = tkinter.IntVar()
        self.v_autoRun.set(0)
        self.cbt_autoRun = tkinter.Checkbutton(self.f_control2, text="Auto run on load", variable=self.v_autoRun, bg='#1c1c1c', fg='#ffffff', activebackground='#1c1c1c', activeforeground='#ffffff', selectcolor='#1c1c1c')
        self.v_aspect = tkinter.IntVar()
        self.v_aspect.set(0)
        self.cbt_aspect = tkinter.Checkbutton(self.f_control2, text="Maintain aspect ratio", variable=self.v_aspect, bg='#1c1c1c', fg='#ffffff', activebackground='#1c1c1c', activeforeground='#ffffff', selectcolor='#1c1c1c')

        self.f_control1.grid(column=0, row=0, sticky=tkinter.N, padx=10)
        self.cbt_run.grid(column=0, row=0, sticky=tkinter.W)
        self.cbt_graph.grid(column=1, row=0, sticky=tkinter.W)
        self.rbt_vertexNone.grid(column=0, row=1, columnspan=2, sticky=tkinter.W, padx=60)
        self.rbt_vertexInd.grid(column=0, row=2, columnspan=2, sticky=tkinter.W, padx=60)
        self.rbt_vertexPos.grid(column=0, row=3, columnspan=2, sticky=tkinter.W, padx=60)

        self.f_control2.grid(column=1, row=0, sticky=tkinter.NSEW)
        self.bt_clear.grid(column=0, row=0)
        self.bt_drawPoly.grid(column=0, row=1)
        self.bt_newrandom.grid(column=0, row=2, rowspan=2, sticky=tkinter.NSEW)
        self.bt_exportGraph.grid(column=1, row=0, columnspan=2)
        self.bt_importGraph.grid(column=1, row=1, columnspan=2)
        self.e_exported.grid(column=3, row=0, sticky=tkinter.NSEW, pady=1)
        self.e_imported.grid(column=3, row=1, sticky=tkinter.NSEW, pady=1)
        self.l_height.grid(column=1, row=2)
        self.e_height.grid(column=2, row=2, sticky=tkinter.NSEW, pady=1)
        self.l_width.grid(column=1, row=3)
        self.e_width.grid(column=2, row=3, sticky=tkinter.NSEW, pady=1)
        self.cbt_autoRun.grid(column=3, row=2, sticky=tkinter.W)
        self.cbt_aspect.grid(column=3, row=3, sticky=tkinter.W)

        self.bt_forceRun.grid(column=4, row=0, columnspan=2, rowspan=2, padx=140)

        # The Map section, the map for the djikstra simulation
        self.f_map = tkinter.Frame(self.cont, pady=10, bg='#1c1c1c')
        self.c_map = tkinter.Canvas(self.f_map, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, highlightthickness=1, relief='ridge')

        self.reload_map(code=2)

        self.c_map.grid(column=0, row=0)

        # Canvas input-related code
        self.c_map.bind("<Button-1>", self.update_start)
        self.c_map.bind("<Button-3>", self.update_end)

        #  Packing main frame
        self.cont.pack(expand=1)
        self.f_data.grid(column=0, row=0, sticky=tkinter.EW)
        self.f_controlmain.grid(column=0, row=1, sticky=tkinter.W)
        self.f_map.grid(column=0, row=2)

        # Mainloop
        tkinter.mainloop()

    # A load/reload canvas function to update canvas from diffrent event
    # Code:
    # 0. Reload to enable/disable some visual, no need for an info reload   
    # 1. There's change to the start/end point, reload thing related to that only
    # 2. There's change to the map, reload all
    def reload_map(self, code=0):
        # Canvas in tkinter actually hold all object as object, even if it got drawn-over. Use delete to prevent memory leak
        self.c_map.delete('all')

        # Stop some in-runnning event
        self.end_draw_map(event="force")

        # Update anything that changed due to user input (example: reconnect all available path)
        if code == 2:
            self.pointConnect = []

        if (self.v_graphCheck.get() or (self.v_pathCheck.get() and not self.startP == [] and not self.endP == [])) and self.pointConnect == []:
            startTime = time.time()
            self.pointConnect = GetRouteFromPolygon(self.point)
            self.graphMapTime = time.time() - startTime
            
        # Update thing that related to the start/end point .aka everything that isn't the main route graph
        if code > 0:
            self.path = []
            self.v_timePath.set(-1)

            startTime = time.time()

            if not self.startP == []:
                self.startConnect = []
                for p in self.point:
                    self.startConnect.append(isRouteInPolygon(self.point, self.startP, p))

                # The 2nd to last element represent the start's connection to itself, since this will be handy when using dijkstra
                self.startConnect.append(0)

                if not self.endP == []:
                    self.startConnect.append(isRouteInPolygon(self.point, self.startP, self.endP))
                else: 
                    self.startConnect.append(0)

            if not self.endP == []:
                self.endConnect = []
                for p in self.point:
                    self.endConnect.append(isRouteInPolygon(self.point, self.endP, p))

                if not self.startP == []:
                    self.endConnect.append(isRouteInPolygon(self.point, self.startP, self.endP))
                else:
                    self.endConnect.append(0)

                # The last element represent the end's connection to itself, since this will be handy when using dijkstra
                self.endConnect.append(0)

            self.graphSETime = time.time() - startTime

        # Redraw everything
        self.c_map.create_rectangle(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT, fill='#161616')

        if len(self.point) > 2:
            self.c_map.create_polygon(self.point, fill='#303030')

        if self.v_graphCheck.get():
            # Draw all connection between point
            for i in range(len(self.pointConnect)):
                for j in range(len(self.pointConnect)):
                    if self.pointConnect[i][j]:
                        self.c_map.create_line(self.point[i], self.point[j], fill="#696969")

            # Draw all connection to the start
            for i in range(len(self.startConnect)):
                if self.startConnect[i]:
                    if i >= len(self.point):
                        if not self.endP == []:
                            self.c_map.create_line(self.startP, self.endP, fill="#696969")
                    else:
                        self.c_map.create_line(self.startP, self.point[i], fill="#696969")

            # Draw all connection to the end
            for i in range(len(self.endConnect)):
                if self.endConnect[i] and i < len(self.point):
                    self.c_map.create_line(self.endP, self.point[i], fill="#696969")

        #Make each point more distinguishable
        if self.v_vertex.get() == 2:
            for i in range(len(self.point)):
                self.c_map.create_oval(self.point[i][0] - 2, self.point[i][1] - 2, self.point[i][0] + 2, self.point[i][1] + 2, fill='#ffffff', width=0)
                self.c_map.create_text(self.point[i][0], self.point[i][1] - 4, text=str(self.point[i][0]), anchor=tkinter.S, fill="#ffffff", font=("TkDefaultFont", 7, 'bold'))
                self.c_map.create_text(self.point[i][0], self.point[i][1] + 4, text=str(self.point[i][1]), anchor=tkinter.N, fill="#ffffff", font=("TkDefaultFont", 7, 'bold'))
        elif self.v_vertex.get() == 1:
            for i in range(len(self.point)):
                self.c_map.create_oval(self.point[i][0] - 2, self.point[i][1] - 2, self.point[i][0] + 2, self.point[i][1] + 2, fill='#ffffff', width=0)
                self.c_map.create_text(self.point[i][0], self.point[i][1] + 4, text=i, anchor=tkinter.N, fill="#ffffff", font=("TkDefaultFont", 7, 'bold'))

        # Make start and end point
        if not self.startP == []:
            self.c_map.create_oval(self.startP[0]  - 3, self.startP[1]  - 3, self.startP[0] + 3, self.startP[1] + 3, fill='lightblue', width=0)
            self.c_map.create_text(self.startP[0], self.startP[1] + 5, text=str(self.startP), anchor=tkinter.N, fill="lightblue")

        if not self.endP == []:
            self.c_map.create_oval(self.endP[0]  - 3, self.endP[1]  - 3, self.endP[0] + 3, self.endP[1] + 3, fill='yellow', width = 0)
            self.c_map.create_text(self.endP[0], self.endP[1] + 5, text=str(self.endP), anchor=tkinter.N, fill="yellow")

        if self.v_pathCheck.get():
            # Run Dijkstra if there isn't an already calculated path yet
            if len(self.path) == 0:
                startTime = time.time()
                self.path = dijkstra(self.point, self.pointConnect, self.startP, self.endP, self.startConnect, self.endConnect)
                self.pathTime = time.time() - startTime
                self.distance = 0

                # Find the distance from start to finish
                for i in range(1, len(self.path) - 2):
                    self.distance += (((self.point[self.path[i+1]][0] - self.point[self.path[i]][0]) ** 2 + (self.point[self.path[i+1]][1] - self.point[self.path[i]][1]) ** 2) ** (1/2))

                if len(self.path) == 2:
                    self.distance = ((self.startP[0] - self.endP[0]) ** 2 + (self.startP[1] - self.endP[1]) ** 2) ** (1/2)

                elif len(self.path) > 2:
                    self.distance += ((self.startP[0] - self.point[self.path[1]][0]) ** 2 + (self.startP[1] - self.point[self.path[1]][1]) ** 2) ** (1/2)
                    self.distance += ((self.endP[0] - self.point[self.path[-2]][0]) ** 2 + (self.endP[1] - self.point[self.path[-2]][1]) ** 2) ** (1/2)

            # If there's only 2 points in the path => only start and end point => just draw one line there
            if len(self.path) == 2:   
                self.c_map.create_line(self.startP, self.endP, fill='#fffffe', width=3)
            else:
                for i in range(1, len(self.path) - 2):
                    self.c_map.create_line(self.point[self.path[i]], self.point[self.path[i+1]], fill='#fffffe', width=3)

                if len(self.path) > 2:
                    self.c_map.create_line(self.startP, self.point[self.path[1]], fill='#fffffe', width=3)
                    self.c_map.create_line(self.point[self.path[-2]], self.endP, fill='#fffffe', width=3)

            if self.path == []: 
                self.v_distance.set("Untraversable")
            else:
                self.v_distance.set(str(round(self.distance, 2)) + " pixels")

        self.v_timeGraph.set(str(round(self.graphMapTime + self.graphSETime, 5)) + " seconds")
        self.v_timePath.set(str(round(self.pathTime, 5)) + " seconds")
        self.v_timeTotal.set(str(round(self.graphMapTime + self.graphSETime + self.pathTime, 5)) + " seconds")

    def start_draw_map(self):
        self.clear_map()
        self.previous = []
        self.v_graphCheck.set(0)
        self.v_pathCheck.set(0)
        self.c_map.unbind("<Button-1>")
        self.c_map.unbind("<Button-3>")
        self.c_map.bind("<Button-1>", self.draw_add_point)
        self.c_map.bind("<Button-3>", self.end_draw_map)
        self.v_isDrawing.set("Restart Draw Session")
        self.bt_drawPoly.config(bg='#8c2c2c')

    def end_draw_map(self, event):
        if not event == "force":
            for i in range(len(self.point) - 1):
                if checkIntersect(self.point[0], self.point[-1], self.point[i], self.point[i+1]):
                    return

        self.c_map.unbind("<Button-1>")
        self.c_map.unbind("<Button-3>")
        self.c_map.bind("<Button-1>", self.update_start)
        self.c_map.bind("<Button-3>", self.update_end)
        self.v_isDrawing.set("Start Draw Session")
        self.bt_drawPoly.config(bg='#1c1c1c')

        if not event == "force":
            self.reload_map(code=2)

    def draw_add_point(self, event):
        newVertex = [event.x, event.y]

        # Check if the newly drawn vertex is overlapping the other drawn line
        for i in range(len(self.point) - 1):
            if checkIntersect(newVertex, self.point[-1], self.point[i], self.point[i+1]):
                return
                
        self.point.append(newVertex)

        if len(self.point) > 1:
            self.c_map.create_line(newVertex, self.point[-2], fill="white", width=2)
        self.c_map.create_oval(event.x - 2.5, event.y - 2.5, event.x + 2.5, event.y + 2.5, fill='white', width=0)

    def clear_map(self):
        self.point = []
        self.pointConnect = []
        self.startP = []
        self.startConnect = []
        self.endP = []
        self.endConnect = []

        self.reload_map(code=2)

    def random_map(self):
        height = self.e_height.get()
        width = self.e_width.get()
        if not height.isdigit() or not width.isdigit():
            height = 5
            width = 10
            tkinter.messagebox.showwarning(title="Not Valid Input", message="Map only accept positive integer as dimension values.\n Default values (H = 5, W = 10) have been used instead.")
        else:
            height = int(height)
            width = int(width)

        gapWidth = (CANVAS_WIDTH - 20) / (width * 2)
        gapHeight = (CANVAS_HEIGHT - 10) / (height * 2)
        if self.v_aspect.get():
            gapWidth = min(gapHeight, gapWidth)
            gapHeight = min(gapHeight, gapWidth)
        self.point = Maze.ASCIIMapToVertices(Maze.CreateASCIIMap(height, width), [20, 20], [gapHeight, gapWidth])

        if self.v_autoRun.get():
            self.v_graphCheck.set(1)
            self.v_pathCheck.set(1)
        else:
            self.v_graphCheck.set(0)
            self.v_pathCheck.set(0)

        self.reload_map(code=2)

    def update_start(self, event):
        self.startP = [event.x, event.y]
        self.reload_map(code=1)

    def update_end(self, event):
        self.endP = [event.x, event.y]
        self.reload_map(code=1)

    def export_graph(self):
        self.v_exported.set(str(self.point))
        self.e_exported.focus()
        self.e_exported.select_range(0, tkinter.END)

    def import_graph(self):
        try:
            self.point = ast.literal_eval(self.e_imported.get())
            self.reload_map(code=2)
        except:
            tkinter.messagebox.showwarning(title="Wrong Format", message="The format to import a graph: [[x1, y1],[x2, y2],[x3, y3]] \n Example: [[10, 20][20, 30][30, 10]]")

    def force_evaluation(self):
        self.v_graphCheck.set(1)
        self.v_pathCheck.set(1)
        self.reload_map(code=2)

mainGI = DjikstraGUI()