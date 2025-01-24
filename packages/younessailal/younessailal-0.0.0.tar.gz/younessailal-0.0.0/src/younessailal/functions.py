list =  [55,6,99,3,10]

def supprimer(list,element=None):
    result = [0] * (len(list) - 1)
    if (element):
        result = [x for x in list if x != element]
    else:
        result = [list[i] for i in range(len(list)-1)]     
    
    return result

# print(supprimer(list))

def ajouter(list,element):
    result = [0]*(len(list)+1)
    
    for i in range(len(list)):
        result [i] = list [i]
    
    result[-1] = element
    
    return result

# print(ajouter(list,"hahaha"))    

def occurence(list,element):
    result = "Not found"
    for i in range(len(list)):
        if list[i] == element:
            result = i
            break
    
    return result


# print(occurence(list,99))
 
 
def trier(list):
    length = len(list)
    for i in range(length):
        for j in range(i+1,length):
            if list[i]>list[j]:
                list[i],list[j] =  list[j],list[i]
    
    return list

 
# print(trier(list)) 

def inverser(list):
    length = len(list)
    for i in range(length//2):
        list[i],list[length-i-1] = list[length-i-1],list[i]
    
    return list

print(inverser(list))