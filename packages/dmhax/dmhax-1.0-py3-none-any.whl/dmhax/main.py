def get_help():
    print("""
    -> get_transactions()
    -> get_gender()
    -> get_sum_of_plane()
    -> get_slice()
    -> get_slice_x()
    -> get_slice_y()
    -> get_slice_z()
    -> get_dice()
    -> get_dice_x()
    -> get_dice_y()
    -> get_dice_z()
    -> get_apriori()
    -> get_partition()
    -> get_fp_growth()
    """)


# Input data for transactions.txt
def get_transactions():
    data = '''[Put these inside transactions.txt]

1,5,6,8
2,4,8
4,5,7
2,3
5,6,7
2,3,4
2,6,7,9
5
8
3,5,7
3,5,7
5,6,8
2,4,6,7
1,3,5,7
2,3,9
'''
    print(data)


# Get sum of first plane
def get_sum_of_plane():
    code = '''
def pretty_print(data_cube, x_axis, y_axis, z_axis, field_width = 5):
for i in range(x_axis):
    print(f"----------- Layer-X[{i}] -------------")        
    for j in range(y_axis):
        row_data = "  ".join(f"{data_cube[i][j][k]:>{field_width}}" for k in range(z_axis))
        print(f"Y[{j}]: {row_data}")
    print()  

x = int(input("Enter the dimension x: "))
y = int(input("Enter the dimension y: "))
z = int(input("Enter the dimension z: "))

datacube = [[[0 for _ in range(z)] for _ in range(y)] for _ in range(x)]

print("Enter the data:")
for i in range(x):
    for j in range(y):
        for k in range(z):
            datacube[i][j][k] = int(input(f"Enter value for a[{i}][{j}][{k}]: "))

print("\\nThe entered cube is:")
pretty_print(datacube, x, y, z)

sum_first_plane = 0
print("Data in the first plane:")
for j in range(y):
    for k in range(z):
        print(datacube[0][j][k], end="\\t")
        sum_first_plane += datacube[0][j][k]
    print()
print(f"\\nThe sum in the first plane is: {sum_first_plane}")
'''
    print(code)



def get_gender_slice():
    code = '''
def pretty_print(data_cube, x_axis, y_axis, z_axis, field_width = 5):
    for i in range(x_axis):
        print(f"----------- Layer-X[{i}] -------------")        
        for j in range(y_axis):
            row_data = "  ".join(f"{data_cube[i][j][k]:>{field_width}}" for k in range(z_axis))
            print(f"Y[{j}]: {row_data}")
        print()

def sliced_view(sliced_array, caption, rowdata_alignment = "left", field_width = 6):
    X = len(sliced_array)    
    Y = len(sliced_array[0])

    print(caption)
    print("-" * (field_width * Y + X))

    if rowdata_alignment.lower() == "right":
        for i in range(X):
            row_data = "  ".join(f"{item:>{field_width}}" for item in sliced_array[i])
            print(row_data)
    else:
        for i in range(X):
            row_data = "  ".join(f"{item:<{field_width}}" for item in sliced_array[i])
            print(row_data)
    print("-" * (field_width * Y + X))


def slice_by_gender(data_cube, gender):
    gender = gender.lower()
    sex = {
        "male": 0,
        "female": 1
    }

    sliced = []
    for x in range(len(data_cube)):
        row = []
        for y in range(len(data_cube[x])):
            row.append(data_cube[x][y][sex[gender]])
        sliced.append(row)
    return sliced


X , Y, Z = 7, 4, 2

data_cube = [
    [[2017, 2017], [2018, 2018], [2019, 2019], [2020, 2020]],
    [[150, 145],   [140, 138],   [130, 132],   [145, 140]],
    [[170, 155],   [160, 146],   [145, 142],   [130, 148]],
    [[130, 120],   [120, 115],   [125, 130],   [135, 125]],
    [[160, 150],   [130, 140],   [145, 140],   [140, 145]],
    [[110, 90],    [100, 85],    [95, 75],     [105, 80]],
    [[125, 120],   [110, 105],   [110, 120],   [115, 90]]]


pretty_print(data_cube, X, Y, Z)
parameter = input("Enter gender to slice:  ").lower()

match parameter:
    case "male": 
        male = slice_by_gender(data_cube, "male")
        sliced_view(male, "Male Slice, i.e., (Z = 0):", "right")

    case "female": 
        female = slice_by_gender(data_cube, "female")
        sliced_view(female, "Female Slice, i.e., (Z = 1):", "right")

    case _: print("Invalid Choice!")
'''
    print(code)

