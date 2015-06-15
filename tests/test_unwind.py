
import py
import cffi

ffi = cffi.FFI()
ffi.cdef("""
typedef struct {
  ...;
} ucontext_t;

int getcontext(ucontext_t *ucp);
void free(char *ptr);

int tbreporter_get_tb(void** result, int max_depth, ucontext_t *ucontext);
char *format_addr(void* sym);
char *serialize_traceback();

int wrapper(void** result, int max_depth, ucontext_t *ucontext);
""")
lib = ffi.verify("""
#include <ucontext.h>

int wrapper(void **result, int max_depth, ucontext_t *ucontext)
{
    return tbreporter_get_tb(result, max_depth, ucontext);
}
""", library_dirs=[str(py.path.local(__file__).join('..', '..'))],
    libraries=['tbreporter', 'unwind'])

def test_get_tb():
    ctx = ffi.new("ucontext_t*")
    assert lib.getcontext(ctx) == 0
    buf = ffi.new("void*[1024]")
    n = lib.wrapper(buf, 1024, ctx)
    assert n >= 5
    all_syms = []
    for i in range(n - 1):
        res = lib.format_addr(buf[i])
        all_syms.append(ffi.string(res))
        lib.free(res)
    assert "python PyEval_EvalFrameEx" in all_syms
    assert "python PyEval_EvalCodeEx" in all_syms

def test_serialize_tb():
    ll_res = lib.serialize_traceback()
    res = ffi.string(ll_res)
    lib.free(ll_res)
    assert ("python PyEval_EvalFrameEx\npython PyEval_EvalFrameEx" in res)
