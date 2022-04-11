class Test():
    def __init__(self) -> None:
        print('Hellow I am a Test')

def test_2(c):
    print('\nTest match')
    match c:
        case 0:
            print('No')
        case Test:
            print('It Worked!!!')



t1 = Test()

print('\nTest normal')
print(t1 is Test)
print(t1 == Test)
print(isinstance(t1, Test))

