
# Stormy appearance
def storm_template(cell):
    
    neigh_sum = template_logic(
            cell,
            value_map={0: 0.75, 1: 0.95, 2: 1.3}
        )
    
    if neigh_sum > 2:
        if neigh_sum <= 3:
            cell.fut_state = (1, 1, neigh_sum-2, 1)
        else:
            cell.fut_state = (0.1, 0.5, 0.1, 1)
    elif neigh_sum > 1.5:
        cell.fut_state = (0, neigh_sum/2, neigh_sum/4, 1)
    elif neigh_sum > 1.2:
        cell.fut_state = (neigh_sum/3-0.1, neigh_sum/2-0.1, neigh_sum/4-0.1, 1)
    elif neigh_sum > 0.5:
        cell.fut_state = (0, neigh_sum/3 - 0.1, neigh_sum/2 - 0.1, 1)
    elif neigh_sum > 0:
        cell.fut_state = (1, 1, 1, 1)
        
    cell.fut_state = tuple([0.6*cell.state[i] + 0.4*cell.fut_state[i] for i in range(4)])
    
def waves_template(cell):
    neigh_sum = template_logic(
            cell,
            value_map={0: 1.5, 1: 0.8, 2: 0.7}
        )
    
    if neigh_sum > 2:
        if neigh_sum <= 3:
            cell.fut_state = (neigh_sum-2, 1, 1, 1)
        else:
            cell.fut_state = (0.1, 0.5, 0.1, 1)
    elif neigh_sum > 1.5:
        cell.fut_state = (0, neigh_sum/2, neigh_sum/4, 1)
    elif neigh_sum > 1.2:
        cell.fut_state = (neigh_sum/3-0.1, neigh_sum/2-0.1, neigh_sum/4-0.1, 1)
    elif neigh_sum > 0.5:
        cell.fut_state = (0.1, neigh_sum/4, neigh_sum - 0.2, 1)
    elif neigh_sum > 0:
        cell.fut_state = (1, 1, 0, 1)
        
    cell.fut_state = tuple([0.1*cell.state[i] + 0.9*cell.fut_state[i] for i in range(4)])
    
# Sandbox template
def sandbox_template(cell):
    neigh_sum = template_logic(
            cell,
            value_map={0: 0.9, 1: 0.8, 2: 0.7}
        )
    
    if neigh_sum > 2:
        if neigh_sum <= 3:
            cell.fut_state = (neigh_sum-2, 1, 1, 1)
        else:
            cell.fut_state = (0.1, 0.5, 0.1, 1)
    elif neigh_sum > 1.5:
        cell.fut_state = (0, neigh_sum/2, neigh_sum/4, 1)
    elif neigh_sum > 1.2:
        cell.fut_state = (neigh_sum/3-0.1, neigh_sum/2-0.1, neigh_sum/4-0.1, 1)
    elif neigh_sum > 0.5:
        cell.fut_state = (0.1, neigh_sum/4, neigh_sum - 0.2, 1)
    elif neigh_sum > 0:
        cell.fut_state = (1, 1, 0, 1)
        
    cell.fut_state = tuple([0.1*cell.state[i] + 0.9*cell.fut_state[i] for i in range(4)])
    
    
def template_logic(cell, value_map):
    neigh_sum = [0]*3
    
    for neighbour in cell.neighbours:
        neigh_sum = [neigh_sum[i] + neighbour.state[i]*value_map[i]/4 for i in range(3)]
    
    neigh_sum = sum(neigh_sum)
    if neigh_sum > 3: print("TOO LARGE!")
    return neigh_sum