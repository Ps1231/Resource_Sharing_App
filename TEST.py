from collections import deque
import sys
# l1 = [1, 2, 3]
# l2 = deque()
# print(dir(l1))
# print(dir(l2))


# class Stack:
#     def __init__(self):
#         self.container = deque()

#     def push(self, val):
#         self.container.append(val)

#     def peek(self):
#         return self.container[-1] if self.container else None

#     def pop(self):
#         return self.container.pop() if self.container else None

#     def size(self):
#         return len(self.container)
class Stack:
    # Constructor to set the data of
    # the newly created tree node
    def __init__(self, capacity):
        self.capacity = capacity
        self.top = -1
        self.array = [0]*capacity

# function to create a stack of given capacity.


def createStack(capacity):
    stack = Stack(capacity)
    return stack

# Stack is full when top is equal to the last index


def isFull(stack):
    return (stack.top == (stack.capacity - 1))

# Stack is empty when top is equal to -1


def isEmpty(stack):
    return (stack.top == -1)

# Function to add an item to stack.
# It increases top by 1


def push(stack, item):
    if (isFull(stack)):
        return
    stack.top += 1
    stack.array[stack.top] = item

# Function to remove an item from stack.
# It decreases top by 1


def Pop(stack):
    if (isEmpty(stack)):
        return -sys.maxsize
    Top = stack.top
    stack.top -= 1
    return stack.array[Top]


# Create an instance of the Stack class
src = Stack(3)
dest = Stack(3)
aux = Stack(3)
push(src, 1)
push(src, 2)
push(src, 3)
print(src.array[0], src.array[1], src.array[2])

push(dest, src.array[src.top])
Pop(src)

push(aux, src.array[src.top])
Pop(src)

push(aux, dest.array[dest.top])
Pop(dest)

push(dest, src.array[src.top])
Pop(src)

push(src, aux.array[aux.top])
Pop(aux)

push(dest, aux.array[aux.top])
Pop(aux)

push(dest, src.array[src.top])
Pop(src)

print(dest.array[0], dest.array[1], dest.array[2])

# s = "Rashi"
# for i in s:
#     my_stack.push(i)  # Call push on the instance
# k = ""
# print(my_stack.container)
# for i in range(my_stack.size()):

#     k += my_stack.pop()
# print(k)

# from collections import deque


# class Queue:
#     def __init__(self):
#         self.container = deque()

#     def enque(self, vol):
#         self.container.appendleft(vol)

#     def dequeue(self):
#         if len(self.container) == 0:
#             raise IndexError("queue is empty")
#         return self.container.pop()

#     def pop(self):
#         return self.container.pop()

#     def size(self):
#         return len(self.container)


# order = Queue()
# order.enque(input("1st Order"))
# order.enque(input("2st Order"))
# order.enque(input("3st Order"))
# print("Order Size:", order.size())
# while order.size() > 0:
#     order = order.dequeue()
#     print(order)
