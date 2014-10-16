class PriorityQueue:

    queue = {}

    def __init__(self):
        self.queue = {}

    def __len__(self):
        return len(self.queue.keys())

    def __repr__(self):
        return str(self.queue)

    def insert(self, item, score):
        self.queue[score] = item

    def remove(self):
        """Returns and removes item with min score"""
        if self.is_empty():
            item = None
        else:
            scores = self.queue.keys()
            item = self.queue[min(scores)]
            del self.queue[min(scores)]
        return item

    def is_empty(self):
        empty = True
        if self.queue:
            empty = False
        return empty



