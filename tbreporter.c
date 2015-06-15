
#define UNW_LOCAL_ONLY
#define _GNU_SOURCE
#include <libunwind.h>
#include <dlfcn.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#define MAX_STACK_DEPTH 1024
#define BUFFER_SIZE 8192

int tbreporter_get_tb(void** result, int max_depth, ucontext_t *ucontext)
{
    void *ip;
    unw_cursor_t cursor;
    unw_context_t uc = *ucontext;
 
    int ret = unw_init_local(&cursor, &uc);
    int n = 0;
    while (n < max_depth) {
        if (unw_get_reg(&cursor, UNW_REG_IP, (unw_word_t *) &ip) < 0) {
            break;
        } 
        result[n++] = ip;
        if (unw_step(&cursor) <= 0) {
            break;
        }
    }
    return n;
}

char *format_addr(void* sym)
{
    Dl_info info;
    char *buf;
    if (dladdr(sym, &info) == 0) {
        return NULL;
    }
    if (!info.dli_sname) {
        buf = (char*)malloc(strlen(info.dli_fname) + 17);
        sprintf(buf, "%s <no debug data>", info.dli_fname);
        return buf;
    }
    buf = (char*)malloc(strlen(info.dli_fname) + 2 +
                              strlen(info.dli_sname));
    if (!buf) {
        return NULL;
    }
    sprintf(buf, "%s %s", info.dli_fname, info.dli_sname);
    return buf;
}
