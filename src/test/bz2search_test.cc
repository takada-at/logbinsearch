extern "C"
{
#include "bz2search.c"
}
#include "gtest/gtest.h"
#include <stdio.h>
#define SAMPLE "../../filebinsearch/test/sample/sample.bz2"

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
    ASSERT_EQ(3770, pos);
    lseek( fd, 0, SEEK_SET );
    res = bz2s_initBlock(self, fd, pos);
    ASSERT_EQ(0, res);
    ASSERT_NE((bunzip_data*)NULL, self->bd);
    p = Reader_iternext(self);
    ASSERT_NE((PyObject*)NULL, p);
    free(self);
}


int main(int argc, char **argv) {
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
