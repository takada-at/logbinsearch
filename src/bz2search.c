#define MODULE_VERSION "0.0.1"
#include <Python.h>
#include "structmember.h"
#include "microbunzip.h"

#define BUF_SIZE 8192
#define BLOCK_HEADER0 0x314159UL
#define BLOCK_HEADER1 0x265359UL
#define MIN(X, Y) (((X) < (Y)) ? (X) : (Y))

static PyObject *error_obj;     /*  exception */

typedef struct {
    PyObject_HEAD
    long startpos;
    bunzip_data *bd;
    int end;
} BlockReader;

typedef struct
{
    FILE *file;
    int buffer;
    int buffsize;
} BitStream;

static int
mbz2_error(int status)
{
    switch(status){
    case RETVAL_OK:
        return 0;
    case RETVAL_LAST_BLOCK:
        PyErr_Format(error_obj,
                     "unexpected end of data");
        return -1;
    case RETVAL_NOT_BZIP_DATA:
        PyErr_Format(error_obj,
                     "not bzip data");
        return -1;
    case RETVAL_UNEXPECTED_INPUT_EOF:
        PyErr_Format(error_obj,
                     "unexpected input eof");
        return -1;
    case RETVAL_UNEXPECTED_OUTPUT_EOF:
        PyErr_Format(error_obj,
                     "unexpected output eof");
        return -1;
    case RETVAL_DATA_ERROR:
        PyErr_Format(error_obj,
                     "data error");
        return -1;
    case RETVAL_OUT_OF_MEMORY:
        PyErr_NoMemory();
        return -1;
    case RETVAL_OBSOLETE_INPUT:
        PyErr_Format(error_obj,
                     "obsolete input");
        return -1;
    }
    return 0;
}

/**
 * BlockReader
 */
static int bz2s_seek(bunzip_data *bd, int fd, long pos)
{
    off_t bytes; char bit;
    bytes = pos / 8;
    bit   = pos % 8;
    if(lseek( fd, bytes, SEEK_SET ) != bytes)
    {
        PyErr_Format(error_obj,
                     "lseek error");
        return -1;
    }
    bd->inbufBitCount = bd->inbufPos = bd->inbufCount = 0;
    get_bits(bd, bit);
    return (int)pos;
}
static PyObject*
Reader_reset(BlockReader *self)
{
    self->end = 0;
    bz2s_seek(self->bd, self->bd->in_fd, self->startpos);
    Py_RETURN_NONE;
}
static PyObject*
Reader_iternext(BlockReader *self)
{
    if(self->end)
        return NULL;
    bunzip_data *bd = self->bd;
    char *line, *buff, *end;
    int gotcount;
    int errorstatus = 0;
    int readcount = 0;
    char c;
    line = (char *)PyMem_Malloc(sizeof(char) * BUF_SIZE);
    if(line==NULL){
        PyErr_NoMemory();
        return NULL;
    }
    buff = line;
    end  = buff + BUF_SIZE;
    Py_BEGIN_ALLOW_THREADS
    while(buff!=end){
        gotcount = read_bunzip(bd, &c, 1);
        if(gotcount==0){
            self->end = 1; break;
        }else if(gotcount==-1){
            self->end = 1; break;
        }else if(gotcount < 0){
            errorstatus = gotcount; break;
        }
        ++readcount;
        *buff++ = c;
        if(c=='\n') break;
    }
    Py_END_ALLOW_THREADS
    if(errorstatus<0){
        mbz2_error(errorstatus);
        return NULL;
    }
    if(readcount==0){
        return NULL;
    }
    return PyString_FromStringAndSize(line, readcount);
}

static int bz2s_initBlock(BlockReader *self, int fd, long pos)
{
    bunzip_data *bd;
    int status;
    if ( ( status = start_bunzip( &bd, fd, 0, 0 ) )==0 ){
        bz2s_seek(bd, fd, pos);
        if ( ( status = get_next_block( bd ) ) ){
            mbz2_error(status);
            return -1;
        }
        bd->writeCRC = 0xffffffffUL;
        bd->writeCopies = 0;
        self->bd = bd;
        self->startpos = pos;
        self->end = 0;
        return 0;
    }else{
        mbz2_error(status);
        return -1;
    }
    return 0;
}
static char *block_kws[] = {
    "file",
    "pos",
    NULL
};
static int
Reader_init(BlockReader *self, PyObject *args, PyObject *kwargs)
{
    PyObject *pyfile = NULL;
    FILE *file;
    long pos = 0;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O|l", block_kws, 
                                     &pyfile, &pos)){
        return -1;
    }
    if (!PyFile_Check(pyfile)){
        PyErr_Format(PyExc_TypeError,
                     "file must be file object");
        return -1;
    }
    file = PyFile_AsFile(pyfile);
    int fd = fileno(file);
    if(fd < 0){
        PyErr_Format(error_obj,
                     "fileno error");
        return -1;
    }
    if(lseek( fd, 0, SEEK_SET ) != 0)
    {
        PyErr_Format(error_obj,
                     "lseek error");
        return -1;
    }
    self->bd = NULL;
    return bz2s_initBlock(self, fd, pos);
}
static PyObject *
Reader_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    BlockReader *self;

    self = (BlockReader *)type->tp_alloc(type, 0);
    if (self == NULL){
        return NULL;
    }
    return (PyObject *)self;
}
static void
Reader_dealloc(BlockReader *self)
{
    if (self->bd != NULL){
        if ( self->bd->dbuf ) PyMem_Free( self->bd->dbuf );
        PyMem_Free(self->bd);
    }
    self->ob_type->tp_free((PyObject*)self);
}

