# Declare the C functions and types
from libc.stdint cimport uint32_t

cdef extern from "params.h":

    ctypedef struct xmss_params:
        unsigned int func
        unsigned int n
        unsigned int padding_len
        unsigned int wots_w
        unsigned int wots_log_w
        unsigned int wots_len1
        unsigned int wots_len2
        unsigned int wots_len
        unsigned int wots_sig_bytes
        unsigned int full_height
        unsigned int tree_height
        unsigned int d
        unsigned int index_bytes
        unsigned int sig_bytes
        unsigned int pk_bytes
        unsigned long long sk_bytes
        unsigned int bds_k


    uint32_t xmssmt_str_to_oid(uint32_t *oid, const char *s)
    int xmssmt_parse_oid(xmss_params *params, const uint32_t oid)


cdef extern from "xmss_core.h":

    int xmssmt_core_seed_keypair(const xmss_params *params,
                                unsigned char *pk, unsigned char *sk,
                                unsigned char *seed)

    int xmssmt_core_sign(const xmss_params *params,
                        unsigned char *sk,
                        unsigned char *sm, unsigned long long *smlen,
                        const unsigned char *m, unsigned long long mlen)

cdef extern from "xmss_commons.h":
    int xmssmt_core_sign_open(const xmss_params *params,
                          unsigned char *m, unsigned long long *mlen,
                          const unsigned char *sm, unsigned long long smlen,
                          const unsigned char *pk)
