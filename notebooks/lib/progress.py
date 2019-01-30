#######################################
## Progress Bar Class
#######################################


class Progress:
    # Class Attributes
    progress_character = '*'
    
     # Initializer / Instance Attributes
    def __init__(self, expected_max, increments):
        self.expected_max = expected_max
        self.increments = increments
        self.increment_size = int(expected_max / increments)
        self.count = 0
        
    # instance method
    def increase(self):
        self.count += 1
        if self.count % self.increment_size == 0:
            print(self.progress_character, ' ', sep='', end='')