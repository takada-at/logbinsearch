extern "C"
{
#include "bz2search.c"
}
#include <Python.h>
#include "gtest/gtest.h"
#include <stdio.h>
#define SAMPLE "../../logbinsearch/test/sample/sample.bz2"

TEST(AddTest, Test1)
{
ASSERT_EQ(2, 1+1);
}
TEST(BZ2SearchTest, Test1)
{
    FILE *fp;
    BlockReader *self;
    int res;
    PyObject *p;
    Py_Initialize();
    printf(SAMPLE"\n");
    fp = fopen(SAMPLE, "r");
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
        pos2 = bz2s_searchBlock(fp, (prev+40)/8);
        printf("prev: %ld, pos2: %ld\n", prev, pos2);
        if(pos2==prev)
            break;
        if(pos2<0)
            break;

        prev = pos2;
    }
    ASSERT_EQ(-1, pos2);
    lseek( fd, 0, SEEK_SET );
    res = bz2s_initBlock(self, fd, prev);
    ASSERT_EQ(0, res);
    ASSERT_NE((bunzip_data*)NULL, self->bd);
    ASSERT_NE((PyObject*)NULL, p);
    int cnt = 0;
    while(p!=NULL){
        p = Reader_iternext(self);
        ++cnt;
    }
    printf("cnt: %d\n", cnt);
    ASSERT_GT(5, cnt);
    free(self);
}


int main(int argc, char **argv) {
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
