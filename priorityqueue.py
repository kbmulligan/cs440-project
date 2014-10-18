import Queue

class PriorityQueue:

    queue = None

    def __init__(self):
        self.queue = Queue.PriorityQueue()

    def __len__(self):
        return len(self.queue)

    def __repr__(self):
        return [x for x in self.queue]

    def insert(self, item, score):
        self.queue.put((score, item))

    def remove(self):
        """Returns and removes item with min score"""
        if self.is_empty():
            item = None
            print 'PriorityQueue: Tried to remove from empty queue!'
        else:
            item = self.queue.get()[1]
        return item

    def is_empty(self):
        return self.queue.empty()



if __name__ == '__main':
    q = PriorityQueue()

    q.insert('a', 1)
    q.insert('b', 2)
    q.insert('c', 3)

    q.insert('z', 1)
    q.insert('b', 4)

    print q
    print q.remove()
    print q.remove()
