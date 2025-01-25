import sys
import os 

current_file_directory = os.path.dirname(os.path.abspath(__file__))
custom_path = os.path.join(current_file_directory, 'lib')
sys.path.append(custom_path)

import numpy as np
from minionpycpp import LSHADE as cppLSHADE
from minionpycpp import LSHADE as cppJADE
from minionpycpp import ARRDE as cppARRDE
from minionpycpp import NLSHADE_RSP as cppNLSHADE_RSP
from minionpycpp import j2020 as cppj2020
from minionpycpp import jSO as cppjSO
from minionpycpp import LSRTDE as cppLSRTDE
from minionpycpp import Differential_Evolution as cppDifferential_Evolution
from minionpycpp import MinionResult as cppMinionResult
from minionpycpp import GWO_DE as cppGWO_DE
from minionpycpp import Minimizer as cppMinimizer
from minionpycpp import NelderMead as cppNelderMead 
from minionpycpp import CEC2017Functions as cppCEC2017Functions
from minionpycpp import CEC2014Functions as cppCEC2014Functions
from minionpycpp import CEC2019Functions as cppCEC2019Functions
from minionpycpp import CEC2020Functions as cppCEC2020Functions
from minionpycpp import CEC2022Functions as cppCEC2022Functions
import pybind11


from typing import Callable, Dict, Union, List, Optional, Any
  
class MinionResult:
    """
    @class MinionResult
    @brief A class to encapsulate the results of an optimization process.

    Stores the optimization result including solution vector, function value,
    number of iterations, number of function evaluations, success status, and a message.
    """

    def __init__(self, minRes):
        """
        @brief Constructor for MinionResult class.

        @param minRes The C++ MinionResult object to initialize from.
        """
        self.x = minRes.x
        self.fun = minRes.fun
        self.nit = minRes.nit
        self.nfev = minRes.nfev
        self.success = minRes.success
        self.message = minRes.message
        self.result = minRes

    def __repr__(self):
        """
        @brief Get a string representation of the MinionResult object.

        @return String representation containing key attributes.
        """
        return (f"MinionResult(x={self.x}, fun={self.fun}, nit={self.nit}, "
                f"nfev={self.nfev}, success={self.success}, message={self.message})")

class CEC2014Functions:
    """
    @class CEC2014Functions
    @brief A class to encapsulate CEC2014 test functions.

    Allows the loading of shift and rotation matrices and the evaluation of test functions.
    """

    def __init__(self, function_number, dimension):
        """
        @brief Constructor for CEC2014Functions class.

        @param function_number Function number (1-30).
        @param dimension Dimension of the problem.
        """
        if function_number not in range(1, 31) : raise Exception("Function number must be between 1-30.")
        if int(dimension) not in [2, 10, 20, 30, 50, 100] : raise Exception("Dimension must be 2, 10, 20, 30, 50, 100")
        self.cpp_func = cppCEC2014Functions(function_number, int(dimension))

    def __call__(self, X):
        """
        @brief Evaluate the CEC2014 test function.

        @param X Input vectors to evaluate.
        @return Vector of function values corresponding to each input vector.
        """
        return self.cpp_func(X)
    
class CEC2017Functions:
    """
    @class CEC2017Functions
    @brief A class to encapsulate CEC2017 test functions.

    Allows the loading of shift and rotation matrices and the evaluation of test functions.
    """

    def __init__(self, function_number, dimension):
        """
        @brief Constructor for CEC2017Functions class.

        @param function_number Function number (1-30).
        @param dimension Dimension of the problem.
        """
        if function_number not in range(1, 31) : raise Exception("Function number must be between 1-30.")
        if int(dimension) not in [2, 10, 20, 30, 50, 100] : raise Exception("Dimension must be 2, 10, 20, 30, 50, 100")
        self.cpp_func = cppCEC2017Functions(function_number, int(dimension))

    def __call__(self, X):
        """
        @brief Evaluate the CEC2017 test function.

        @param X Input vectors to evaluate.
        @return Vector of function values corresponding to each input vector.
        """
        return self.cpp_func(X)
    
