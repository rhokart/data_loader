numericDict = {
    'A': '1','B': '2','C': '3','D': '4','E': '5','F': '8','G': '3','H': '5','I': '1','J': '1','K': '2','L': '3','M': '4','N': '5',
    'O': '7','P': '8','Q': '1','R': '2','S': '3','T': '4','U': '6','V': '6','W': '6','X': '5','Y': '1','Z': '7'
}

def calculate(ipValue):
    valueString = ipValue.upper()
    compoundValue = 0
    computedString = ''
    result = {}
    isNote = ''
    for ch in valueString:
        if ch != ' ':
            if ch.isnumeric():
                compoundValue = compoundValue + int(ch)
            else:
                charNumber = numericDict.get(ch)
                if charNumber is not None:
                    compoundValue = compoundValue + int(charNumber)
                else:
                    isNote = 'Only alphabets and numerical digits are considered for numerology value calculation as per the Chaldean methodology. Any other type of character is not considered.'

    return compoundValue

class char_calculator:
    def __init__(self):
        pass