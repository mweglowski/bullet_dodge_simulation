import numpy as np

class QLearningAgent:
    def __init__(self, n_states, n_actions, learning_rate=0.1, discount_rate=0.95, exploration_rate=1.0):
        self.n_states = n_states
        self.n_actions = n_actions
        self.lr = learning_rate
        self.gamma = discount_rate
        self.epsilon = exploration_rate
        self.q_table = np.zeros((n_states, n_actions))

    def choose_action(self, state):
        if np.random.random() < self.epsilon:
            # EXPLORATION
            return np.random.choice(self.n_actions)
        else:
            # EXPLOITATION
            return np.argmax(self.q_table[state])

    def update_q_table(self, state, action, reward, next_state):
        best_next_action = np.argmax(self.q_table[next_state])
        td_target = reward + self.gamma * self.q_table[next_state][best_next_action]
        td_error = td_target - self.q_table[state][action]
        self.q_table[state][action] += self.lr * td_error

    def decay_epsilon(self):
        self.epsilon *= 0.99
