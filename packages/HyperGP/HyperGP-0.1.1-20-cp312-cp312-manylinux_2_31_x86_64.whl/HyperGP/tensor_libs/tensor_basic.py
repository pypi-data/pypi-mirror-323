
from ._src._tensor_ops import *
from ._src._tensor_ops import _pow
from ._src.basic import *
from ._src.basic import _static_check, _ITEM_STATIC
from ..src.ndarray import _dtype_strmap



class Tensor(Value):
    def __init__(self, array, device=None, dtype=None, device_id=0, **kwargs):
        if isinstance(array, Tensor):
            if device == None:
                device = array.device
            if device == array.device and dtype == array.dtype:
                cached_data = array.realize_cached_data
            else:
                cached_data = array_api._array(array.realize_cached_data, dtype=dtype, device=device, device_id=device_id)
        else:
            cached_data = array_api._array(array, dtype=dtype, device=device, device_id=device_id)
        self._init(None, [], cached_data)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __int__(self):
        return int(self.cached_data.numpy())
    
    def __float__(self):
        return float(self.cached_data.numpy())
    
    def __bool__(self):
        return bool(self.cached_data.numpy())
    
    @property
    def realize_cached_data(self):
        if self.cached_data is not None:
            return self.cached_data
        else:
            self.cached_data = self.op.compute(*[input_tensor.realize_cached_data if isinstance(input_tensor, Tensor)
                                                 else input_tensor
                                             for input_tensor in self.input])
            return self.cached_data
    
    @property
    def dtype(self):
        return self.cached_data.dtype
    @property
    def shape(self):
        return self.cached_data.shape
    
    def __getstate__(self):
        return (self.op, self.input, self.cached_data.__getstate__())
    
    def __setstate__(self, states):
        if states[2][1] not in _dtype_strmap:
            raise ValueError("The dtype '{D}' is unsupported now.".format(D=states[2][1]))
        self._init(states[0], states[1], NDArray._setstate(states[2]))

    def __getitem__(self, idx):
        tensor = Tensor.__new__(Tensor)
        tensor._init(None, [], self.cached_data[idx])
        return tensor
    
    def __setitem__(self, idxs, other):
        # assert isinstance(other, Tensor) or isinstance(other, np.ndarray), "The input array type should be Tensor or np.ndarray"
        if isinstance(other, Tensor):
            self.realize_cached_data[idxs] = other.realize_cached_data
        else:
            self.realize_cached_data[idxs] = other
        
    def __str__(self):
        return self.cached_data.__str__()
    
    def reshape(self, shape):
        tensor = Tensor.__new__(Tensor)
        tensor._init(None, [], self.cached_data.reshape(shape))
        return tensor
    
    def __deepcopy__(self, memo):
        #[ ] TODO : only copy the current node data without op and input 
        tensor = Tensor.__new__(Tensor)
        tensor._init(None, [], self.realize_cached_data.copy())
        return tensor

    def copy(self):
        tensor = Tensor.__new__(Tensor)
        tensor._init(None, [], self.realize_cached_data.copy())
        return tensor
    
    def view(self):
        tensor = Tensor.__new__(Tensor)
        tensor._init(self.op, self.input, self.cached_data.view())
        return tensor

    @property
    def device(self):
        return self.cached_data.device
    
    def __add__(self, other):
        
        if MOD[0] == "STATIC":
            if not isinstance(other, Tensor):
                other = Tensor(other)
            strs_list, param_list = _static_check(self, other)
            strs_list.append("add")
            return Tensor([], **{"item_static":_ITEM_STATIC(strs_list, param_list)})
        if MOD[0] == "IMM":
            if isinstance(other, Tensor):
                tensor = Tensor(self.cached_data + other.cached_data)
            elif isinstance(other, float) or isinstance(other, int):
                tensor = Tensor(self.cached_data + other)
            else:
                tensor = Tensor(self.cached_data + array_api._array(other))
        else:
            if isinstance(other, Tensor):
                tensor = Tensor.make_from_op(EWiseAdd(), [self, other])
            else:
                tensor = Tensor.make_from_op(ScalarAdd(), [self, other])
        
            if MOD[0] == "Async":
                tensor.realize_cached_data

        return tensor
    
    def __radd__(self, other):
        
        if MOD[0] == "STATIC":
            if not isinstance(other, Tensor):
                other = Tensor(other)
            strs_list, param_list = _static_check(other, self)
            strs_list.append("add")
            return Tensor([], **{"item_static":_ITEM_STATIC(strs_list, param_list)})
        if MOD[0] == "IMM":
            if isinstance(other, Tensor):
                tensor = Tensor(other.cached_data + self.cached_data)
            elif isinstance(other, float) or isinstance(other, int):
                tensor = Tensor(other + self.cached_data)
            else:
                tensor = Tensor(array_api._array(other) + self.cached_data)
        else:
            if isinstance(other, Tensor):
                tensor = Tensor.make_from_op(EWiseAdd(), [other + self])
            else:
                tensor = Tensor.make_from_op(ScalarAdd(), [other + self])
        
            if MOD[0] == "Async":
                tensor.realize_cached_data

        return tensor

    def __pow__(self, other):
        
        if MOD[0] == "STATIC":
            if not isinstance(other, Tensor):
                other = Tensor(other)
            strs_list, param_list = _static_check(self, other)
            strs_list.append("pow")
            return Tensor([], **{"item_static":_ITEM_STATIC(strs_list, param_list)})
        if MOD[0] == "IMM":
            if isinstance(other, Tensor):
                tensor = Tensor(self.cached_data.pow(other.cached_data))
            elif isinstance(other, float) or isinstance(other, int):
                tensor = Tensor(self.cached_data.pow(other))
            else:
                tensor = Tensor(self.cached_data.pow(array_api._array(other)))
        else:
            if isinstance(other, Tensor):
                tensor = Tensor.make_from_op(EWisePow(), [self, other])
            else:
                tensor = Tensor.make_from_op(ScalarPow(), [self, other])
        
            if MOD[0] == "Async":
                tensor.realize_cached_data

        return tensor
    
    def __rpow__(self, other):
        
        if MOD[0] == "STATIC":
            if not isinstance(other, Tensor):
                other = Tensor(other)
            strs_list, param_list = _static_check(other, self)
            strs_list.append("pow")
            return Tensor([], **{"item_static":_ITEM_STATIC(strs_list, param_list)})
        if MOD[0] == "IMM":
            if isinstance(other, float) or isinstance(other, int):
                tensor = Tensor(_pow(other, self.cached_data))
            else:
                tensor = Tensor(_pow(array_api._array(other), self.cached_data))
        else:
            other = Tensor(array_api._array(other))
            tensor = Tensor.make_from_op(EWiseRPow(), [other, self])
        
            if MOD[0] == "Async":
                tensor.realize_cached_data

        return tensor
    
    def __sub__(self, other):
        
        if MOD[0] == "STATIC":
            if not isinstance(other, Tensor):
                other = Tensor(other)
            strs_list, param_list = _static_check(self, other)
            strs_list.append("sub")
            return Tensor([], **{"item_static":_ITEM_STATIC(strs_list, param_list)})
        if MOD[0] == "IMM":
            if isinstance(other, Tensor):
                tensor = Tensor(self.cached_data - other.cached_data)
            elif isinstance(other, float) or isinstance(other, int):
                tensor = Tensor(self.cached_data - other)
            else:
                tensor = Tensor(self.cached_data - array_api._array(other))
        else:
            if isinstance(other, Tensor):
                tensor = Tensor.make_from_op(EWiseSub(), [self, other])
            else:
                tensor = Tensor.make_from_op(ScalarSub(), [self, other])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor

    def __rsub__(self, other):
        
        if MOD[0] == "STATIC":
            if not isinstance(other, Tensor):
                other = Tensor(other)
            strs_list, param_list = _static_check(other, self)
            strs_list.append("sub")
            return Tensor([], **{"item_static":_ITEM_STATIC(strs_list, param_list)})
        if MOD[0] == "IMM":
            if isinstance(other, Tensor):
                tensor = Tensor(other.cached_data - self.cached_data)
            elif isinstance(other, float) or isinstance(other, int):
                tensor = Tensor(other - self.cached_data)
            else:
                tensor = Tensor(array_api._array(other) - self.cached_data)
        else:
            if isinstance(other, Tensor):
                tensor = Tensor.make_from_op(EWiseSub(), [other, self])
            else:
                tensor = Tensor.make_from_op(ScalarSub(), [other, self])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor

    def __mul__(self, other):
        if MOD[0] == "STATIC":
            if not isinstance(other, Tensor):
                other = Tensor(other)
            strs_list, param_list = _static_check(self, other)
            strs_list.append("mul")
            return Tensor([], **{"item_static":_ITEM_STATIC(strs_list, param_list)})
        if MOD[0] == "IMM":
            if isinstance(other, Tensor):
                tensor = Tensor(self.cached_data * other.cached_data)
            elif isinstance(other, float) or isinstance(other, int):
                tensor = Tensor(self.cached_data * other)
            else:
                tensor = Tensor(self.cached_data * array_api._array(other))
        else:
            if isinstance(other, Tensor):
                tensor = Tensor.make_from_op(EWiseMul(), [self, other])
            else:
                tensor = Tensor.make_from_op(ScalarMul(), [self, other])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor

    def __rmul__(self, other):
        if MOD[0] == "STATIC":
            if not isinstance(other, Tensor):
                other = Tensor(other)
            strs_list, param_list = _static_check(other, self)
            strs_list.append("mul")
            return Tensor([], **{"item_static":_ITEM_STATIC(strs_list, param_list)})
        if MOD[0] == "IMM":
            if isinstance(other, Tensor):
                tensor = Tensor(other.cached_data * self.cached_data)
            elif isinstance(other, float) or isinstance(other, int):
                tensor = Tensor(other * self.cached_data)
            else:
                tensor = Tensor(array_api._array(other) * self.cached_data)
        else:
            if isinstance(other, Tensor):
                tensor = Tensor.make_from_op(EWiseMul(), [other, self])
            else:
                tensor = Tensor.make_from_op(ScalarMul(), [other, self])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor


    def __truediv__(self, other):
        
        if MOD[0] == "STATIC":
            if not isinstance(other, Tensor):
                other = Tensor(other)
            strs_list, param_list = _static_check(self, other)
            strs_list.append("div")
            return Tensor([], **{"item_static":_ITEM_STATIC(strs_list, param_list)})
        if MOD[0] == "IMM":
            if isinstance(other, Tensor):
                tensor = Tensor(self.cached_data / other.cached_data)
            elif isinstance(other, float) or isinstance(other, int):
                tensor = Tensor(self.cached_data / other)
            else:
                tensor = Tensor(self.cached_data / array_api._array(other))
        else:
            if isinstance(other, Tensor):
                tensor = Tensor.make_from_op(EWiseDiv(), [self, other])
            else:
                tensor = Tensor.make_from_op(ScalarDiv(), [self, other])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor

    def __rtruediv__(self, other):
        
        if MOD[0] == "STATIC":
            if not isinstance(other, Tensor):
                other = Tensor(other)
            strs_list, param_list = _static_check(other, self)
            strs_list.append("div")
            return Tensor([], **{"item_static":_ITEM_STATIC(strs_list, param_list)})
        if MOD[0] == "IMM":
            if isinstance(other, Tensor):
                tensor = Tensor(other.cached_data / self.cached_data)
            elif isinstance(other, float) or isinstance(other, int):
                tensor = Tensor(other / self.cached_data)
            else:
                tensor = Tensor(array_api._array(other) / self.cached_data)
        else:
            if isinstance(other, Tensor):
                tensor = Tensor.make_from_op(EWiseDiv(), [other, self])
            else:
                tensor = Tensor.make_from_op(ScalarDiv(), [other, self])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor



    def T(self, dim_0):
        if MOD[0] == "STATIC":
            strs_list, param_list = _static_check(self)
            param_list.extend([dim_0])
            strs_list.append("T")
            return Tensor([], **{"item_static":_ITEM_STATIC(strs_list, param_list)})
        if MOD[0] == "IMM":
            tensor = Tensor(self.cached_data.T(dim_0))
        else:
            tensor = Tensor.make_from_op(EWiseTDim(), [self, dim_0])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor
    
    def dot(self, other, dim_0 = 0, dim_1 = 0):
        
        if MOD[0] == "STATIC":
            if not isinstance(other, Tensor):
                other = Tensor(other)
            strs_list, param_list = _static_check(self, other)
            param_list.extend([dim_0, dim_1])
            strs_list.append("dot")
            return Tensor([], **{"item_static":_ITEM_STATIC(strs_list, param_list)})
        if MOD[0] == "IMM":
            if isinstance(other, Tensor):
                tensor = Tensor(self.cached_data.dot(other.cached_data, dim_0, dim_1))
            else:
                tensor = Tensor(self.cached_data.dot(array_api._array(other), dim_0, dim_1))
        else:
            if isinstance(other, Tensor):
                tensor = Tensor.make_from_op(EWiseDotDim(), [self, other, dim_0, dim_1])
            else:
                tensor = Tensor.make_from_op(EWiseDotDim(), [self, Tensor(other), dim_0, dim_1])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor

    def sin(self):
        if MOD[0] == "STATIC":
            strs_list, param_list = _static_check(self)
            strs_list.append("sin")
            return Tensor([], **{"item_static":_ITEM_STATIC(strs_list, param_list)})
        if MOD[0] == "IMM":
            tensor = Tensor(self.cached_data.sin())
        else:
            tensor = Tensor.make_from_op(EWiseSin(), [self])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor

    def cos(self):
        if MOD[0] == "STATIC":
            strs_list, param_list = _static_check(self)
            strs_list.append("cos")
            return Tensor([], **{"item_static":_ITEM_STATIC(strs_list, param_list)})
        if MOD[0] == "IMM":
            tensor = Tensor(self.cached_data.cos())
        else:
            tensor = Tensor.make_from_op(EWiseCos(), [self])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor

    def tan(self):
        if MOD[0] == "STATIC":
            strs_list, param_list = _static_check(self)
            strs_list.append("tan")
            return Tensor([], **{"item_static":_ITEM_STATIC(strs_list, param_list)})
        if MOD[0] == "IMM":
            tensor = Tensor(self.cached_data.tan())
        else:
            tensor = Tensor.make_from_op(EWiseTan(), [self])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor

    def sum(self, dim=0):
        if MOD[0] == "STATIC":
            strs_list, param_list = _static_check(self)
            strs_list.append("sum")
            param_list.extend([dim])
            return Tensor([], **{"item_static":_ITEM_STATIC(strs_list, param_list)})
        if MOD[0] == "IMM":
            tensor = Tensor(self.cached_data.sum(dim))
        else:
            tensor = Tensor.make_from_op(EWiseSum(), [self, dim])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor
    
    # def substract(self, other, dim=0):
    #     tensor = EwiseSubDim().make(self, other, dim)
    #     if MOD[0] == "Async":
    #         tensor.realize_cached_data
    #     return tensor
    
    def min(self, dim=0):
        if MOD[0] == "STATIC":
            strs_list, param_list = _static_check(self)
            strs_list.append("min")
            param_list.extend([dim])
            return Tensor([], **{"item_static":_ITEM_STATIC(strs_list, param_list)})
        if MOD[0] == "IMM":
            tensor = Tensor(self.cached_data.min(dim))
        else:
            tensor = Tensor.make_from_op(EWiseMin(), [self, dim])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor
    
    def max(self, dim=0):
        if MOD[0] == "STATIC":
            strs_list, param_list = _static_check(self)
            strs_list.append("max")
            param_list.extend([dim])
            return Tensor([], **{"item_static":_ITEM_STATIC(strs_list, param_list)})
        if MOD[0] == "IMM":
            tensor = Tensor(self.cached_data.max(dim))
        else:
            tensor = Tensor.make_from_op(EWiseMax(), [self, dim])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor
    
    def mean(self, dim=0):
        if MOD[0] == "STATIC":
            strs_list, param_list = _static_check(self)
            strs_list.append("mean")
            param_list.extend([dim])
            return Tensor([], **{"item_static":_ITEM_STATIC(strs_list, param_list)})
        if MOD[0] == "IMM":
            tensor = Tensor(self.cached_data.mean(dim))
        else:
            tensor = Tensor.make_from_op(EWiseMean(), [self, dim])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor
    
    def argmax(self, dim=0):
        if MOD[0] == "STATIC":
            strs_list, param_list = _static_check(self)
            strs_list.append("argmax")
            param_list.extend([dim])
            return Tensor([], **{"item_static":_ITEM_STATIC(strs_list, param_list)})
        if MOD[0] == "IMM":
            tensor = Tensor(self.cached_data.argmax(dim))
        else:
            tensor = Tensor.make_from_op(EWiseArgmax(), [self, dim])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor
    
    def argmin(self, dim=0):
        if MOD[0] == "IMM":
            tensor = Tensor(self.cached_data.argmin(dim))
        else:
            tensor = Tensor.make_from_op(EWiseArgmin(), [self, dim])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor
    
    def std(self, dim=0):
        if MOD[0] == "IMM":
            tensor = Tensor(self.cached_data.std(dim))
        else:
            tensor = Tensor.make_from_op(EWiseStd(), [self, dim])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor
    
    def var(self, dim=0):
        if MOD[0] == "IMM":
            tensor = Tensor(self.cached_data.var(dim))
        else:
            tensor = Tensor.make_from_op(EWiseVar(), [self, dim])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor
    
    def __lt__(self, other):
        if MOD[0] == "IMM":
            if isinstance(other, Tensor):
                res = Tensor(self.cached_data < other.cached_data)
            else:
                res = Tensor(self.cached_data < array_api._array(other))
        else:
            if isinstance(other, Tensor):
                res = Tensor.make_from_op(EWiseLt(), [self, other])
            else:
                res = Tensor.make_from_op(EWiseLt(), [self, Tensor(other)])
            res.realize_cached_data
        return res
    
    def __le__(self, other):
        if MOD[0] == "IMM":
            if isinstance(other, Tensor):
                res = Tensor(self.cached_data <= other.cached_data)
            else:
                res = Tensor(self.cached_data <= array_api._array(other))
        else:
            if isinstance(other, Tensor):
                res = Tensor.make_from_op(EWiseLe(), [self, other])
            else:
                res = Tensor.make_from_op(EWiseLe(), [self, Tensor(other)])
            res.realize_cached_data
        return res
    
    def __gt__(self, other):
        if MOD[0] == "IMM":
            if isinstance(other, Tensor):
                res = Tensor(self.cached_data > other.cached_data)
            else:
                res = Tensor(self.cached_data > array_api._array(other))
        else:
            if isinstance(other, Tensor):
                res = Tensor.make_from_op(EWiseGt(), [self, other])
            else:
                res = Tensor.make_from_op(EWiseGt(), [self, Tensor(other)])
            res.realize_cached_data
        return res
    
    def __ge__(self, other):
        if MOD[0] == "IMM":
            if isinstance(other, Tensor):
                res = Tensor(self.cached_data >= other.cached_data)
            else:
                res = Tensor(self.cached_data >= array_api._array(other))
        else:
            if isinstance(other, Tensor):
                res = Tensor.make_from_op(EWiseGe(), [self, other])
            else:
                res = Tensor.make_from_op(EWiseGe(), [self, Tensor(other)])
            res.realize_cached_data
        return res
    
    def __eq__(self, other):
        if MOD[0] == "IMM":
            if isinstance(other, Tensor):
                res = Tensor(self.cached_data == other.cached_data)
            else:
                res = Tensor(self.cached_data == array_api._array(other))
        else:
            if isinstance(other, Tensor):
                res = Tensor.make_from_op(EWiseEq(), [self, other])
            else:
                res = Tensor.make_from_op(EWiseEq(), [self, Tensor(other)])
            res.realize_cached_data
        return res
    
    def __ne__(self, other):
        if MOD[0] == "IMM":
            if isinstance(other, Tensor):
                res = Tensor(self.cached_data != other.cached_data)
            else:
                res = Tensor(self.cached_data != array_api._array(other))
        else:
            if isinstance(other, Tensor):
                res = Tensor.make_from_op(EWiseNeq(), [self, other])
            else:
                res = Tensor.make_from_op(EWiseNeq(), [self, Tensor(other)])
            res.realize_cached_data
        return res

    def numpy(self):
        return self.cached_data.numpy()
    
    @staticmethod
    def make_from_op(op: Op, inputs: List["Tensor"]):
        tensor = Tensor.__new__(Tensor)
        tensor._init(op, inputs)
        return tensor
    
    def arcsin(self):
        
        if MOD[0] == "IMM":
            tensor = Tensor(self.cached_data.arcsin())
        else:
            tensor = Tensor.make_from_op(EWiseArcSin(), [self])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor
    
    def arccos(self):
        if MOD[0] == "IMM":
            tensor = Tensor(self.cached_data.arccos())
        else:
            tensor = Tensor.make_from_op(EWiseArcCos(), [self])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor
    
    def arctan(self):
        if MOD[0] == "IMM":
            tensor = Tensor(self.cached_data.arctan())
        else:
            tensor = Tensor.make_from_op(EWiseArcTan(), [self])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor
    
    def sign(self):
        if MOD[0] == "IMM":
            tensor = Tensor(self.cached_data.sign())
        else:
            tensor = Tensor.make_from_op(EWiseSign(), [self])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor
    
    def sqrt(self):
        if MOD[0] == "IMM":
            tensor = Tensor(self.cached_data.sqrt())
        else:
            tensor = Tensor.make_from_op(EWiseSqrt(), [self])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor
    
    def abs(self):
        if MOD[0] == "IMM":
            tensor = Tensor(self.cached_data.abs())
        else:
            tensor = Tensor.make_from_op(EWiseAbs(), [self])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor
    
    def exp(self):
        if MOD[0] == "IMM":
            tensor = Tensor(self.cached_data.exp())
        else:
            tensor = Tensor.make_from_op(EWiseExp(), [self])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor
    
    def ceil(self):
        if MOD[0] == "IMM":
            tensor = Tensor(self.cached_data.ceil())
        else:
            tensor = Tensor.make_from_op(EWiseCeil(), [self])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor
    
    def floor(self):
        if MOD[0] == "IMM":
            tensor = Tensor(self.cached_data.floor())
        else:
            tensor = Tensor.make_from_op(EWiseFloor(), [self])
            if MOD[0] == "Async":
                tensor.realize_cached_data
        return tensor
    
    def wait(self):
        self.realize_cached_data.wait()
        return self
    
    def __len__(self):
        return self.shape[0]