# Slicing Menu
def get_slice():
    code = '''
def pretty_print(data_cube, x_axis, y_axis, z_axis, field_width = 5):
    for i in range(x_axis):
        print(f"----------- Layer-X[{i}] -------------")        
        for j in range(y_axis):
            row_data = "  ".join(f"{data_cube[i][j][k]:>{field_width}}" for k in range(z_axis))
            print(f"Y[{j}]: {row_data}")
        print()  


def slice_cube(datacube, axis, slice_index, x, y, z):
    axes = {
        1: "X-axis",
        2: "Y-axis",
        3: "Z-axis"
    }

    if  (axis == 1 and 0 <= slice_index < x) or \\
        (axis == 2 and 0 <= slice_index < y) or \\
        (axis == 3 and 0 <= slice_index < z):

        print(f"\\nSlice along {axes[axis]}:")

        if axis == 1:  
            for j in range(y):
                print("\\t".join(str(datacube[slice_index][j][k]) for k in range(z)))
        elif axis == 2:  
            for i in range(x):
                print("\\t".join(str(datacube[i][slice_index][k]) for k in range(z)))
        elif axis == 3:  
            for i in range(x):
                print("\\t".join(str(datacube[i][j][slice_index]) for j in range(y)))
    else:
        print("Invalid slice index for the chosen axis.")


def slice_menu(datacube, x, y, z):
    print("Choose the Slicing Operation: ")
    print("1. Along X-axis")
    print("2. Along Y-axis")
    print("3. Along Z-axis")

    axis = int(input("Enter your choice:  "))
    match axis:
        case 1:
            print("You have selected Slicing along X-axis!")
            slice_index = int(input(f"Select a slice index (0 to {x}): "))
            slice_cube(datacube, axis, slice_index, x, y, z)
        case 2:
            print("You have selected Slicing along Y-axis!")
            slice_index = int(input(f"Select a slice index (0 to {y}): "))
            slice_cube(datacube, axis, slice_index, x, y, z)
        case 3:
            print("You have selected Slicing along Z-axis!")
            slice_index = int(input(f"Select a slice index (0 to {z}): "))
            slice_cube(datacube, axis, slice_index, x, y, z)
        case _:
            print("Invalid axis choice. Please select 1, 2, or 3.")


data_cube = [
    [[ 1,  2,  3], [ 4,  5,  6], [ 7,  8,  9]],
    [[10, 11, 12], [13, 14, 15], [16, 17, 18]],
    [[19, 20, 21], [22, 23, 24], [25, 26, 27]]
]

x, y, z = len(data_cube), len(data_cube[0]), len(data_cube[0][0])
pretty_print(data_cube, x, y, z)
slice_menu(data_cube, x, y, z)
'''
    print(code)


def get_slice_x():
    code = '''
def pretty_print(data_cube, x_axis, y_axis, z_axis, field_width = 5):
    for i in range(x_axis):
        print(f"----------- Layer-X[{i}] -------------")        
        for j in range(y_axis):
            row_data = "  ".join(f"{data_cube[i][j][k]:>{field_width}}" for k in range(z_axis))
            print(f"Y[{j}]: {row_data}")
        print() 

def slice_x(datacube, x, y, z):
    print("Slice along X-axis!")
    slice_index = int(input(f"Select a slice index (0 to {x}): "))
    
    if(0 <= slice_index < x):
        for j in range(y):
            print("\\t".join(str(datacube[slice_index][j][k]) for k in range(z)))
    else:
        print("Invalid slice index for the chosen axis.")

data_cube = [
    [[ 1,  2,  3], [ 4,  5,  6], [ 7,  8,  9]],
    [[10, 11, 12], [13, 14, 15], [16, 17, 18]],
    [[19, 20, 21], [22, 23, 24], [25, 26, 27]]
]

x, y, z = len(data_cube), len(data_cube[0]), len(data_cube[0][0])
pretty_print(data_cube, x, y, z)
slice_x(data_cube, x, y, z)
'''
    print(code)



