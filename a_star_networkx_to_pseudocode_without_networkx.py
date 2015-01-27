    __author__ = ["Falitokiniaina Rabearison"]    
    '''
    If you wanto to try without networkx to compute the shortest path, in analysis.py just replace the commented function
    def a_star(self, source, target, distance='cosine'):
    with the ones under it here.
    This new implementation is slower because we need to query a db at each finding the neighbours, I think
    '''
    
    '''
    def a_star(self, source, target, distance='cosine'):
        if distance == 'cosine':
            heuristic = self.heuristicFunctionCosine
        elif distance == 'kl':
            heuristic = self.heuristicFunctionKl
        #path = nx.astar_path(self.nxG, source, target, heuristic)
        #length = sum(self.nxG[u][v].get('weight', 1) for u, v in zip(path[:-1], path[1:]))
        return path, length
    '''

    def get_weight_bewteen(self, from_node1, to_node2):
        query = """SELECT weight
                   FROM {0}
                   WHERE node1={1} AND node2={2}""".format(self.graph.bigraph_norm,from_node1,to_node2)
        return 1-self.graph.sendQuery(query)[0][0]


    def get_next_neighbors(self,node1):
        query = """SELECT node2
                   FROM {0}
                   WHERE node1={1}""" \
                .format(self.graph.bigraph_norm, node1)
        list_neighbors = []
        bad_list_neighbors = self.graph.sendQuery(query)
        for neighbor_tuple in bad_list_neighbors:
            list_neighbors.append(neighbor_tuple[0])
        return list_neighbors

    import operator
    def a_star(self, source, target, distance='cosine'):
        closedset = []      #closedset := the empty set    // The set of nodes already evaluated.
        openset = [source]  #openset := {start}    // The set of tentative nodes to be evaluated, initially containing the start node
        came_from = {}      #came_from := the empty map    // The map of navigated nodes.
        g_score = {}
        f_score = {}

        g_score[source] = 0 #g_score[start] := 0    // Cost from start along best known path.
        # Estimated total cost from start to goal through y.
        if distance == 'cosine':
            f_score[source] = g_score[source] + self.heuristicFunctionCosine(source,target)#f_score[start] := g_score[start] + heuristic_cost_estimate(start, goal)
        elif distance == 'kl':
            f_score[source] = g_score[source] + self.heuristicFunctionKl(source,target)     #f_score[start] := g_score[start] + heuristic_cost_estimate(start, goal)
        #while openset is not empty
        while openset:
            print("Openset : {0}".format(openset))
            #current := the node in openset having the lowest f_score[] value
            temp_f = {}
            for i in openset:
                temp_f[i] = f_score[i]
            current = min(temp_f.items(), key=operator.itemgetter(1))[0]
            #if current = goal
            print("current ={0}".format(current))
            if current == target:
                print(self.reconstruct_path(came_from, target))
                return self.reconstruct_path(came_from, target)

            #remove current from openset
            openset.remove(current)
            #add current to closedset
            closedset.append(current)
            #for each neighbor in neighbor_nodes(current)
            current_neighbors = self.get_next_neighbors(current)
            print("neighbours of the current : {0}".format(current_neighbors))
            for neighbor in current_neighbors:
                #if neighbor in closedset
                if neighbor in closedset:
                    continue
                #tentative_g_score := g_score[current] + dist_between(current,neighbor)
                tentative_g_score = g_score[current] +  self.get_weight_bewteen(current,neighbor)

                #if neighbor not in openset or tentative_g_score < g_score[neighbor]
                if neighbor not in openset or tentative_g_score < g_score[neighbor]:
                    #came_from[neighbor] := current
                    came_from[neighbor] = current
                    #g_score[neighbor] := tentative_g_score
                    g_score[neighbor] = tentative_g_score
                    #f_score[neighbor] := g_score[neighbor] + heuristic_cost_estimate(neighbor, goal)
                    if distance == 'cosine':
                        f_score[neighbor] = g_score[neighbor] + self.heuristicFunctionCosine(neighbor,target)
                    elif distance == 'kl':
                        f_score[neighbor] = g_score[neighbor] + self.heuristicFunctionKl(neighbor,target)
                    #if neighbor not in openset
                    if neighbor not in openset:
                        #add neighbor to openset
                        openset.append(neighbor)
        return print("The target node is not reachable")

    #function reconstruct_path(came_from,current)
    def reconstruct_path(self,came_from,current):
        #total_path := [current]
        total_path = [current]
        #while current in came_from:
        total_weigth = 0
        while current in came_from:
            total_weigth += self.get_weight_bewteen(current,came_from[current])
            #current := came_from[current]
            current = came_from[current]
            total_path.append(current)
        return total_path, total_weigth
