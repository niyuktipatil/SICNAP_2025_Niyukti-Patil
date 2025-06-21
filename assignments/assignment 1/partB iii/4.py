a = input("num1:")
b = input("num2:")
c = input("num3:")

if a > b:
    if a > c:
        print("num1 is the greatest")
    else:
        print("num3 is the greatest")
elif b > c:
    print("num2 is the greatest")
else:
     print("num3 is the greatest")