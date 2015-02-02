extern "C"
{
#include "bz2search.c"
}
#include <Python.h>
#include "gtest/gtest.h"
#include <stdio.h>
#define SAMPLE "../../logbinsearch/test/sample/sample.bz2"
#define SAMPLE2 "../../logbinsearch/test/sample/sample_1block.bz2"

TEST(AddTest, Test1)
{
ASSERT_EQ(2, 1+1);
}
TEST(getBitsTest, Test1)
{
    FILE *file = fopen(SAMPLE, "r");
    if (file == NULL) {
        printf("fopen error\n");
        exit(EXIT_FAILURE);
    }
    BitStream* bs = (BitStream*)malloc( sizeof(BitStream) );
    bs->file = file;
    bs->buffer = 0;
    bs->buffsize = 0;
    int b = 0, i = 24;
    for(i=0; i< 24; ++i){
        b = (b<<1) | (getBits(bs) & 1);
    }
    ASSERT_EQ(4348520, b);
    fclose(file);
    free(bs);
}
TEST(BZ2SearchTest, Test1)
{
    FILE *fp;
    BlockReader *self;
    int res;
    PyObject *p;
    Py_Initialize();
    printf(SAMPLE"\n");
    fp = fopen(SAMPLE, "rb");
    if (fp == NULL) {
        printf("fopen error\n");
        exit(EXIT_FAILURE);
    }
    int fd = fileno(fp);
    self = (BlockReader*)malloc(sizeof(BlockReader));
    if (self == NULL){
        printf("malloc error\n");
        exit(EXIT_FAILURE);
    }
    long pos = bz2s_searchBlock(fp, 5);
    ASSERT_LT(100, pos);
    lseek( fd, 0, SEEK_SET );
    printf("pos: %ld\n", pos);
    res = bz2s_initBlock(self, fd, pos);
    ASSERT_EQ(0, res);
    ASSERT_NE((bunzip_data*)NULL, self->bd);
    p = Reader_iternext(self);
    ASSERT_NE((PyObject*)NULL, p);

    long pos2, prev;
    pos2 = 0;
    prev = pos2;
    while(1){
        fp = fopen(SAMPLE, "rb");
        pos2 = bz2s_searchBlock(fp, (prev+8)/8);
        printf("prev: %ld, pos2: %ld\n", prev, pos2);
        if(pos2==prev)
            break;
        if(pos2<0)
            break;

        prev = pos2;
    }

    ASSERT_EQ(-1, pos2);
    lseek( fd, 0, SEEK_SET );
    printf("prev: %ld\n", prev);
    res = bz2s_initBlock(self, fd, prev);
    ASSERT_EQ(0, res);
    ASSERT_NE((bunzip_data*)NULL, self->bd);
    ASSERT_NE((PyObject*)NULL, p);
    while(p!=NULL){
        p = Reader_iternext(self);
    }
    free(self);
    ASSERT_FALSE(PyErr_Occurred());
    if (PyErr_Occurred())
        PyErr_Print();
}
TEST(BZ2SearchTest2, Test1)
{
    FILE *fp;
    BlockReader *self;
    PyObject *p;
    int res;
    Py_Initialize();
    printf(SAMPLE2"\n");
    fp = fopen(SAMPLE2, "rb");
    if (fp == NULL) {
        printf("fopen error\n");
        exit(EXIT_FAILURE);
    }
    self = (BlockReader*)malloc(sizeof(BlockReader));
    if (self == NULL){
        printf("malloc error\n");
        exit(EXIT_FAILURE);
    }

    long pos = bz2s_searchBlock(fp, 0);
    ASSERT_EQ(32, pos);
    fp = fopen(SAMPLE2, "rb");
    int fd = fileno(fp);
    lseek( fd, 0, SEEK_SET );
    res = bz2s_initBlock(self, fd, pos);
    ASSERT_EQ(0, res);
    ASSERT_NE((bunzip_data*)NULL, self->bd);
    p = Reader_iternext(self);
    ASSERT_NE((PyObject*)NULL, p);
}

int main(int argc, char **argv) {
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