class CEC2019Functions:
    """
    @class CEC2019Functions
    @brief A class to encapsulate CEC2019 test functions.

    Allows the loading of shift and rotation matrices and the evaluation of test functions.
    """

    def __init__(self, function_number):
        """
        @brief Constructor for CEC2019Functions class.

        @param function_number Function number (1-10).
        @param dimension Dimension of the problem.
        """
        if function_number not in range(1, 11) : raise Exception("Function number must be between 1-10.")
        if function_number==1 : dimension=9
        elif function_number==2:  dimension = 16
        elif function_number==3 : dimension=18
        else: dimension =10
        self.cpp_func = cppCEC2019Functions(function_number, int(dimension))

    def __call__(self, X):
        """
        @brief Evaluate the CEC2019 test function.

        @param X Input vectors to evaluate.
        @return Vector of function values corresponding to each input vector.
        """
        return self.cpp_func(X)
       
class CEC2020Functions:
    """
    @class CEC2020Functions
    @brief A class to encapsulate CEC2020 test functions.

    Allows the loading of shift and rotation matrices and the evaluation of test functions.
    """

    def __init__(self, function_number, dimension):
        """
        @brief Constructor for CEC2020Functions class.

        @param function_number Function number (1-10).
        @param dimension Dimension of the problem.
        """
        if function_number not in range(1, 11) : raise Exception("Function number must be between 1-10.")
        if int(dimension) not in [2, 5, 10, 15, 20] : raise Exception("Dimension must be 2, 10, or 20.")
        self.cpp_func = cppCEC2020Functions(function_number, int(dimension))

    def __call__(self, X):
        """
        @brief Evaluate the CEC2020 test function.

        @param X Input vectors to evaluate.
        @return Vector of function values corresponding to each input vector.
        """
        return self.cpp_func(X)

class CEC2022Functions:
    """
    @class CEC2022Functions
    @brief A class to encapsulate CEC2022 test functions.

    Allows the loading of shift and rotation matrices and the evaluation of test functions.
    """

    def __init__(self, function_number, dimension):
        """
        @brief Constructor for CEC2020Functions class.

        @param function_number Function number (1-10).
        @param dimension Dimension of the problem.
        """
        if function_number not in range(1, 13) : raise Exception("Function number must be between 1-12.")
        if int(dimension) not in [2, 10, 20] : raise Exception("Dimension must be 2, 10, or 20.")
        self.cpp_func = cppCEC2022Functions(function_number, int(dimension))

    def __call__(self, X):
        """
        @brief Evaluate the CEC2022 test function.

        @param X Input vectors to evaluate.
        @return Vector of function values corresponding to each input vector.
        """
        return self.cpp_func(X)
    
class CalllbackWrapper: 
    """
    @class CalllbackWrapper
    @brief Wrap a Python function that takes cppMinionResult as an argument to work with MinionResult.

    Convert a callback function from working with cppMinionResult to MinionResult.
    """

    def __init__(self, callback):
        """
        @brief Constructor for CalllbackWrapper.

        @param callback Callback function that takes cppMinionResult as argument.
        """
        self.callback = callback

    def __call__(self, minRes):
        """
        @brief Call operator to invoke the callback function.

        @param minRes MinionResult object to pass to callback function.
        @return Result of the callback function.
        """
        minionResult = MinionResult(minRes)
        return self.callback(minionResult)
    

