#include <Python.h>
#include <math.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdio.h>

#define new(x) (x *)malloc(sizeof(x))
#define new_array(x, y) (x *)malloc(sizeof(x) * y)

typedef struct {
    PyObject_HEAD

    unsigned int bit1 : 1;
    unsigned int bit2 : 1;
    unsigned int bit3 : 1;
    unsigned int bit4 : 1;
    unsigned int bit5 : 1;
    unsigned int bit6 : 1;
    unsigned int bit7 : 1;
    unsigned int bit8 : 1;
} Byte_t;

typedef struct {
    PyObject_HEAD

    Byte_t* data;
    int size;

} BitmapObject;

static void init_byte(Byte_t *byte) {
    byte->bit1 = 0;
    byte->bit2 = 0;
    byte->bit3 = 0;
    byte->bit4 = 0;
    byte->bit5 = 0;
    byte->bit6 = 0;
    byte->bit7 = 0;
    byte->bit8 = 0;
}


static void _byte_set_bit(Byte_t *byte, int bit_index, int value){
    switch(bit_index){
        case 0: byte->bit1 = value; break;
        case 1: byte->bit2 = value; break;
        case 2: byte->bit3 = value; break;
        case 3: byte->bit4 = value; break;
        case 4: byte->bit5 = value; break;
        case 5: byte->bit6 = value; break;
        case 6: byte->bit7 = value; break;
       case 7: byte->bit8 = value; break;
    }
}

static int _byte_get_bit(Byte_t* byte, int bit_index){
    switch(bit_index){
        case 0: return byte->bit1;
        case 1: return byte->bit2;
        case 2: return byte->bit3;
        case 3: return byte->bit4;
        case 4: return byte->bit5;
        case 5: return byte->bit6;
        case 6: return byte->bit7;
        case 7: return byte->bit8;
    }
}

bool check_index(int num, int start, int end){
    return (num >= start && num < end);
}

static PyObject* byte_get_bit(Byte_t *self, PyObject *args){
    int bit_index;
    if(!PyArg_ParseTuple(args, "i", &bit_index)){
        PyErr_BadArgument();
    }
    if (bit_index < 0){
        bit_index += 8;
    }
    if (!check_index(bit_index, 0, 8)){
        PyErr_SetString(PyExc_IndexError, "Index out of range");
    }
    return PyLong_FromLong(_byte_get_bit(self, bit_index));
}

static PyObject* byte_set_bit(Byte_t *self, PyObject *args){
    int bit_index, value;
    if(!PyArg_ParseTuple(args, "ii", &bit_index, &value)){
        PyErr_BadArgument();
    }
    if (bit_index < 0){
        bit_index += 8;
    }
    if (!check_index(bit_index, 0, 8)){
        PyErr_SetString(PyExc_IndexError, "Index out of range");
    }
    _byte_set_bit(self, bit_index, value);
    Py_RETURN_NONE;
}

static long byte_to_int(Byte_t *byte){
    // PyErr_SetString(PyExc_OverflowError, "Overflow error");
    return (
        ((long)(byte->bit1)) |
        (((long)(byte->bit2)) << 1) |
        (((long)(byte->bit3)) << 2) |
        (((long)(byte->bit4)) << 3) |
        (((long)(byte->bit5)) << 4) |
        (((long)(byte->bit6)) << 5) |
        (((long)(byte->bit7)) << 6) |
        (((long)(byte->bit8)) << 7));
}

static PyObject* bitmap_to_bytes(BitmapObject *self) {
    char *bytes = new_array(char, self->size);
    // PyErr_SetString(PyExc_OverflowError, "Overflow error");
    long i = 0;
    for(; i < (self->size); i++){
        long ttemp = byte_to_int(&self->data[i]);
        bytes[i] = (char)ttemp;
    }
    return PyBytes_FromStringAndSize(bytes, self->size);
}

static int Bitmap_init(BitmapObject *self, PyObject *args, PyObject *kwds) {
    PyObject *size_or_bits_obj = NULL;
    static char *kwlist[] = {"size_or_bits", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O", kwlist, &size_or_bits_obj)) {
        return -1;
    }

    if (PyLong_Check(size_or_bits_obj)) {
        // Initialize with an integer (size of the bitmap)
        self->size = PyLong_AsLong(size_or_bits_obj);
        if (self->size == -1 && PyErr_Occurred()) {
            return -1;  // If PyLong_AsLong failed, return -1
        }

        self->data = new_array(Byte_t, self->size);
        if (self->data == NULL) {
            PyErr_SetString(PyExc_MemoryError, "Failed to allocate memory for bitmap data");
            return -1;
        }

        for (int i = 0; i < self->size; i++) {
            init_byte(&self->data[i]);
        }
    } else if (PySequence_Check(size_or_bits_obj)) {
        // Initialize with a sequence of booleans
        Py_ssize_t seq_length = PySequence_Size(size_or_bits_obj);
        if (seq_length == -1) {
            return -1;  // If PySequence_Size failed, return -1
        }

        self->size = (seq_length + 7) / 8;  // Calculate the number of bytes needed
        self->data = new_array(Byte_t, self->size);
        if (self->data == NULL) {
            PyErr_SetString(PyExc_MemoryError, "Failed to allocate memory for bitmap data");
            return -1;
        }

        for (int i = 0; i < seq_length; i++) {
            PyObject *item = PySequence_GetItem(size_or_bits_obj, i);
            if (!PyBool_Check(item)) {
                PyErr_SetString(PyExc_TypeError, "All elements in the sequence must be booleans");
                Py_DECREF(item);
                return -1;
            }

            int byte_index = i / 8;
            int bit_index = i % 8;
            Byte_t *byte = &self->data[byte_index];
            _byte_set_bit(byte, bit_index, PyObject_IsTrue(item));
            Py_DECREF(item);
        }
    } else {
        PyErr_SetString(PyExc_TypeError, "Expected an integer or a sequence of booleans");
        return -1;
    }

    return 0;  // Initialization successful
}




