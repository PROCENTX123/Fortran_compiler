import enum
from llvmlite import ir


class Type:
    name = "undefined"
    mangle_suff = "Und"

    def __eq__(self, other):
        return isinstance(other, type(self))

    def __ne__(self, other):
        return not self.__eq__(other)

    def default_value(self):
        return None

    def castable_to(self, other_type):
        raise NotImplementedError()

    def cast_to(self, other_type, builder: ir.IRBuilder):
        raise NotImplementedError()

    def __str__(self):
        return "Auto"

    def llvm_type(self):
        pass


class NumericT(Type):
    name = "numeric"
    mangle_suff = "N"
    priority = 0

    def default_value(self):
        return 0

    def castable_to(self, other_type):
        return isinstance(other_type, NumericT) and self.priority <= other_type.priority

    def cmp(self, op, builder: ir.IRBuilder, name: str = None):
        raise NotImplementedError("cmp for NumericT")

    def add(self, builder: ir.IRBuilder, name: str = None):
        raise NotImplementedError("add for NumericT")

    def sub(self, builder: ir.IRBuilder, name: str = None):
        raise NotImplementedError("sub for NumericT")

    def mul(self, builder: ir.IRBuilder, name: str = None):
        raise NotImplementedError("mul for NumericT")

    def div(self, builder: ir.IRBuilder, name: str = None):
        raise NotImplementedError("div for NumericT")

    def neg(self, builder: ir.IRBuilder, name: str = None):
        raise NotImplementedError("neg for NumericT")


class IntegralT(NumericT):
    name = "integral"
    mangle_suff = "N"
    priority = 0

    def cast_to(self, other_type, builder: ir.IRBuilder):
        if isinstance(other_type, IntegralT):
            return lambda x: builder.zext(x, other_type.llvm_type())
        elif isinstance(other_type, FloatingPointT):
            return lambda x: builder.sitofp(x, other_type.llvm_type())
        else:
            return None

    def add(self, builder: ir.IRBuilder, name: str = None):
        return lambda lhs, rhs: builder.add(lhs, rhs, name if name else '')

    def sub(self, builder: ir.IRBuilder, name: str = None):
        return lambda lhs, rhs: builder.sub(lhs, rhs, name if name else '')

    def mul(self, builder: ir.IRBuilder, name: str = None):
        return lambda lhs, rhs: builder.mul(lhs, rhs, name if name else '')

    def div(self, builder: ir.IRBuilder, name: str = None):
        return lambda lhs, rhs: builder.sdiv(lhs, rhs, name if name else '')

    def neg(self, builder: ir.IRBuilder, name: str = None):
        return lambda lhs: builder.neg(lhs, name if name else '')


class FloatingPointT(NumericT):
    name = "floating_point"
    mangle_suff = "N"
    priority = 0

    def cast_to(self, other_type, builder: ir.IRBuilder):
        if isinstance(other_type, FloatingPointT):
            return lambda x: builder.fpext(x, other_type.llvm_type())
        else:
            return None

    def add(self, builder: ir.IRBuilder, name: str = None):
        return lambda lhs, rhs: builder.fadd(lhs, rhs, name if name else '')

    def sub(self, builder: ir.IRBuilder, name: str = None):
        return lambda lhs, rhs: builder.fsub(lhs, rhs, name if name else '')

    def mul(self, builder: ir.IRBuilder, name: str = None):
        return lambda lhs, rhs: builder.fmul(lhs, rhs, name if name else '')

    def div(self, builder: ir.IRBuilder, name: str = None):
        return lambda lhs, rhs: builder.fdiv(lhs, rhs, name if name else '')

    def neg(self, builder: ir.IRBuilder, name: str = None):
        return lambda lhs: builder.fneg(lhs, name if name else '')



class IntegerT(IntegralT):
    name = "integer"
    priority = 2

    def __str__(self):
        return "Integer"

    def llvm_type(self):
        return ir.IntType(32)


class FloatT(FloatingPointT):
    name = "!"
    priority = 4

    def __str__(self):
        return "Float"

    def llvm_type(self):
        return ir.FloatType()


class ArrayT(Type):
    name = "dimension"

    def __init__(self, valueT:Type, size: list[int]):
        self.type = valueT
        self.size = size


    def __eq__(self, other):
        if isinstance(other, ArrayT):
            self_any = self.type == Type()
            other_any = other.type == Type()
            if self_any or other_any:
                return self.size == other.size if len(self.size) != 1 and len(other.size) != 1 else True
            else:
                return self.type == other.type and len(self.size) == len(other.size)
        return False

    def __str__(self):
        return f"{self.type}[]"

    def default_value(self):
        sz = self.size[0] if not hasattr(self.size[0], "value") else self.size[0].value
        if len(self.size) == 1:
            return [0] * sz
        elif len(self.size) >= 1:
            return [ArrayT(self.type, self.size[1:]).default_value()] * sz


    def llvm_type(self):
        if self.is_function_param:
            return self.llvm_type_ref()
        else:
            return self.llvm_type_init()

    def llvm_type_init(self):
        if len(self.size) == 1:
            return ir.ArrayType(self.type.llvm_type(), self.size[0])
        elif len(self.size) >= 1:
            return ir.ArrayType(ArrayT(self.type, self.size[1:]).llvm_type_init(), self.size[0])

    def llvm_type_ref(self):
        if len(self.size) == 1:
            return ir.PointerType(self.type.llvm_type(), self.size[0])
        elif len(self.size) >= 1:
            return ir.PointerType(ArrayT(self.type, self.size[1:]).llvm_type_ref(), self.size[0])

    def cast_to(self, other_type, builder: ir.IRBuilder):
        def casting(lhs_val_list, rhs_val_list):
            result = []
            for lhs_val, rhs_val in zip(lhs_val_list, rhs_val_list):
                result.append(self.type.cast_to(other_type, builder)(lhs_val, rhs_val))
            return result
        return casting

    def castable_to(self, other_type):
        return self.size == other_type.size and self.type == other_type.type


class FunctionsT(Type):
    name = "func"

    def __init__(self, retT: Type, argsT: list[Type]):
        self.retT = retT
        self.argsT = argsT

    def __str__(self):
        return f"{self.retT}(" + ','.join([str(v) for v in self.argsT]) + ")"

    def castable_to(self, other_type):
        result = self.retT == other_type.retT and len(self.argsT) == len(other_type.argsT)
        if not result:
            return False
        for idx in range(len(self.argsT)):
            result &= self.argsT[idx].castable_to(other_type.argsT[idx])
        return result