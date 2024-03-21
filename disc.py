import math
import sys
file_path_DCD = 'DCD.txt'
file_path_EHD = 'EHD.txt'

class Discriminator:
    maxDistDCD = 9999
    maxDistEHD = 9999
    maxDist25 = 9999
    maxDist50 = 9999
    maxDist75 = 9999
    messibestDistDCD = 0
    catDistDCD = 0
    snackDistDCD = 0 
    messibestDistEHD = 0
    catDistEHD = 0
    snackDistEHD = 0
    messi = 0 
    id_DCD = 0
    id_EHD = 0
    id_25 = 0
    id_50 = 0
    id_75 = 0



def readFile(file_path):
    matrix = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
    for line in lines:
        matrix.append(line.split())

    #0 1:NUMBER 2:#DOMCOL 3:%1 4-6:Centroid 7-9:Variance 
    return matrix



def find_query_descriptors(query_descriptor):
    numbers_query = []
    for field in query_descriptor.split():
        numbers_query.append(field)
    return numbers_query



def extract_descriptor_data(descriptor):
    numberOfDominantColors = int(descriptor[2])
    spatialCoherency = float(descriptor[3])
    color_descriptors = []
    for i in range(numberOfDominantColors):
        start_index = 4 + i * 7
        if start_index + 6 >= len(descriptor):
            sys.exit("Error: Not enough elements in the color descriptor. Did you paste it right?")
        else:
            percentage = float(descriptor[start_index])
            centroid_1 = float(descriptor[start_index + 1])
            centroid_2 = float(descriptor[start_index + 2])
            centroid_3 = float(descriptor[start_index + 3])
            variance_1 = float(descriptor[start_index + 4])
            variance_2 = float(descriptor[start_index + 5])
            variance_3 = float(descriptor[start_index + 6])
            color_descriptors.append([percentage, centroid_1, centroid_2, centroid_3, variance_1, variance_2, variance_3])
    return numberOfDominantColors, spatialCoherency, color_descriptors

def extract_color(numberOfDominantColors, color_descriptors):
    color_RGB = []
    for i in range(numberOfDominantColors):
        if len(color_descriptors[i]) >= 4: 
            color_RGB.append([color_descriptors[i][1], color_descriptors[i][2], color_descriptors[i][3]])
    return color_RGB



def euclidean_distance(color1, color2):
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    distance = abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2)
    return distance



def similarity_coefficient(color_query, color_database):
    a = 0
    euclidean = euclidean_distance(color_query, color_database)
    T_d = 15
    alpha = 1.25
    d_max = alpha * T_d
    if euclidean <= T_d:
        a = 1 - (euclidean/ d_max)
    else:
        a = 0
    return a



def manhattan_distance(vector1, vector2):
    vector1 = vector1[2:]
    vector2 = vector2[2:]

    if len(vector1) < len(vector2):
        vector1 += [0] * (len(vector2) - len(vector1))
    elif len(vector2) < len(vector1):
        vector2 += [0] * (len(vector1) - len(vector2))

    distance = 0
    for v1, v2 in zip(vector1, vector2):
        try:
            distance += abs(float(v1) - float(v2))
        except ValueError:
            print(f"Warning: could not convert '{v1}' and/or '{v2}' to float. Skipping these values.")
    return distance/len(vector1)
        



def matching_DCD(numbers_query, line):
    query_numberOfDominantColors, query_spatialCoherency, query_color_descriptors = extract_descriptor_data(numbers_query)
    color_query = extract_color(query_numberOfDominantColors, query_color_descriptors)
    database_numberOfDominantColors, database_spatialCoherency, database_color_descriptors = extract_descriptor_data(line)
    color_database = extract_color(database_numberOfDominantColors, database_color_descriptors)
    percentatge_query = 0
    percentatge_database = 0
    comb = 0
    for i in range(query_numberOfDominantColors):
        percentatge_query += pow(query_color_descriptors[i][0], 2)
    for i in range(database_numberOfDominantColors):
        percentatge_database += pow(database_color_descriptors[i][0], 2)
    for i in range(query_numberOfDominantColors):
        for j in range(database_numberOfDominantColors):
            comb += 2 * similarity_coefficient(color_query[i], color_database[j]) * query_color_descriptors[i][0] * database_color_descriptors[j][0] 
    return math.sqrt(abs(percentatge_query + percentatge_database - comb))



