from nao_logger import get_nao_logger

logger = get_nao_logger('nao_context_manager')

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
