
#ifndef MYPRINT_H
#define MYPRINT_H

#include <stdio.h>

#include "mutex.h"

#ifdef __cplusplus
extern "C" {
#endif

extern mutex_t myprint_lock;

#define myputs(arg)     do { \
    mutex_lock(&myprint_lock); \
    puts(arg); \
    mutex_unlock(&myprint_lock); } while (0U)

#define myprintf(...)   do { \
    mutex_lock(&myprint_lock); \
    printf(__VA_ARGS__); \
    mutex_unlock(&myprint_lock); } while (0U)

#ifdef __cplusplus
}
#endif

#endif /* MYPRINT_H */
/** @} */