def get_slice_y():
    code = '''
def pretty_print(data_cube, x_axis, y_axis, z_axis, field_width = 5):
    for i in range(x_axis):
        print(f"----------- Layer-X[{i}] -------------")        
        for j in range(y_axis):
            row_data = "  ".join(f"{data_cube[i][j][k]:>{field_width}}" for k in range(z_axis))
            print(f"Y[{j}]: {row_data}")
        print() 

def slice_y(datacube, x, y, z):
    print("Slice along Y-axis!")
    slice_index = int(input(f"Select a slice index (0 to {y}): "))
    
    if(0 <= slice_index < y):
        for i in range(x):
            print("\\t".join(str(datacube[i][slice_index][k]) for k in range(z)))
    else:
        print("Invalid slice index for the chosen axis.")

data_cube = [
    [[ 1,  2,  3], [ 4,  5,  6], [ 7,  8,  9]],
    [[10, 11, 12], [13, 14, 15], [16, 17, 18]],
    [[19, 20, 21], [22, 23, 24], [25, 26, 27]]
]

x, y, z = len(data_cube), len(data_cube[0]), len(data_cube[0][0])
pretty_print(data_cube, x, y, z)
slice_y(data_cube, x, y, z)
'''
    print(code)



def get_slice_z():
    code = '''
def pretty_print(data_cube, x_axis, y_axis, z_axis, field_width = 5):
    for i in range(x_axis):
        print(f"----------- Layer-X[{i}] -------------")        
        for j in range(y_axis):
            row_data = "  ".join(f"{data_cube[i][j][k]:>{field_width}}" for k in range(z_axis))
            print(f"Y[{j}]: {row_data}")
        print() 

def slice_z(datacube, x, y, z):
    print("Slice along Z-axis!")
    slice_index = int(input(f"Select a slice index (0 to {z}): "))
    
    if(0 <= slice_index < z):
        for i in range(x):
            print("\\t".join(str(datacube[i][j][slice_index]) for j in range(y)))
    else:
        print("Invalid slice index for the chosen axis.")

data_cube = [
    [[ 1,  2,  3], [ 4,  5,  6], [ 7,  8,  9]],
    [[10, 11, 12], [13, 14, 15], [16, 17, 18]],
    [[19, 20, 21], [22, 23, 24], [25, 26, 27]]
]

x, y, z = len(data_cube), len(data_cube[0]), len(data_cube[0][0])
pretty_print(data_cube, x, y, z)
slice_z(data_cube, x, y, z) 
'''
    print(code)



# Dicing Menu
def get_dice():
    code = '''
def pretty_print(data_cube, x_axis, y_axis, z_axis, field_width = 5):
    for i in range(x_axis):
        print(f"----------- Layer-X[{i}] -------------")        
        for j in range(y_axis):
            row_data = "  ".join(f"{data_cube[i][j][k]:>{field_width}}" for k in range(z_axis))
            print(f"Y[{j}]: {row_data}")
        print()  

def dice_cube(datacube, axis, start_index, end_index, x, y, z, field_width=5):
    axes = { 1: "X-axis", 2: "Y-axis", 3: "Z-axis" }

    if (axis == 1 and 0 <= start_index < end_index <= x) or \\
       (axis == 2 and 0 <= start_index < end_index <= y) or \\
       (axis == 3 and 0 <= start_index < end_index <= z):
    
        print(f"\\nSubcube along {axes[axis]} (from index {start_index} to {end_index}):")
        
        if axis == 1:  
            for j in range(y):
                for k in range(z):
                    row_data = "  ".join(f"{datacube[i][j][k]:>{field_width}}" for i in range(start_index, end_index + 1))
                    print(f"Y[{j}] Z[{k}] : {row_data}")
                print()

        elif axis == 2:  
            for i in range(x):
                for k in range(z):
                    row_data = "  ".join(f"{datacube[i][j][k]:>{field_width}}" for j in range(start_index, end_index + 1))
                    print(f"X[{i}] Z[{k}] : {row_data}")
                print()

        elif axis == 3:  
            for i in range(x):
                for j in range(y):
                    row_data = "  ".join(f"{datacube[i][j][k]:>{field_width}}" for k in range(start_index, end_index + 1))
                    print(f"X[{i}] Y[{j}] : {row_data}")
                print()
                
        else:
            print("Invalid range for the dicing operation.")
    else:
        print("Invalid range for the dicing operation.")


def dice_menu(datacube, x, y, z):
    print("Choose the Dicing Operation: ")
    print("1. Along X-axis")
    print("2. Along Y-axis")
    print("3. Along Z-axis")
    axis = int(input("Enter your choice:  "))

    match axis:
        case 1:
            print("You have selected Dicing along X-axis!")
            start_index = int(input(f"Select the starting index for the slice (0 to {x-1}): "))
            end_index = int(input(f"Select the ending index for the slice (starting from {start_index} to {x-1}): "))
            if 0 <= start_index < end_index < x:
                dice_cube(datacube, axis, start_index, end_index, x, y, z)
            else:
                print("Invalid indices. Please ensure 0 <= start_index < end_index < x.")

        case 2:
            print("You have selected Dicing along Y-axis!")
            start_index = int(input(f"Select the starting index for the slice (0 to {y-1}): "))
            end_index = int(input(f"Select the ending index for the slice (starting from {start_index} to {y-1}): "))
            if 0 <= start_index < end_index < y:
                dice_cube(datacube, axis, start_index, end_index, x, y, z)
            else:
                print("Invalid indices. Please ensure 0 <= start_index < end_index < y.")

        case 3:
            print("You have selected Dicing along Z-axis!")
            start_index = int(input(f"Select the starting index for the slice (0 to {z-1}): "))
            end_index = int(input(f"Select the ending index for the slice (starting from {start_index} to {z-1}): "))
            if 0 <= start_index < end_index < z:
                dice_cube(datacube, axis, start_index, end_index, x, y, z)
            else:
                print("Invalid indices. Please ensure 0 <= start_index < end_index < z.")

        case _:
            print("Invalid axis choice. Please select 1, 2, or 3.")


data_cube = [
    [[ 1,  2,  3], [ 4,  5,  6], [ 7,  8,  9]],
    [[10, 11, 12], [13, 14, 15], [16, 17, 18]],
    [[19, 20, 21], [22, 23, 24], [25, 26, 27]]
]

x, y, z = len(data_cube), len(data_cube[0]), len(data_cube[0][0])
pretty_print(data_cube, x, y, z)
dice_menu(data_cube, x, y, z)
'''
    print(code)


