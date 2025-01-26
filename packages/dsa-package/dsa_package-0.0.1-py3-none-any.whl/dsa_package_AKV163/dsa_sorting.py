class DSA:
    def __init__(self):
        pass

    def bubble_sort(self,array:list)->list:

        for i in range(0,len(array)-1):
            for j in range(0,len(array)-1):
                if array[j]>array[j+1]:
                    temp = array[j+1]
                    array[j+1] = array[j]
                    array[j] = temp 
        return array
    
    def insertion_sort(self):
        pass

    def selection_sort(self):
        pass


sorting = DSA()