PyDoc_STRVAR(BlockReader_Type_doc,
"BZ2 block reader\n"
);

static struct PyMethodDef Reader_methods[] = {
    {"reset", (PyCFunction)Reader_reset,  METH_NOARGS, "seek to start point"},
    { NULL, NULL }
};

static struct PyMemberDef Reader_memberlist[] = {
    { NULL }
};

static PyTypeObject BlockReader_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "bz2search.BlockReader",                /*tp_name*/
    sizeof(BlockReader),                    /*tp_basicsize*/
    0,                                      /*tp_itemsize*/
    /* methods */
    (destructor)Reader_dealloc,             /*tp_dealloc*/
    (printfunc)0,                           /*tp_print*/
    (getattrfunc)0,                         /*tp_getattr*/
    (setattrfunc)0,                         /*tp_setattr*/
    (cmpfunc)0,                             /*tp_compare*/
    (reprfunc)0,                            /*tp_repr*/
    0,                                      /*tp_as_number*/
    0,                                      /*tp_as_sequence*/
    0,                                      /*tp_as_mapping*/
    (hashfunc)0,                            /*tp_hash*/
    (ternaryfunc)0,                         /*tp_call*/
    (reprfunc)0,                                /*tp_str*/
    0,                                      /*tp_getattro*/
    0,                                      /*tp_setattro*/
    0,                                      /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    BlockReader_Type_doc,                     /*tp_doc*/
    (traverseproc)0,                        /*tp_traverse*/
    (inquiry)0,                             /*tp_clear*/
    0,                                      /*tp_richcompare*/
    0,                                      /*tp_weaklistoffset*/
    PyObject_SelfIter,                          /*tp_iter*/
    (getiterfunc)Reader_iternext,           /*tp_iternext*/
    Reader_methods,                         /*tp_methods*/
    Reader_memberlist,                      /*tp_members*/
    0,                                      /*tp_getset*/
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)Reader_init,               /* tp_init */
    0,                         /* tp_alloc */
    Reader_new,                         /* tp_new */

};

static int getBits(BitStream* bs)
{
   if (bs->buffsize > 0) {
      bs->buffsize--;
      return (((bs->buffer) >> (bs->buffsize)) & 0x1 );
   } else {
      int val = getc(bs->file);
      if ( val == EOF ) {
         return 2;
      }
      bs->buffsize = 7;
      bs->buffer = val;
      return (((bs->buffer) >> 7) & 0x1);
   }
}

static long bz2s_searchBlock(FILE* file, long pos)
{
    int b;
    int readbuff = 0;
    long readbit = 0;
    int state = 0;
    long searchpos = 0;
    BitStream* bs = (BitStream*)PyMem_Malloc( sizeof(BitStream) );
    if (bs == NULL) {
        PyErr_NoMemory();
        return -1;
    }
    bs->file = file;
    bs->buffer = 0;
    bs->buffsize = 0;
    fseek(file, pos, SEEK_SET);
    while(1){
        b = getBits(bs);
        if (b>=2){
            PyMem_Free(bs);
            return -1;
        }
        ++readbit;
        readbuff = (readbuff << 1) | (b & 1);
        if (state == 0 && (readbuff & 0x00ffffff) == BLOCK_HEADER0){
            state = 1;
        }else if(state==1 && (readbuff & 0x00ffffff) == BLOCK_HEADER1){
            state = 0;
            searchpos = readbit / 8;
            PyMem_Free(bs);
            return pos * 8 + readbit - 48;
        }
    }
    PyMem_Free(bs);
    return -1;
}

static PyObject* pybz2s_searchBlock(PyObject *self, PyObject *args)
{
    PyObject *pyfile = NULL;
    long pos = 0;
    FILE *file;
    long block;
    if (!PyArg_ParseTuple(args, "O|l", &pyfile, &pos)){
        return NULL;
    }

    if (!PyFile_Check(pyfile)){
        PyErr_Format(PyExc_TypeError,
                     "file must be file object");
        return NULL;
    }

    file = PyFile_AsFile(pyfile);
    PyFile_IncUseCount((PyFileObject*)pyfile);
    Py_BEGIN_ALLOW_THREADS
    block = bz2s_searchBlock(file, pos);
    Py_END_ALLOW_THREADS
    PyFile_DecUseCount((PyFileObject*)pyfile);
    return Py_BuildValue("i", block);
}

static PyMethodDef Bz2SearchMethods[] = {
    {"searchblock",  pybz2s_searchBlock, METH_VARARGS,
     "Search BZ2 Block."},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC
initbz2search(void)
{
    PyObject *m;
    if (PyType_Ready(&BlockReader_Type) < 0)
        return;
    m = Py_InitModule("bz2search", Bz2SearchMethods);
    if (m == NULL)
        return;

    Py_INCREF(&BlockReader_Type);
    if (PyModule_AddObject(m, "BlockReader", (PyObject *)&BlockReader_Type))
        return;
    error_obj = PyErr_NewException("bz2search.BZ2Error", NULL, NULL);
    if (error_obj == NULL)
        return;

    PyModule_AddObject(m, "BZ2Error", error_obj);
}