static PyObject* bitmap_set_bit(BitmapObject *self, PyObject *args) {
    int index, value;
    if (!PyArg_ParseTuple(args, "ii", &index, &value)) {
        return NULL;
    }
    int byte_index = index / 8;
    int bit_index = index % 8;
    if (byte_index >= self->size) {
        PyErr_SetString(PyExc_IndexError, "Index out of range");
        return NULL;
    }
    Byte_t *byte = &self->data[byte_index];
    switch (bit_index) {
        case 0: byte->bit1 = value; break;
        case 1: byte->bit2 = value; break;
        case 2: byte->bit3 = value; break;
        case 3: byte->bit4 = value; break;
        case 4: byte->bit5 = value; break;
        case 5: byte->bit6 = value; break;
        case 6: byte->bit7 = value; break;
        case 7: byte->bit8 = value; break;
        default: break;
    }
    Py_RETURN_NONE;
}

static PyObject* bitmap_set_bits(BitmapObject *self, PyObject *args) {
    long start, end, step;
    bool on;
    if(!PyArg_ParseTuple(args, "lll", &start, &end, &step, &on)){
        PyErr_BadArgument();
    }
    if (start < 0)start += self->size;
    if (end < 0)end += self->size;
    if (step == 0)PyErr_SetString(PyExc_ValueError, "Step cannot be zero");
    if (start < 0 || end < 0 || step < 0 || start >= self->size || end >= self->size) {
        PyErr_SetString(PyExc_IndexError, "Index out of range");
        return NULL;
    }
    for(long i = start; i < end; i += step)bitmap_set_bit(self, Py_BuildValue("ii", i, on));
}

static PyObject* bitmap_get_bit(BitmapObject *self, PyObject *args) {
    int index;
    if (!PyArg_ParseTuple(args, "i", &index)) {
        return NULL;
    }
    int byte_index = index / 8;
    int bit_index = index % 8;
    if (byte_index >= self->size) {
        PyErr_SetString(PyExc_IndexError, "Index out of range");
        return NULL;
    }
    Byte_t *byte = &self->data[byte_index];
    bool value = _byte_get_bit(byte, bit_index);
    return PyBool_FromLong(value);
}

static PyObject* bitmap_get_size(BitmapObject *self) {
    return PyLong_FromLong(self->size);
}

static PyObject* bitmap_byte_at(BitmapObject *self, PyObject* args){
    long indexl;
    if (!PyArg_ParseTuple(args, "l", &indexl)){
        return NULL;
    };
    if (indexl < 0){
        indexl = self->size + indexl;
    }
    if (indexl < 0 || indexl >= self->size){
        PyErr_SetString(PyExc_IndexError, "Index out of range");
    }
    PyObject* result = PyLong_FromLong(byte_to_int(&self->data[indexl/8]));
    if (PyErr_Occurred()){
        return NULL;
    }
    return result;
}



static void bitmap_dealloc(BitmapObject *self) {
    free(self->data);
    Py_TYPE(self)->tp_free((PyObject *)self);
}



static PyMethodDef BitmapMethods[] = {
    {"_C_set_bit", (PyCFunction)bitmap_set_bit, METH_VARARGS, "Set a bit in the bitmap"},
    {"_C_get_bit", (PyCFunction)bitmap_get_bit, METH_VARARGS, "Get a bit from the bitmap"},
    {"_C_get_size", (PyCFunction)bitmap_get_size, METH_NOARGS, "Get the size of the bitmap"},
    {"_C_to_bytes", (PyCFunction)bitmap_to_bytes, METH_NOARGS, "Convert the bitmap to bytes"},
    {"_C_byte_at", (PyCFunction)bitmap_byte_at, METH_VARARGS, "Get a byte from the bitmap"},
    {NULL, NULL, 0, NULL}
};


static PyMethodDef ByteMethods[] = {
    {"_C_set_bit", (PyCFunction)byte_set_bit, METH_VARARGS, "Set a range of bits in the bitmap"},
    {"_C_get_bit", (PyCFunction)byte_get_bit, METH_VARARGS, "Get a range of bits from the bitmap"},
    {NULL, NULL, 0, NULL}
};



static PyTypeObject BitmapType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "bitmap.Bitmap",
    .tp_doc = "Bitmap objects",
    .tp_basicsize = sizeof(BitmapObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)Bitmap_init,
    .tp_dealloc = (destructor)bitmap_dealloc,
    .tp_methods = BitmapMethods,
};





static struct PyModuleDef bitmapmodule = {
    PyModuleDef_HEAD_INIT,
    .m_name = "bitmap",
    .m_doc = "Example module that creates an extension type.",
    .m_size = -1,
    .m_methods = BitmapMethods,
    .m_slots = NULL,
    .m_traverse = NULL,
    .m_clear = NULL,
    .m_free = NULL,
};

PyMODINIT_FUNC PyInit_pybitmap(void) {
    PyObject *m;
    if (PyType_Ready(&BitmapType) < 0) {
        return NULL;
    }
    m = PyModule_Create(&bitmapmodule);
    if (m == NULL) {
        return NULL;
    }
    Py_INCREF(&BitmapType);
    if (PyModule_AddObject(m, "Bitmap", (PyObject *)&BitmapType) < 0) {
        Py_DECREF(&BitmapType);
        Py_DECREF(m);
        return NULL;
    }
    return m;
}