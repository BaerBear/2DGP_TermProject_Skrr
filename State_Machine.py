class StateMachine:
    def __init__(self, initial_state):
        self.current_state = initial_state
        self.current_state.enter()

    def change_state(self, new_state):
        pass

    def update(self):
        self.current_state.do()

    def draw(self):
        self.current_state.draw()