class StateMachine:
    def __init__(self, start_state, rules):
        self.current_state = start_state
        self.rules = rules
        self.current_state.enter(('START', None))

    def change_state(self, new_state):
        self.current_state.exit()
        self.current_state = new_state
        self.current_state.enter()

    def update(self):
        self.current_state.do()

    def draw(self):
        self.current_state.draw()

    def handle_event(self, state_event):
        for check_event in self.rules[self.current_state].keys():
            if check_event(state_event):
                next_state = self.rules[self.current_state][check_event]
                print(f'State Change: {self.current_state.__class__.__name__} -> {next_state.__class__.__name__}')
                self.current_state.exit(state_event)
                self.current_state = next_state
                self.current_state.enter(state_event)
                return True
        return False