def get_dice_x():
    code = '''
def pretty_print(data_cube, x_axis, y_axis, z_axis, field_width = 5):
    for i in range(x_axis):
        print(f"----------- Layer-X[{i}] -------------")        
        for j in range(y_axis):
            row_data = "  ".join(f"{data_cube[i][j][k]:>{field_width}}" for k in range(z_axis))
            print(f"Y[{j}]: {row_data}")
        print()  

def dice_x(datacube, x, y, z, field_width=5):
    print("Dicing along X-axis!")
    start_index = int(input(f"Select the starting index for the slice (0 to {x-1}): "))
    end_index = int(input(f"Select the ending index for the slice (starting from {start_index} to {x-1}): "))

    if(0 <= start_index < end_index <= x):
        print(f"\\nSubcube along X-axis (from index {start_index} to {end_index}):")
        for j in range(y):
            for k in range(z):
                row_data = "  ".join(f"{datacube[i][j][k]:>{field_width}}" for i in range(start_index, end_index + 1))
                print(f"Y[{j}] Z[{k}] : {row_data}")
            print()
    else:
        print("Invalid range for the dicing operation.")

data_cube = [
    [[ 1,  2,  3], [ 4,  5,  6], [ 7,  8,  9]],
    [[10, 11, 12], [13, 14, 15], [16, 17, 18]],
    [[19, 20, 21], [22, 23, 24], [25, 26, 27]]
]

x, y, z = len(data_cube), len(data_cube[0]), len(data_cube[0][0])
pretty_print(data_cube, x, y, z)
dice_x(data_cube, x, y, z)
'''
    print(code)




def get_dice_y():
    code = '''
def pretty_print(data_cube, x_axis, y_axis, z_axis, field_width = 5):
    for i in range(x_axis):
        print(f"----------- Layer-X[{i}] -------------")        
        for j in range(y_axis):
            row_data = "  ".join(f"{data_cube[i][j][k]:>{field_width}}" for k in range(z_axis))
            print(f"Y[{j}]: {row_data}")
        print()  

def dice_y(datacube, x, y, z, field_width=5):
    print("Dicing along Y-axis!")
    start_index = int(input(f"Select the starting index for the slice (0 to {y-1}): "))
    end_index = int(input(f"Select the ending index for the slice (starting from {start_index} to {y-1}): "))

    if(0 <= start_index < end_index <= y):
        print(f"\\nSubcube along Y-axis (from index {start_index} to {end_index}):")
        for i in range(x):
            for k in range(z):
                row_data = "  ".join(f"{datacube[i][j][k]:>{field_width}}" for j in range(start_index, end_index + 1))
                print(f"X[{i}] Z[{k}] : {row_data}")
            print()
    else:
        print("Invalid range for the dicing operation.")

data_cube = [
    [[ 1,  2,  3], [ 4,  5,  6], [ 7,  8,  9]],
    [[10, 11, 12], [13, 14, 15], [16, 17, 18]],
    [[19, 20, 21], [22, 23, 24], [25, 26, 27]]
]

x, y, z = len(data_cube), len(data_cube[0]), len(data_cube[0][0])
pretty_print(data_cube, x, y, z)
dice_y(data_cube, x, y, z)
'''
    print(code)



