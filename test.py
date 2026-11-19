import string
import random
import char_calculator
import csv

def name_generator():
    name_dict = {}
# using random.choices() generating random strings
    for i in range(10000000000):
        res = ''.join(random.choices(string.ascii_letters,
                                     k=6)) # initializing size of string
        gen_str = str(res).upper()
        if name_dict.get(gen_str) is None:
            calculate_val  = char_calculator.calculate(gen_str)
            if calculate_val == 32:
                print(gen_str)
                name_dict.update({gen_str: calculate_val})

        if len(name_dict) == 10000:
            break

    return name_dict

if __name__ == '__main__':
    name_dict  = name_generator()
    for key,val in name_dict:
        print(key)