class MinimizerBase:
    """
    @class MinimizerBase
    @brief Base class for minimization algorithms.

    Provides common functionality for optimization algorithms.
    """

    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[float]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = {}) : 
        """
        @brief Constructor for MinimizerBase class.

        @param func Objective function to minimize.
        @param bounds Bounds for the decision variables.
        @param data Additional data to pass to the objective function.
        @param x0 Initial guess for the solution.
        @param relTol Relative tolerance for convergence.
        @param maxevals Maximum number of function evaluations.
        @param callback Callback function called after each iteration.
        @param seed Seed for the random number generator.
        @param options (dict) further options for the algorithm
        """
        if not callable(func):
            raise TypeError("func must be callable")
        if not isinstance(bounds, list) or not all(isinstance(b, tuple) and len(b) == 2 for b in bounds):
            raise TypeError("bounds must be a list of tuples (float, float)")
        if x0 is not None and not all(isinstance(x, float) for x in x0):
            raise TypeError("x0 must be a list of floats or None")
        if not isinstance(relTol, float):
            raise TypeError("relTol must be a float")
        if not isinstance(maxevals, int):
            raise TypeError("maxevals must be an int")
        if callback is not None and not callable(callback):
            raise TypeError("callback must be callable or None")
        if seed is not None and not isinstance(seed, int):
            raise TypeError("seed must be an int or None")
        if not isinstance(options, dict):
            raise TypeError("options must be a dictionary")

        self.pyfunc = func 
        self.bounds = self._validate_bounds(bounds)
        self.x0 = x0 
        if self.x0 is not None : 
            if len(self.x0) != len(self.bounds) : raise ValueError("x0 must have the same dimension as the length of the bounds.")   
        self.x0cpp = self.x0 if self.x0 is not None else []
        self.data = None

        self.callback = callback  
        self.cppCallback = CalllbackWrapper(self.callback) if callback is not None else None

        self.relTol = relTol
        self.maxevals = maxevals
        self.seed = seed if seed is not None else -1
        self.history = []
        self.minionResult = None
        self.options= options

    def func(self, xmat, data) : 
        """
        @brief the minion library accept function with signature func(matrix, data. This basically function basically decorate the original pyfunc into an acceptable form.
        """
        return self.pyfunc(xmat) 

    def _validate_bounds(self, bounds):
        """
        @brief Validate the bounds format.

        @param bounds Bounds for the decision variables.
        @return Validated bounds in the required format.
        @throws ValueError if bounds are invalid.
        """

        try:
            bounds = np.array(bounds)
        except:
            raise ValueError("Invalid bounds.")
        if np.any(bounds[:, 0]>= bounds[:,1]): raise ValueError ("upper bound must be larger than lower bound.")
        if bounds.shape[1] != 2:
            raise ValueError("Invalid bounds. Bounds must be a list of (lower_bound, upper_bound).")
        return [(b[0], b[1]) for b in bounds]

class GWO_DE(MinimizerBase):
    """
    @class GWO_DE
    @brief Implementation of the Grey Wolf Optimizer with Differential Evolution (GWO-DE) algorithm.

    Inherits from MinimizerBase and implements the optimization algorithm.
    """

    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[float]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = {}
        ) : 
        """
        @brief Constructor for MinimizerBase class.

        @param func Objective function to minimize.
        @param bounds Bounds for the decision variables.
        @param data Additional data to pass to the objective function.
        @param x0 Initial guess for the solution.
        @param relTol Relative tolerance for convergence.
        @param maxevals Maximum number of function evaluations.
        @param callback Callback function called after each iteration.
        @param seed Seed for the random number generator.
        @param options (dict) further options for the algorithm
        """

        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppGWO_DE(self.func, self.bounds, self.x0cpp, self.data,  self.cppCallback, relTol, maxevals, self.seed, self.options)
    
    def optimize(self):
        """
        @brief Optimize the objective function using GWO-DE.

        @return MinionResult object containing the optimization results.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        return self.minionResult

class NelderMead(MinimizerBase):
    """
    @class AdaptiveNelderMead
    @brief Implementation of the Adaptive Nelder-Mead algorithm.

    Inherits from MinimizerBase and implements the Adaptive Nelder-Mead optimization algorithm.
    """

    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[float]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = {}
        ) : 
        """
        @brief Constructor for MinimizerBase class.

        @param func Objective function to minimize.
        @param bounds Bounds for the decision variables.
        @param data Additional data to pass to the objective function.
        @param x0 Initial guess for the solution.
        @param relTol Relative tolerance for convergence.
        @param maxevals Maximum number of function evaluations.
        @param callback Callback function called after each iteration.
        @param seed Seed for the random number generator.
        @param options (dict) further options for the algorithm
        """

        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppNelderMead(self.func, self.bounds, self.x0cpp, self.data,  self.cppCallback, relTol, maxevals, self.seed, self.options)

    def optimize(self):
        """
        @brief Optimize the objective function using Adaptive Nelder-Mead.

        @return MinionResult object containing the optimization results.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        return self.minionResult



