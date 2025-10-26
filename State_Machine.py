class StateMachine:
    def __init__(self, start_state, rules):
        self.cur_state = start_state
        self.rules = rules
        self.cur_state.enter(('START', None))

    def __init__(self, initial_state):
        self.current_state = initial_state
        self.current_state.enter()

    def change_state(self, new_state):
        self.current_state.exit()
        self.current_state = new_state
        self.current_state.enter()

    def update(self):
        self.cur_state.do()

    def draw(self):
        self.cur_state.draw()

    def handle_event(self, state_event):
        for check_event in self.rules[self.cur_state].keys():
            if check_event(state_event):
                next_state = self.rules[self.cur_state][check_event]
                print(f'State Change: {self.cur_state.__class__.__name__} -> {next_state.__class__.__name__}')
                self.cur_state.exit(state_event)
                self.cur_state = next_state
                self.cur_state.enter(state_event)
                return True
        return False