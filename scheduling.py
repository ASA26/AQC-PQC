import numpy as np


class Scheduling:
    def __init__(self, number_of_qubits, steps, scheduling):
        self.number_of_qubits = number_of_qubits
        self.number_of_states = 2 ** number_of_qubits
        self.steps = steps
        self.step_size = 1 / steps
        self.scheduling = scheduling


    def search(self, time):
        N = self.number_of_states
        s = 1 + np.tan((2 * time - 1) * np.arctan(np.sqrt(N - 1))) / np.sqrt(N - 1)
        s /= 2
        return s


    def get_lambdas(self):
        lambdas = np.linspace(self.step_size, 1, num=self.steps)

        if self.scheduling == 'search':
            lambdas = list(map(self.search, lambdas))

        return list(lambdas)