def matchImage(query_descriptor1, query_descriptor2):
    numbers_query1 = find_query_descriptors(query_descriptor1)
    numbers_query2 = find_query_descriptors(query_descriptor2)
    database1 = readFile(file_path_DCD)
    database2 = readFile(file_path_EHD)
    for i, line in enumerate(database1, start=0):
        if (numbers_query1[1] == line[1]):
            continue 
        dcd = matching_DCD(numbers_query1, line)
        ehd = manhattan_distance(numbers_query2, database2[i])
        if(dcd < Discriminator.maxDistDCD):
            Discriminator.maxDistDCD = dcd
            Discriminator.id_DCD = line[1]
        if(ehd < Discriminator.maxDistEHD):
            Discriminator.maxDistEHD = ehd
            Discriminator.id_EHD = database2[i][1]
        if(dcd*0.25 + ehd*0.75 < Discriminator.maxDist25):
            Discriminator.maxDist25 = dcd*0.25 + ehd*0.75
            Discriminator.id_25 = line[1]
        if(dcd*0.50 + ehd*0.50 < Discriminator.maxDist50):
            Discriminator.maxDist50 = dcd*0.50 + ehd*0.50
            Discriminator.id_50 = line[1]
        if(dcd*0.75 + ehd*0.25 < Discriminator.maxDist75):
            Discriminator.maxDist75 = dcd*0.75 + ehd*0.25
            Discriminator.id_75 = line[1]
    print(f"DCD: Poza {Discriminator.id_DCD} is the closest one with the distance {Discriminator.maxDistDCD} /// EHD: Poza{Discriminator.id_EHD} is the closest one with the distance {Discriminator.maxDistEHD}.")
    print(f"25% DCD + 75% EHD: Poza {Discriminator.id_25} is the closest one with the distance {Discriminator.maxDist25}.")
    print(f"50% DCD + 50% EHD: Poza {Discriminator.id_50} is the closest one with the distance {Discriminator.maxDist50}.")
    print(f"75% DCD + 25% EHD: Poza {Discriminator.id_75} is the closest one with the distance {Discriminator.maxDist75}.")

def matchGroup(query_descriptor1, query_descriptor2):
    numbers_query1 = find_query_descriptors(query_descriptor1)
    numbers_query2 = find_query_descriptors(query_descriptor2)
    database1 = readFile(file_path_DCD)
    database2 = readFile(file_path_EHD)

    for i, line in enumerate(database1, start=1):
        if i % 3 == 0:
            Discriminator.snackDistDCD += matching_DCD(numbers_query1, line) / 29
        elif i % 3 == 1:
            Discriminator.messibestDistDCD += matching_DCD(numbers_query1, line) / 29
        else:
            Discriminator.catDistDCD += matching_DCD(numbers_query1, line) / 29
            
    for i, line in enumerate(database2, start=1):
        if i % 3 == 0:
            Discriminator.snackDistEHD += manhattan_distance(numbers_query2, line) / 29
        elif i % 3 == 1:
            Discriminator.messibestDistEHD += manhattan_distance(numbers_query2, line) / 29
        else:
            Discriminator.catDistEHD += manhattan_distance(numbers_query2, line) / 29

    if Discriminator.snackDistDCD < Discriminator.messibestDistDCD and Discriminator.snackDistDCD < Discriminator.catDistDCD:
        print(f"(DCD): It's a desssert! with average distance {Discriminator.snackDistDCD}")
    elif Discriminator.messibestDistDCD < Discriminator.snackDistDCD and Discriminator.messibestDistDCD < Discriminator.catDistDCD:
        print(f"(DCD): It's Messi! with average distance {Discriminator.messibestDistDCD}")
        Discriminator.messi += 1
    else:
        print(f"(DCD): It's a cat! with average distance {Discriminator.catDistDCD}")
    if Discriminator.snackDistEHD < Discriminator.messibestDistEHD and Discriminator.snackDistEHD < Discriminator.catDistEHD:
        print(f"(EHD): It's a desssert! with average distance {Discriminator.snackDistEHD}")
    elif Discriminator.messibestDistEHD < Discriminator.snackDistEHD and Discriminator.messibestDistEHD < Discriminator.catDistEHD:
        print(f"(EHD): It's Messi! with average distance {Discriminator.messibestDistEHD}")
        Discriminator.messi += 1
    else:
        print(f"(EHD): It's a cat! with average distance {Discriminator.catDistEHD}")
    if (Discriminator.snackDistDCD + Discriminator.snackDistEHD) < (Discriminator.messibestDistDCD + Discriminator.messibestDistEHD) and (Discriminator.snackDistDCD + Discriminator.snackDistEHD) < (Discriminator.catDistDCD + Discriminator.catDistEHD):
        print("50% DCD + 50% EHD: It's a dessert!")
    elif (Discriminator.messibestDistDCD + Discriminator.messibestDistEHD) < (Discriminator.snackDistDCD + Discriminator.snackDistEHD) and (Discriminator.messibestDistDCD + Discriminator.messibestDistEHD) < (Discriminator.catDistDCD + Discriminator.catDistEHD):
        print("50% DCD + 50% EHD: It's Messi!")
        Discriminator.messi += 1
    else:
        print("50% DCD + 50% EHD: It's a cat!")
    if Discriminator.messi == 3:
        print("                                                     Barca Barca Baaarca!")



if __name__ == "__main__":
    if len(sys.argv) > 2:
        userinput1 = sys.argv[1]
        userinput2 = sys.argv[2]
        print("///////////////////////////////////////////////////////")
        print("Image matching:")
        matchImage(userinput1, userinput2)
        print("\n")
        print("///////////////////////////////////////////////////////")
        print("Group matching:")
        print("\n")
        matchGroup(userinput1, userinput2)
    else:
        print("Please provide two query descriptors as command-line arguments.")