class LSHADE(MinimizerBase):
    """
    @class LSHADE
    @brief Implementation of the LSHADE algorithm.

    Inherits from MinimizerBase and implements the optimization algorithm.
    """
    
    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[float]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = {}
        ) : 
        """
        @brief Constructor for MinimizerBase class.

        @param func Objective function to minimize.
        @param bounds Bounds for the decision variables.
        @param data Additional data to pass to the objective function.
        @param x0 Initial guess for the solution.
        @param relTol Relative tolerance for convergence.
        @param maxevals Maximum number of function evaluations.
        @param callback Callback function called after each iteration.
        @param seed Seed for the random number generator.
        @param options (dict) further options for the algorithm
        """

        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppLSHADE(self.func, self.bounds, self.x0cpp, self.data,  self.cppCallback, relTol, maxevals, self.seed, self.options)
    
    def optimize(self):
        """
        @brief Optimize the objective function using LSHADE.

        @return MinionResult object containing the optimization results.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        self.meanCR = self.optimizer.meanCR
        self.meanF = self.optimizer.meanF
        self.stdCR = self.optimizer.stdCR
        self.stdF = self.optimizer.stdF
        self.diversity = self.optimizer.diversity
        return self.minionResult

class jSO(MinimizerBase):
    """
    @class jSO
    @brief Implementation of the jSO algorithm.

    Inherits from MinimizerBase and implements the optimization algorithm.
    """
    
    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[float]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = {}
        ) : 
        """
        @brief Constructor for MinimizerBase class.

        @param func Objective function to minimize.
        @param bounds Bounds for the decision variables.
        @param data Additional data to pass to the objective function.
        @param x0 Initial guess for the solution.
        @param relTol Relative tolerance for convergence.
        @param maxevals Maximum number of function evaluations.
        @param callback Callback function called after each iteration.
        @param seed Seed for the random number generator.
        @param options (dict) further options for the algorithm
        """

        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppjSO(self.func, self.bounds, self.x0cpp, self.data,  self.cppCallback, relTol, maxevals, self.seed, self.options)
    
    def optimize(self):
        """
        @brief Optimize the objective function using LSHADE.

        @return MinionResult object containing the optimization results.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        self.meanCR = self.optimizer.meanCR
        self.meanF = self.optimizer.meanF
        self.stdCR = self.optimizer.stdCR
        self.stdF = self.optimizer.stdF
        self.diversity = self.optimizer.diversity
        return self.minionResult
    