def get_dice_z():
    code = '''
def pretty_print(data_cube, x_axis, y_axis, z_axis, field_width = 5):
    for i in range(x_axis):
        print(f"----------- Layer-X[{i}] -------------")        
        for j in range(y_axis):
            row_data = "  ".join(f"{data_cube[i][j][k]:>{field_width}}" for k in range(z_axis))
            print(f"Y[{j}]: {row_data}")
        print()  

def dice_z(datacube, x, y, z, field_width=5):
    print("Dicing along Z-axis!")
    start_index = int(input(f"Select the starting index for the slice (0 to {z-1}): "))
    end_index = int(input(f"Select the ending index for the slice (starting from {start_index} to {z-1}): "))

    if(0 <= start_index < end_index <= z):
        print(f"\\nSubcube along Z-axis (from index {start_index} to {end_index}):")
        for i in range(x):
            for j in range(y):
                row_data = "  ".join(f"{datacube[i][j][k]:>{field_width}}" for k in range(start_index, end_index + 1))
                print(f"X[{i}] Y[{j}] : {row_data}")
            print()
    else:
        print("Invalid range for the dicing operation.")

data_cube = [
    [[ 1,  2,  3], [ 4,  5,  6], [ 7,  8,  9]],
    [[10, 11, 12], [13, 14, 15], [16, 17, 18]],
    [[19, 20, 21], [22, 23, 24], [25, 26, 27]]
]

x, y, z = len(data_cube), len(data_cube[0]), len(data_cube[0][0])
pretty_print(data_cube, x, y, z)
dice_z(data_cube, x, y, z)
'''
    print(code)




def get_apriori():
    code = '''
from itertools import combinations
from collections import defaultdict

def read_transactions(file_path):
    transactions = []
    with open(file_path, 'r') as file:
        for line in file:
            transaction = line.strip().split(',')
            transactions.append(set(transaction))
    return transactions

def get_itemsets(transactions, length):
    items = set(item for transaction in transactions for item in transaction)
    return set(combinations(items, length))

def calculate_support(transactions, itemsets):
    support_count = defaultdict(int)
    for transaction in transactions:
        for itemset in itemsets:
            if set(itemset).issubset(transaction):
                support_count[itemset] += 1
    return support_count

def apriori(transactions, min_support):
    length = 1
    frequent_itemsets = []
    candidate_itemsets = get_itemsets(transactions, length)
   
    while candidate_itemsets:
        print(f"\\n=== Generating itemsets of length {length} ===")
        support_count = calculate_support(transactions, candidate_itemsets)
        current_frequent = {itemset: count for itemset, count in support_count.items() if count >= min_support}
        if not current_frequent:
            break

        frequent_itemsets.extend(current_frequent.keys())
       
        print(f"Frequent Itemsets of Length {length}: ")
        for itemset, count in current_frequent.items():
            print(f"{str(itemset):<{(10*length) + 3}} -> Support: {count}")

        candidate_itemsets = set(combinations(
            set(item for itemset in current_frequent.keys() for item in itemset), length + 1))
        length += 1

    return frequent_itemsets

if __name__ == "__main__":
    file_path = "transactions.txt"
    min_support = 3
    transactions = read_transactions(file_path)

    print("=== Apriori Algorithm ===")
    frequent_itemsets = apriori(transactions, min_support)

    print("\\n===== Results =====")
    print("Frequent Itemsets:")
    for itemset in frequent_itemsets:
        print(itemset) 
'''
    print(code)




