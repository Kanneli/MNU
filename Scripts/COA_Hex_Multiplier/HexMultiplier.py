num_one = input('Enter a hex value: ').strip()
num_two = input('Enter another hex value: ').strip()
result = []
answer = ''

def hexToInt(digit):
    if digit.isdigit(): return int(digit)
    return ord(digit.upper()) - 55

def intToHex(digit):
    if digit < 10: return str(digit)
    return chr(digit + 55)

def hexMultiply(digit_one, digit_two, pos):
    mult = digit_one * digit_two
    addToPlace(mult % 16, pos)
    if mult > 15:
        addToPlace(int(mult / 16), pos + 1)

def addToPlace(num, pos):
    if len(result) < pos + 1: result.append(0)
    result[pos] += num
    if result[pos] > 15:
        result[pos] = result[pos] % 16
        addToPlace(1, pos + 1) 

increment = 0
for digit_two in num_two[::-1]:
    count = increment
    digit_two = hexToInt(digit_two)
    for digit_one in num_one[::-1]:
        digit_one = hexToInt(digit_one)
        hexMultiply(digit_one, digit_two, count)
        count += 1
    increment += 1

for digit in result[::-1]:
    answer += intToHex(digit)
print(answer)