import logging

logger = logging.getLogger('context_manager')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Create console handler and set level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create file handler and set level
file_handler = logging.FileHandler("log.log")
file_handler.setLevel(logging.DEBUG)

# Create file handler and set level
logger.addHandler(console_handler)
logger.addHandler(file_handler)

class Context:

    def __init__(self):
        self.stack = []
        logger.debug('CREATED: Context manager created.')

    def __str__(self):
        return ".".join(self.stack)

    def __repr__(self):
       return self.__str__()

    def enter(self, name):
        self.stack.append(name)
        logger.debug(f'ENTERED: {self.__str__()}')
    
    def exit(self):
        logger.debug(f'EXITED: {self.__str__()}')
        self.stack.pop()

    def get_parent(self):
        return self.stack[:-1]
    
    def get_self(self):
        return self.stack[len(self.stack)-1]
    
    def get_tree_level(self):
        return len(self.stack)