def get_partition():
    code = '''
from itertools import combinations
from collections import defaultdict

def read_transactions(file_path):
    with open(file_path, 'r') as file:
        transactions = [line.strip().split(",") for line in file]
    return transactions

def get_frequent_itemsets(transactions, min_support):
    item_counts = defaultdict(int)
    for transaction in transactions:
        for item in transaction:
            item_counts[frozenset([item])] += 1

    frequent_itemsets = {itemset for itemset, count in item_counts.items() if count >= min_support}
    frequent_items_support = {itemset: count for itemset, count in item_counts.items() if count >= min_support}

    k = 2
    while frequent_itemsets:
        candidates = set()
        for itemset1 in frequent_itemsets:
            for itemset2 in frequent_itemsets:
                union_set = itemset1 | itemset2
                if len(union_set) == k:
                    candidates.add(union_set)

        candidate_counts = defaultdict(int)
        for transaction in transactions:
            transaction_set = frozenset(transaction)
            for candidate in candidates:
                if candidate.issubset(transaction_set):
                    candidate_counts[candidate] += 1

        frequent_itemsets = {itemset for itemset, count in candidate_counts.items() if count >= min_support}
        frequent_items_support.update({itemset: count for itemset, count in candidate_counts.items() if count >= min_support})
        k += 1

    return frequent_items_support

def partition_algorithm(file_path, min_support, num_partitions=2):
    transactions = read_transactions(file_path)
    partition_size = len(transactions) // num_partitions
    partitions = [transactions[i * partition_size: (i + 1) * partition_size] for i in range(num_partitions)]

    local_frequent_itemsets = []
    for partition in partitions:
        local_frequent_itemsets.append(get_frequent_itemsets(partition, min_support // num_partitions))

    global_candidates = set()
    for itemsets in local_frequent_itemsets:
        global_candidates.update(itemsets.keys())

    global_counts = defaultdict(int)
    for transaction in transactions:
        transaction_set = frozenset(transaction)
        for candidate in global_candidates:
            if candidate.issubset(transaction_set):
                global_counts[candidate] += 1

    globally_frequent_itemsets = {itemset: count for itemset, count in global_counts.items() if count >= min_support}

    return globally_frequent_itemsets

file_path = "transactions.txt"
min_support = 3     # Minimum support count
num_partitions = 3  # Number of partitions
frequent_itemsets = partition_algorithm(file_path, min_support, num_partitions)

print(f"{"Frequent Itemsets":<18} | Support")
print("-" * 28)
for itemset, support in frequent_itemsets.items():
    print(f"{str(set(itemset)):<18} : {support}")
'''
    print(code)




def get_fp_growth():
    code = '''
from collections import defaultdict

class TreeNode:
    def __init__(self, name, count, parent):
        self.name = name
        self.count = count
        self.parent = parent
        self.children = {}
        self.link = None

    def increment(self, count):
        self.count += count

def build_fptree(transactions, min_support):
    item_counts = defaultdict(int)
    for transaction in transactions:
        for item in transaction:
            item_counts[item] += 1

    item_counts = {k: v for k, v in item_counts.items() if v >= min_support}
    if not item_counts:
        return None, None

    sorted_transactions = []
    for transaction in transactions:
        filtered = [item for item in transaction if item in item_counts]
        sorted_transactions.append(sorted(filtered, key=lambda x: -item_counts[x]))

    root = TreeNode("root", 1, None)
    header_table = {item: None for item in item_counts}

    for transaction in sorted_transactions:
        current_node = root
        for item in transaction:
            if item not in current_node.children:
                new_node = TreeNode(item, 0, current_node)
                current_node.children[item] = new_node

                if header_table[item] is None:
                    header_table[item] = new_node
                else:
                    current = header_table[item]
                    while current.link is not None:
                        current = current.link
                    current.link = new_node

            current_node = current_node.children[item]
            current_node.increment(1)

    return root, header_table

def find_patterns(header_table, min_support):
    frequent_itemsets = []

    def mine_tree(node, suffix):
        itemset = suffix + [node.name]
        frequent_itemsets.append((itemset, node.count))

        for child in node.children.values():
            mine_tree(child, itemset)

    for item, node in header_table.items():
        while node is not None:
            mine_tree(node, [])
            node = node.link

    return frequent_itemsets

def fp_growth(transactions, min_support):
    tree, header_table = build_fptree(transactions, min_support)
    if not tree:
        return []

    return find_patterns(header_table, min_support)

def read_transactions(file_name):
    with open(file_name, "r") as file:
        return [line.strip().split(",") for line in file.readlines()]

min_support = 3
input_file = "transactions.txt"
transactions = read_transactions(input_file)
frequent_itemsets = fp_growth(transactions, min_support)

print("Frequent Itemsets:")
for itemset, support in frequent_itemsets:
    print(f"Itemset: {str(set(itemset)):<22} -> Support: {support}")
'''
    print(code)