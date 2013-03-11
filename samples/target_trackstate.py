class StateMachine(object):

    count = 0

    def __init__(self):
        self.count = 0

    def advance(self):
        self.count += 1

def main():
    sm = StateMachine()
    sm.advance()
    sm.advance()
    sm.advance()
