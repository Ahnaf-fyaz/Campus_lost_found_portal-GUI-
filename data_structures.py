# ==================== LINKED LIST ====================
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def insert_at_head(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node

    def find_first_by_user(self, username):
        """Return first node whose data['username'] matches."""
        cur = self.head
        while cur:
            if cur.data.get('username') == username:
                return cur
            cur = cur.next
        return None

    def delete_node(self, node_to_delete):
        """Delete a specific node (by reference)."""
        if self.head is None or node_to_delete is None:
            return
        if self.head == node_to_delete:
            self.head = self.head.next
            return
        prev = self.head
        while prev.next and prev.next != node_to_delete:
            prev = prev.next
        if prev.next == node_to_delete:
            prev.next = node_to_delete.next

    def to_list(self):
        """Convert linked list to Python list (for iterating)."""
        result = []
        cur = self.head
        while cur:
            result.append(cur.data)
            cur = cur.next
        return result

    def linear_search(self, room, floor, item_name):
        """Linear search: return first node where room & floor match and item_name is substring."""
        cur = self.head
        while cur:
            d = cur.data
            if d['room'] == room and d['floor'] == floor:
                if item_name.lower() in d['item'].lower() or d['item'].lower() in item_name.lower():
                    return cur
            cur = cur.next
        return None

# ==================== STACK ====================
class StackNode:
    def __init__(self, data):
        self.data = data
        self.next = None

class Stack:
    def __init__(self):
        self.top = None

    def push(self, data):
        node = StackNode(data)
        node.next = self.top
        self.top = node

    def pop(self):
        if self.top is None:
            return None
        data = self.top.data
        self.top = self.top.next
        return data

    def is_empty(self):
        return self.top is None

    def clear(self):
        while not self.is_empty():
            self.pop()

# ==================== QUEUE ====================
class QueueNode:
    def __init__(self, data):
        self.data = data
        self.next = None

class Queue:
    def __init__(self):
        self.front = None
        self.rear = None

    def enqueue(self, data):
        node = QueueNode(data)
        if self.rear is None:
            self.front = self.rear = node
        else:
            self.rear.next = node
            self.rear = node

    def dequeue(self):
        if self.front is None:
            return None
        data = self.front.data
        self.front = self.front.next
        if self.front is None:
            self.rear = None
        return data

    def is_empty(self):
        return self.front is None

    def to_list(self):
        """Convert queue to list (FIFO order)."""
        result = []
        cur = self.front
        while cur:
            result.append(cur.data)
            cur = cur.next
        return result

    def clear(self):
        while not self.is_empty():
            self.dequeue()

# ==================== SORTING & SEARCHING ====================
def bubble_sort(arr, key=lambda x: x):
    """Bubble sort a list in-place (ascending by key)."""
    n = len(arr)
    for i in range(n-1):
        for j in range(0, n-i-1):
            if key(arr[j]) > key(arr[j+1]):
                arr[j], arr[j+1] = arr[j+1], arr[j]

def binary_search(arr, target, key=lambda x: x):
    """Binary search on a sorted list; returns index or -1."""
    left, right = 0, len(arr)-1
    while left <= right:
        mid = (left + right) // 2
        val = key(arr[mid])
        if val == target:
            return mid
        elif val < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1