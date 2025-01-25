# xmssmt.pyx

from libc.stdint cimport uint32_t, uint8_t
from libc.stddef cimport size_t  # Import NULL from libc.stddef
from cpython.bytes cimport PyBytes_FromStringAndSize, PyBytes_AsString
from cpython.ref cimport Py_INCREF
from cpython.exc cimport PyErr_SetString
from cpython.mem cimport PyMem_Malloc, PyMem_Free
from libc.stdlib cimport malloc, free
from libc.string cimport memset

# Import the C declarations from the .pxd file
cimport xmssmt  # Imports from xmssmt.pxd

# Define a Python class to wrap the xmss_params struct
cdef class XmssParams:
    cdef xmssmt.xmss_params params  # cdef struct instance

    def __init__(self, uint32_t oid):
        cdef int result
        result = xmssmt.xmssmt_parse_oid(&self.params, oid)
        if result != 0:
            raise ValueError("Failed to initialize xmss_params with OID {}".format(oid))

    def get_n(self):
        return self.params.n

    def get_index_bytes(self):
        return self.params.index_bytes


    def get_height(self):
        return self.params.full_height


def str_to_oid(str s):
    """
    Converts XMSS parameter string to OID.

    Parameters:
        s (str): The XMSS parameter string.

    Returns:
        int: The corresponding OID value.

    Raises:
        ValueError: If the function fails to convert the string to an OID.
    """
    cdef bytes s_encoded = s.encode('utf-8')            # Keep the bytes object alive
    cdef const char* s_c = PyBytes_AsString(s_encoded)  # Safely get the C string
    cdef uint32_t oid                                   # Declare the oid variable
    cdef uint32_t result                                # Result from the C function

    # Call the C function, passing the address of oid
    result = xmssmt.xmssmt_str_to_oid(&oid, s_c)
    if result != 0:
        raise ValueError("Error converting string to OID")

    return oid


def core_seed_keypair(XmssParams params, seed):
    """
    Generates a keypair (pk, sk) using the provided seed and parameters.

    Parameters:
        params (XmssParams): The XMSS parameters.
        seed (bytes): The seed used to generate the keypair.

    Returns:
        tuple: (pk, sk), both as bytes.

    Raises:
        ValueError: If the function fails to generate the keypair.
    """
    cdef unsigned char* pk = NULL
    cdef unsigned char* sk = NULL
    cdef const unsigned char* seed_c
    cdef int result
    cdef size_t pk_bytes_size = params.params.pk_bytes 
    cdef size_t sk_bytes_size = params.params.sk_bytes
    cdef size_t n = params.params.n  # Seed length is n bytes

    if len(seed) != n * 3:
        raise ValueError("Seed length must be {} bytes".format(n*3))

    # Keep a reference to the seed bytes
    cdef bytes seed_bytes = seed
    seed_c = <const unsigned char *>PyBytes_AsString(seed_bytes)
    #print(f'=> seed: {seed_c}')

    # Allocate memory for pk and sk
    pk = <unsigned char*> malloc(pk_bytes_size)
    sk = <unsigned char*> malloc(sk_bytes_size)

    if pk == NULL or sk == NULL:
        if pk != NULL:
            free(pk)
        if sk != NULL:
            free(sk)
        raise MemoryError("Failed to allocate memory for keypair")

    # Initialize pk and sk memory to zero (optional)
    memset(pk, 0, pk_bytes_size)
    memset(sk, 0, sk_bytes_size)

    # Call the C function
    #print(f'=> params: {params.params}')
    #print(f'=> seed: {seed_c}')
    result = xmssmt.xmssmt_core_seed_keypair(&params.params, pk, sk, <unsigned char*> seed_c)
    #print(f'=> result: {result}')
    if result != 0:
        free(pk)
        free(sk)
        raise ValueError("Error generating keypair")

    # Convert pk and sk to Python bytes
    #print(f'=> pk (w1): {pk}')

    pk_bytes = PyBytes_FromStringAndSize(<char*> pk, pk_bytes_size)
    sk_bytes = PyBytes_FromStringAndSize(<char*> sk, sk_bytes_size)

    # Free allocated memory
    free(pk)
    free(sk)

    #print(f'=> pk (w2): {pk_bytes}')

    return pk_bytes, sk_bytes


def core_sign(XmssParams params, sk, message):
    """
    Generates a signature for the given message using the secret key.

    Parameters:
        params (XmssParams): The XMSS parameters.
        sk (bytes): The secret key.
        message (bytes): The message to sign.

    Returns:
        bytes: The signature.

    Raises:
        ValueError: If the function fails to generate the signature.
    """
    cdef unsigned char* sk_c
    cdef const unsigned char* message_c
    cdef unsigned char* signature
    cdef unsigned long long signature_len
    cdef unsigned long long message_len = len(message)
    cdef int result


    # Compute maximum signature length
    cdef size_t max_signature_len = params.params.sig_bytes + len(message)

    # Check the length of sk
    if len(sk) != params.params.sk_bytes:
        raise ValueError("Secret key length must be {} bytes".format(params.params.sk_bytes))

    # Keep references to sk and message bytes
    cdef bytes sk_bytes = sk
    sk_c = <unsigned char *>PyBytes_AsString(sk_bytes)

    cdef bytes message_bytes = message
    message_c = <const unsigned char *>PyBytes_AsString(message_bytes)

    # Allocate memory for signature
    signature = <unsigned char*> malloc(max_signature_len)

    if signature == NULL:
        raise MemoryError("Failed to allocate memory for signature")

    # Call the C function
    result = xmssmt.xmssmt_core_sign(&params.params, sk_c, signature, &signature_len, message_c, message_len)

    if result != 0:
        free(signature)
        raise ValueError("Error generating signature")

    # Convert signature to Python bytes
    signature_bytes = PyBytes_FromStringAndSize(<char*> signature, signature_len)

    # Free allocated memory
    free(signature)

    return signature_bytes


def core_sign_open(XmssParams params, pk, signature):
    """
    Verifies a signature and extracts the original message.

    Parameters:
        params (XmssParams): The XMSS parameters.
        pk (bytes): The public key.
        signature (bytes): The signature.

    Returns:
        bytes: The original message if the signature is valid.

    Raises:
        ValueError: If the signature is invalid or verification fails.
    """
    cdef const unsigned char* pk_c
    cdef const unsigned char* signature_c
    cdef unsigned char* message
    cdef unsigned long long message_len
    cdef unsigned long long signature_len = len(signature)
    cdef int result

    # Check the length of pk
    if len(pk) != params.params.pk_bytes:
        raise ValueError("Public key length must be {} bytes".format(params.params.pk_bytes))

    # Keep references to pk and signature bytes
    cdef bytes pk_bytes = pk
    pk_c = <const unsigned char *>PyBytes_AsString(pk_bytes)

    cdef bytes signature_bytes = signature
    signature_c = <const unsigned char *>PyBytes_AsString(signature_bytes)

    # Allocate memory for message (maximum possible size: signature length)
    message = <unsigned char*> malloc(signature_len)

    if message == NULL:
        raise MemoryError("Failed to allocate memory for message")

    # Call the C function
    result = xmssmt.xmssmt_core_sign_open(&params.params, message, &message_len, signature_c, signature_len, pk_c)
    print(f'-> verification result: {result}')
    if result != 0:
        free(message)
        raise ValueError("Invalid signature or verification failed")

    # Convert message to Python bytes
    message_bytes = PyBytes_FromStringAndSize(<char*> message, message_len)

    # Free allocated memory
    free(message)

    return message_bytes