class JADE(MinimizerBase):
    """
    @class JADE
    @brief Implementation of the JADE algorithm.

    Inherits from MinimizerBase and implements the optimization algorithm.
    """
    
    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[float]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = {}
        ) : 
        """
        @brief Constructor for MinimizerBase class.

        @param func Objective function to minimize.
        @param bounds Bounds for the decision variables.
        @param data Additional data to pass to the objective function.
        @param x0 Initial guess for the solution.
        @param relTol Relative tolerance for convergence.
        @param maxevals Maximum number of function evaluations.
        @param callback Callback function called after each iteration.
        @param seed Seed for the random number generator.
        @param options (dict) further options for the algorithm
        """

        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppJADE(self.func, self.bounds, self.x0cpp, self.data,  self.cppCallback, relTol, maxevals, self.seed, self.options)
    
    def optimize(self):
        """
        @brief Optimize the objective function using JADE.

        @return MinionResult object containing the optimization results.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        self.meanCR = self.optimizer.meanCR
        self.meanF = self.optimizer.meanF
        self.stdCR = self.optimizer.stdCR
        self.stdF = self.optimizer.stdF
        self.diversity = self.optimizer.diversity
        return self.minionResult
    
    
class NLSHADE_RSP(MinimizerBase):
    """
    @class LSHAD_RSP
    @brief Implementation of the LSHADE_RSP algorithm.

    Inherits from MinimizerBase and implements the optimization algorithm.
    """
    
    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[float]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = {}
        ) : 
        """
        @brief Constructor for MinimizerBase class.

        @param func Objective function to minimize.
        @param bounds Bounds for the decision variables.
        @param data Additional data to pass to the objective function.
        @param x0 Initial guess for the solution.
        @param relTol Relative tolerance for convergence.
        @param maxevals Maximum number of function evaluations.
        @param callback Callback function called after each iteration.
        @param seed Seed for the random number generator.
        @param options (dict) further options for the algorithm
        """

        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppNLSHADE_RSP(self.func, self.bounds, self.x0cpp, self.data,  self.cppCallback, relTol, maxevals, self.seed, self.options)
    
    def optimize(self):
        """
        @brief Optimize the objective function using LSHADE.

        @return MinionResult object containing the optimization results.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        return self.minionResult
    
class j2020(MinimizerBase):
    """
    @class j2020
    @brief Implementation of the j2020 algorithm.

    Inherits from MinimizerBase and implements the optimization algorithm.
    """
    
    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[float]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = {}
        ) : 
        """
        @brief Constructor for MinimizerBase class.

        @param func Objective function to minimize.
        @param bounds Bounds for the decision variables.
        @param data Additional data to pass to the objective function.
        @param x0 Initial guess for the solution.
        @param relTol Relative tolerance for convergence.
        @param maxevals Maximum number of function evaluations.
        @param callback Callback function called after each iteration.
        @param seed Seed for the random number generator.
        @param options (dict) further options for the algorithm
        """

        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppj2020(self.func, self.bounds, self.x0cpp, self.data,  self.cppCallback, relTol, maxevals, self.seed, self.options)
    
    def optimize(self):
        """
        @brief Optimize the objective function using j2020.

        @return MinionResult object containing the optimization results.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        return self.minionResult
    
class LSRTDE(MinimizerBase):
    """
    @class j2020
    @brief Implementation of the LSRTDE algorithm.

    Inherits from MinimizerBase and implements the optimization algorithm.
    """
    
    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[float]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = {}
        ) : 
        """
        @brief Constructor for MinimizerBase class.

        @param func Objective function to minimize.
        @param bounds Bounds for the decision variables.
        @param data Additional data to pass to the objective function.
        @param x0 Initial guess for the solution.
        @param relTol Relative tolerance for convergence.
        @param maxevals Maximum number of function evaluations.
        @param callback Callback function called after each iteration.
        @param seed Seed for the random number generator.
        @param options (dict) further options for the algorithm
        """

        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppLSRTDE(self.func, self.bounds, self.x0cpp, self.data,  self.cppCallback, relTol, maxevals, self.seed, self.options)
    
    def optimize(self):
        """
        @brief Optimize the objective function using j2020.

        @return MinionResult object containing the optimization results.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        return self.minionResult


