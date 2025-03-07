from qiskit.visualization import *
import numpy as np
import scipy.optimize as optimize
import networkx as nx
import collections
from hamiltonian import Hamiltonian
from quantum_circuit import QCir
from qiskit.quantum_info import Statevector
from sympy import Matrix


class AQC_PQC():
    def __init__(self, number_of_qubits, problem, steps, layers, single_qubit_gates, entanglement_gates, entanglement, use_third_derivatives = False, use_null_space = False, use_null_derivatives = False):

        self.number_of_qubits = number_of_qubits
        self.problem = problem
        self.steps = steps
        self.layers = layers
        self.single_qubit_gates = single_qubit_gates
        self.entanglement_gates = entanglement_gates
        self.entanglement = entanglement
        self.use_null_space = use_null_space
        self.use_null_derivatives = use_null_derivatives

        qcir = QCir(self.number_of_qubits, 'initial', self.layers, self.single_qubit_gates, self.entanglement_gates, self.entanglement)

        self.initial_parameters = qcir.get_initial_parameters()
        self.number_of_parameters = len(self.initial_parameters)

        hamiltonians = Hamiltonian(self.number_of_qubits, self.problem)

        self.offset = hamiltonians.get_offset()
        self.initial_hamiltonian = hamiltonians.construct_initial_hamiltonian()
        self.target_hamiltonian = hamiltonians.construct_problem_hamiltonian()


    def get_expectation_value(self, angles, observable):
        circuit = QCir(self.number_of_qubits, angles, self.layers, self.single_qubit_gates, self.entanglement_gates, self.entanglement)
        sv1 = Statevector.from_label('0'*self.number_of_qubits)
        sv1 = sv1.evolve(circuit.qcir)
        expectation_value = sv1.expectation_value(observable)
        return np.real(expectation_value)
    
    def get_derivative(self, observable, which_parameter, parameters):

        derivative = 0
        parameters_plus, parameters_minus = parameters.copy(), parameters.copy()
        parameters_plus[which_parameter] += np.pi/2
        parameters_minus[which_parameter] -= np.pi/2

        derivative += 1/2*self.get_expectation_value(parameters_plus, observable)
        derivative -= 1/2*self.get_expectation_value(parameters_minus, observable)
        
        return derivative
    
    def get_hessian_matrix(self, observable, angles):

        hessian = np.zeros((self.number_of_parameters, self.number_of_parameters))
    
        for parameter1 in range(self.number_of_parameters):
            for parameter2 in range(self.number_of_parameters):
                if parameter1 < parameter2:    
                    
                    hessian_thetas_1, hessian_thetas_2, hessian_thetas_3, hessian_thetas_4 = angles.copy(), angles.copy(), angles.copy(), angles.copy()

                    hessian_thetas_1[parameter1] += np.pi/2
                    hessian_thetas_1[parameter2] += np.pi/2


                    hessian_thetas_2[parameter1] -= np.pi/2
                    hessian_thetas_2[parameter2] += np.pi/2

                    hessian_thetas_3[parameter1] += np.pi/2
                    hessian_thetas_3[parameter2] -= np.pi/2

                    hessian_thetas_4[parameter1] -= np.pi/2
                    hessian_thetas_4[parameter2] -= np.pi/2

                    hessian[parameter1, parameter2] += self.get_expectation_value(hessian_thetas_1, observable)/4
                    hessian[parameter1, parameter2] -= self.get_expectation_value(hessian_thetas_2, observable)/4
                    hessian[parameter1, parameter2] -= self.get_expectation_value(hessian_thetas_3, observable)/4
                    hessian[parameter1, parameter2] += self.get_expectation_value(hessian_thetas_4, observable)/4

                    hessian[parameter2, parameter1] = hessian[parameter1, parameter2]
                    
                if parameter1 == parameter2:

                    hessian_thetas_1 , hessian_thetas_2 = angles.copy(), angles.copy()

                    hessian_thetas_1[parameter1] += np.pi
                    hessian_thetas_2[parameter1] -= np.pi
                    
                    hessian[parameter1, parameter1] += self.get_expectation_value(hessian_thetas_1, observable)/4
                    hessian[parameter1, parameter1] += self.get_expectation_value(hessian_thetas_2, observable)/4
                    hessian[parameter1, parameter1] -= self.get_expectation_value(angles, observable)/2

        return hessian

    def get_third_derivatives(self, observable, angles):
        third_derivatives = np.zeros((self.number_of_parameters, self.number_of_parameters, self.number_of_parameters))

        for parameter1 in range(self.number_of_parameters):
            for parameter2 in range(self.number_of_parameters):
                for parameter3 in range(self.number_of_parameters):

                    if parameter1<=parameter2 and parameter2<=parameter3:

                        third_order_thetas1, third_order_thetas2, third_order_thetas3, third_order_thetas4, third_order_thetas5, third_order_thetas6, third_order_thetas7, third_order_thetas8 = angles.copy(), angles.copy(), angles.copy(), angles.copy(), angles.copy(), angles.copy(), angles.copy(), angles.copy()

                        third_order_thetas1[parameter1] += np.pi/2
                        third_order_thetas1[parameter2] += np.pi/2
                        third_order_thetas1[parameter3] += np.pi/2

                        third_order_thetas2[parameter1] += np.pi/2
                        third_order_thetas2[parameter2] += np.pi/2
                        third_order_thetas2[parameter3] -= np.pi/2

                        third_order_thetas3[parameter1] -= np.pi/2
                        third_order_thetas3[parameter2] += np.pi/2
                        third_order_thetas3[parameter3] += np.pi/2

                        third_order_thetas4[parameter1] -= np.pi/2
                        third_order_thetas4[parameter2] += np.pi/2
                        third_order_thetas4[parameter3] -= np.pi/2

                        third_order_thetas5[parameter1] += np.pi/2
                        third_order_thetas5[parameter2] -= np.pi/2
                        third_order_thetas5[parameter3] += np.pi/2

                        third_order_thetas6[parameter1] += np.pi/2
                        third_order_thetas6[parameter2] -= np.pi/2
                        third_order_thetas6[parameter3] -= np.pi/2

                        third_order_thetas7[parameter1] -= np.pi/2
                        third_order_thetas7[parameter2] -= np.pi/2
                        third_order_thetas7[parameter3] += np.pi/2

                        third_order_thetas8[parameter1] -= np.pi/2
                        third_order_thetas8[parameter2] -= np.pi/2
                        third_order_thetas8[parameter3] -= np.pi/2

                        third_derivatives[parameter1, parameter2, parameter3] += self.get_expectation_value(third_order_thetas1, observable)/8
                        third_derivatives[parameter1, parameter2, parameter3] -= self.get_expectation_value(third_order_thetas2, observable)/8  
                        third_derivatives[parameter1, parameter2, parameter3] -= self.get_expectation_value(third_order_thetas3, observable)/8
                        third_derivatives[parameter1, parameter2, parameter3] += self.get_expectation_value(third_order_thetas4, observable)/8
                        third_derivatives[parameter1, parameter2, parameter3] -= self.get_expectation_value(third_order_thetas5, observable)/8
                        third_derivatives[parameter1, parameter2, parameter3] += self.get_expectation_value(third_order_thetas6, observable)/8
                        third_derivatives[parameter1, parameter2, parameter3] += self.get_expectation_value(third_order_thetas7, observable)/8
                        third_derivatives[parameter1, parameter2, parameter3] -= self.get_expectation_value(third_order_thetas8, observable)/8

                        third_derivatives[parameter1, parameter3, parameter2] = third_derivatives[parameter1, parameter2, parameter3]
                        third_derivatives[parameter2, parameter1, parameter3] = third_derivatives[parameter1, parameter2, parameter3]
                        third_derivatives[parameter2, parameter3, parameter1] = third_derivatives[parameter1, parameter2, parameter3]
                        third_derivatives[parameter3, parameter1, parameter2] = third_derivatives[parameter1, parameter2, parameter3]
                        third_derivatives[parameter3, parameter2, parameter1] = third_derivatives[parameter1, parameter2, parameter3]

        return np.array(third_derivatives)


    def get_instantaneous_hamiltonian(self, time):
        return (1-time)*self.initial_hamiltonian + time*self.target_hamiltonian
    
    def get_linear_system(self, hamiltonian, angles):

        zero_order_terms = np.zeros((self.number_of_parameters,))
        first_order_terms = np.zeros((self.number_of_parameters, self.number_of_parameters))

        #We start with zero order terms.
        for parameter in range(self.number_of_parameters):
            zero_order_terms[parameter] += self.get_derivative(hamiltonian, parameter, angles)

        first_order_terms = self.get_hessian_matrix(hamiltonian, angles)

        return np.array(zero_order_terms), np.array(first_order_terms)
    
    def find_indices(self, s, threshold=0.1):
        indices = []
        for k in range(self.number_of_parameters):
            if s[k] <= threshold:
                indices.append(k)

        return indices
    
    def get_directional_diretivative(self, observable, vector, parameters, h=0.001):
        
        shifted_parameters = [parameters[i] + h*vector[i] for i in range(self.number_of_parameters)]

        exp_value1, exp_value2 = self.get_expectation_value(shifted_parameters, observable), self.get_expectation_value(parameters, observable)
        directional_derivative = (exp_value1 - exp_value2)/h

        return directional_derivative
    
    def get_hessian_elements_directional_derivative(self, hessian, vector, parameters, hamiltonian, h=0.0001):
        
        hessian_shifted = self.get_hessian_matrix(hamiltonian,  [parameters[i] + h*vector[i] for i in range(self.number_of_parameters)])

        hessian_elements_dir_dervs = (hessian_shifted - hessian)/h
        return hessian_elements_dir_dervs
    
    def get_hessian_from_null_vectors(self, hessian, hessian_elements_dir_derivs, coefs):

        hessian_matrix = hessian.copy()
        for _ in range(len(coefs)):
            hessian_matrix += coefs[_]*hessian_elements_dir_derivs[_]

        return hessian_matrix

    def directional_derivative_minimum_eigenvalue_of_hessian(self, hessian, vector, parameters, hamiltonian, h=0.0001):

        hessian_shifted = self.get_hessian_matrix(hamiltonian,  [parameters[i] + h*vector[i] for i in range(self.number_of_parameters)])

        min_eig_shifted, min_eig_at_point = self.minimum_eigenvalue(hessian_shifted), self.minimum_eigenvalue(hessian)

        return (min_eig_shifted-min_eig_at_point)/h
    
    def derivative_of_minimum_eigenvalue_over_lamda(self, hessian, time, parameters, q=0.001): #This function quantifies how much the perturbation affects the minimum eigenvalue.

        hamiltonian_perturbed = self.get_instantaneous_hamiltonian(time+q)
        hessian_perturbed = self.get_hessian_matrix(hamiltonian_perturbed, parameters)
        min_eig_unperturbed, min_eig_perturbed = self.minimum_eigenvalue(hessian), self.minimum_eigenvalue(hessian_perturbed)

        return (min_eig_perturbed-min_eig_unperturbed)/q


    def get_hessian_approximation(self, hessian, hamiltonian, gradient, parameters, shift): #need to do the derivation to write the correct change of gradients as well 

        new_angles =  [parameters[_] + shift[_] for _ in range(self.number_of_parameters)]
        new_gradient = np.array([self.get_derivative(hamiltonian, parameter, new_angles) for parameter in range(self.number_of_parameters)])
        change_of_gradient = (new_gradient - np.array(gradient)).reshape((self.number_of_parameters, 1))
        shift = np.array(shift).reshape((self.number_of_parameters, 1))

        term1 = change_of_gradient@change_of_gradient.T
        term1 /= shift@change_of_gradient.T@shift

        term2 = hessian@shift@shift.T@hessian
        term2 /= shift.T@hessian@shift

        hessian_approximation = hessian + term1 - term2

        return hessian_approximation

    def minimum_eigenvalue(self, matrix):

        min_eigen = np.min(np.linalg.eig(matrix)[0])
        print(min_eigen)
        return min_eigen

    def run(self):
        
        energies_aqcpqc = []

        lambdas = [i for i in np.linspace(0, 1, self.steps+1)][1:]
        optimal_thetas = self.initial_parameters.copy()
        print(f'We start with the optimal angles of the initial hamiltonian: {optimal_thetas}')

        initial_hessian = self.get_hessian_matrix(self.initial_hamiltonian, optimal_thetas) 
        w, v = np.linalg.eig(initial_hessian)
        print(f'The eigenvalues of the initial Hessian are {np.round(w, 7)}')

        for lamda in lambdas:
            print('\n')
            print(f'We are working on {lamda} where the current optimal point is {optimal_thetas}')
            hamiltonian = self.get_instantaneous_hamiltonian(lamda)
            zero, first = self.get_linear_system(hamiltonian, optimal_thetas)
 


            def equations(x):
                array = np.array([x[_] for _ in range(self.number_of_parameters)])
                equations = zero + first@array

                y = np.array([equations[_] for _ in range(self.number_of_parameters)])
                return y@y
            
            if not self.use_null_space:

                def minim_eig_constraint(x):
                    new_thetas = [optimal_thetas[i] + x[i] for i in range(self.number_of_parameters)]
                    return self.minimum_eigenvalue(self.get_hessian_matrix(hamiltonian, new_thetas))

                cons = [{'type': 'ineq', 'fun':minim_eig_constraint}]
                res = optimize.minimize(equations, x0 = [0 for _ in range(self.number_of_parameters)], constraints=cons,  method='COBYLA',  options={'disp': False}) 
                epsilons = [res.x[_] for _ in range(self.number_of_parameters)]
                
                
                print(f'The solutions of equations are {epsilons}')
                optimal_thetas = [optimal_thetas[_] + epsilons[_] for _ in range(self.number_of_parameters)]


            else:

                u, s, v = np.linalg.svd(first)
                indices = self.find_indices(s)
                print(f'The singular values of matrix A are {s}')

                null_space_approx = [v[index] for index in indices]


                unconstrained_optimization = optimize.minimize(equations, x0 = [0 for _ in range(self.number_of_parameters)], method='SLSQP',  options={'disp': False})
                epsilons_0 = unconstrained_optimization.x

                print(f'A solution to the linear system of equations is {epsilons_0}')
                optimal_thetas = [optimal_thetas[i] + epsilons_0[i] for i in range(self.number_of_parameters)]


                def norm(x):
                    vector = epsilons_0.copy()
                    for _ in range(len(null_space_approx)):
                        vector += x[_]*null_space_approx[_]

                    norm = np.linalg.norm(vector)
                    #print(f'Norm: {norm}')
                    return norm
                
                if not self.use_null_derivatives:

                    def minim_eig_constraint(x):
                        new_thetas = optimal_thetas.copy()
                        for _ in range(len(null_space_approx)):
                            new_thetas += x[_]*null_space_approx[_]
                        return self.minimum_eigenvalue(self.get_hessian_matrix(hamiltonian, new_thetas))
                    

                else:
                
                    #We can further make use that the null vectors are small! We construct a linear model of the Hessian using the directional derivatives of the Hessian elements, at the directional of the null vectors.
                    #First of all, we calculate the Hessian of the perturbed Hamiltonian at the previous optimal.
                    perturbed_hessian_at_optimal = self.get_hessian_matrix(hamiltonian, optimal_thetas)


                    #Then, we find the directional derivatives of the hessian elements at the optimal point.
                    directional_derivs_of_hessian_elements = []
                    for _ in range(len(null_space_approx)):
                        directional_derivs_of_hessian_elements.append(self.get_hessian_elements_directional_derivative(perturbed_hessian_at_optimal, null_space_approx[_], optimal_thetas, hamiltonian))


                    #Once we have the directional derivatives of the matrix elements, we can further proceed and impose the new minimum_eigenvalue constraint.

                    def minim_eig_constraint(x):
                        return self.minimum_eigenvalue(self.get_hessian_from_null_vectors(perturbed_hessian_at_optimal, directional_derivs_of_hessian_elements, x))

                
                
                cons = [{'type': 'ineq', 'fun':minim_eig_constraint}]
                constrained_optimization = optimize.minimize(norm, x0=[0 for _ in range(len(null_space_approx))], constraints=cons, method='COBYLA', options={'disp':True, 'maxiter':400}) 
                print(f'The solutions of the second optimization are {constrained_optimization.x}')

                for _ in range(len(null_space_approx)):
                    optimal_thetas += constrained_optimization.x[_]*null_space_approx[_]


            hessian = self.get_hessian_matrix(hamiltonian, optimal_thetas)
            min_eigen = self.minimum_eigenvalue(hessian)


            inst_exp_value = self.get_expectation_value(optimal_thetas, hamiltonian) - lamda*self.offset
            energies_aqcpqc.append(inst_exp_value)

            print(f'and the minimum eigenvalue of the Hessian at the solution is {min_eigen}')
            print(f'and the instantaneous expectation values is {inst_exp_value}') 

            print(f'The derivative of the minimum eigenvalue over lambda is {self.derivative_of_minimum_eigenvalue_over_lamda(hessian, lamda, optimal_thetas)}')

        return energies_aqcpqc