class ARRDE(MinimizerBase):
    """
    @class ARRDE
    @brief Implementation of the ARRDE algorithm.

    Inherits from MinimizerBase and implements the optimization algorithm.
    """
    
    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[float]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = {}
        ) : 
        """
        @brief Constructor for MinimizerBase class.

        @param func Objective function to minimize.
        @param bounds Bounds for the decision variables.
        @param data Additional data to pass to the objective function.
        @param x0 Initial guess for the solution.
        @param relTol Relative tolerance for convergence.
        @param maxevals Maximum number of function evaluations.
        @param callback Callback function called after each iteration.
        @param seed Seed for the random number generator.
        @param options (dict) further options for the algorithm
        """

        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppARRDE(self.func, self.bounds, self.x0cpp, self.data,  self.cppCallback, relTol, maxevals, self.seed, self.options)
    
    def optimize(self):
        """
        @brief Optimize the objective function using ARRDE.

        @return MinionResult object containing the optimization results.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        self.meanCR = self.optimizer.meanCR
        self.meanF = self.optimizer.meanF
        self.stdCR = self.optimizer.stdCR
        self.stdF = self.optimizer.stdF
        self.diversity = self.optimizer.diversity
        return self.minionResult


class Differential_Evolution(MinimizerBase):
    """
    @class Differential_Evolution
    @brief Implementation of the Differential Evolution algorithm.

    Inherits from MinimizerBase and implements the optimization algorithm.
    """
    
    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[float]] = None,
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = {}
        ) : 
        """
        @brief Constructor for MinimizerBase class.

        @param func Objective function to minimize.
        @param bounds Bounds for the decision variables.
        @param x0 Initial guess for the solution.
        @param relTol Relative tolerance for convergence.
        @param maxevals Maximum number of function evaluations.
        @param callback Callback function called after each iteration.
        @param seed Seed for the random number generator.
        @param options (dict) further options for the algorithm
        """

        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppDifferential_Evolution(self.func, self.bounds, self.x0cpp, self.data,  self.cppCallback, relTol, maxevals, self.seed, self.options)
    
    def optimize(self):
        """
        @brief Optimize the objective function using Differential Evolution.

        @return MinionResult object containing the optimization results.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        self.meanCR = self.optimizer.meanCR
        self.meanF = self.optimizer.meanF
        self.stdCR = self.optimizer.stdCR
        self.stdF = self.optimizer.stdF
        self.diversity = self.optimizer.diversity
        return self.minionResult
    
class Minimizer(MinimizerBase):
    """
    @class Differential_Evolution
    @brief Implementation of the Differential Evolution algorithm.

    Inherits from MinimizerBase and implements the optimization algorithm.
    """
    
    def __init__(self, func: Callable[[np.ndarray, Optional[object]], float],
                 bounds: List[tuple[float, float]],
                 x0: Optional[List[float]] = None,
                 algo : str = "ARRDE",
                 relTol: float = 0.0001,
                 maxevals: int = 100000,
                 callback: Optional[Callable[[Any], None]] = None,
                 seed: Optional[int] = None,
                 options: Dict[str, Any] = {}
        ) : 
        """
        @brief Constructor for MinimizerBase class.

        @param func Objective function to minimize.
        @param bounds Bounds for the decision variables.
        @param x0 Initial guess for the solution.
        @param algo Algorithm to use : "LSHADE", "DE", "JADE", "jSO", "DE", "NelderMead", "LSRTDE", "NLSHADE_RSP", "j2020", "GWO_DE"
        @param relTol Relative tolerance for convergence.
        @param maxevals Maximum number of function evaluations.
        @param callback Callback function called after each iteration.
        @param seed Seed for the random number generator.
        @param options (dict) further options for the algorithm
        """
        all_algo = ["LSHADE", "DE", "JADE", "jSO", "NelderMead", "LSRTDE", "NLSHADE_RSP", "j2020", "GWO_DE", "ARRDE"]
        if not (algo in all_algo) : 
            raise Exception("Uknownn algorithm. The algorithm must be one of these : ", all_algo)
        
        super().__init__(func, bounds, x0, relTol, maxevals, callback, seed, options)
        self.optimizer = cppMinimizer(self.func, self.bounds, self.x0cpp, self.data,  self.cppCallback, algo,relTol, maxevals, self.seed, self.options)
    
    def optimize(self):
        """
        @brief Optimize the objective function using Differential Evolution.

        @return MinionResult object containing the optimization results.
        """
        self.minionResult = MinionResult(self.optimizer.optimize())
        self.history = [MinionResult(res) for res in self.optimizer.history]
        return self.minionResult
