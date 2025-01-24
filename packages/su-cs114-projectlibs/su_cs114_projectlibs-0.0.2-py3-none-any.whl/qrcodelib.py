""" The polynomial arithmetic for QR Code shall be calculated using bit-wise
modulo 2 arithmetic and bytewise modulo 100011101 arithmetic. This is a Galois
field of 2^8 with 100011101 representing the field's prime modulus polynomial
x8 + x4 + x3 + x2 +1.

The data codewords are the coefficients of the terms of a polynomial with the
coefficient of the highest term being the first data codeword and that of the
lowest power term being the last data codeword before the first error
correction codeword.

The error correction codewords are the remainder after dividing the data
codewords by a polynomial g(x) used for error correction codes.
The highest order coefficient of the remainder is the first error correction
codeword and the zero power coefficient is the last error correction codeword
and the last codeword in the block.
"""
INVALID_ERROR_CORRECTION_LEVEL = "Invalid data encoding pattern: {}"
INVALID_MASK_PATTERN = "Invalid error correction mask pattern: {}"
INVALID_DATA = "Invalid data to encode: {}"

# GF(256) log
GALIOS_LOG = [0] * 256

# GF(256) antilog
# Inverse of the logarithm table.  Maps integer logarithms to members of the field.
GALIOS_EXP = [0] * 512


class ErrorCorrectionException(Exception):
    def __init__(self, comment, obj=None):
        super().__init__(comment)
        self.obj = obj


class InformationBitsException(Exception):
    def __init__(self, comment, obj=None):
        super().__init__(comment)
        self.obj = obj


def _init_tables(prim=0x11d):    # 0x11d = 285 = 100011101
    """ Initialize the exponential and logarithm tables for GF(2^8).
    prime polynomial: 0x11d (285) / generator: 2
    """
    x = 1
    for i in range(255):
        GALIOS_EXP[i] = x
        GALIOS_LOG[x] = i
        x <<= 1
        if x & 0x100:
            x ^= prim
    for i in range(255, 512):
        GALIOS_EXP[i] = GALIOS_EXP[i - 255]


_init_tables()


def _gf_mul(x, y):
    """ Multiply two numbers in GF (2^8). """
    if x == 0 or y == 0:
        return 0
    return GALIOS_EXP[GALIOS_LOG[x] + GALIOS_LOG[y]]


def _gf_poly_mul(p, q):
    """ Multiply two polynomials in GF (2^8). """
    r = [0] * (len(p) + len(q) - 1)
    for j in range(len(q)):
        for i in range(len(p)):
            r[i + j] ^= _gf_mul(p[i], q[j])
    return r


def _gf_poly_add(p, q):
    """ Add two polynomials in GF (2^8). """
    r = [0] * max(len(p), len(q))
    for i in range(len(p)):
        r[i + len(r) - len(p)] = p[i]
    for i in range(len(q)):
        r[i + len(r) - len(q)] ^= q[i]
    return r


def _rs_generator_poly(num_err_words):
    """ Generate a generator polynomial for RS encoding . """
    g = [1]
    for i in range(num_err_words):
        g = _gf_poly_mul(g, [1, GALIOS_EXP[i]])
    return g


def get_error_codewords(message, num_err_words=16):
    """ Encode a list of integers using Reed - Solomon codes.
    
    Parameters:
    ----------
    message : list
         A list of integer representations of ASCII encodable decimal values.
    num_err_words : int
        The number of error correction codewords to generate.

    Returns:
    -------
    list
        A list of length 'num_err_words' containing the integer representations
        of the generated codewords generated for the 'message'.
    """
    for i in range(len(message)):
        m = message[i]
        if not isinstance(m, int) or m not in range(256):
            raise ErrorCorrectionException(INVALID_DATA.format(m))

    gen = _rs_generator_poly(num_err_words)
    encoded_message = [0] * (len(message) + num_err_words)
    encoded_message[:len(message)] = message

    for i in range(len(message)):
        coefficient = encoded_message[i]
        if coefficient != 0:
            for j in range(len(gen)):
                encoded_message[i + j] ^= _gf_mul(gen[j], coefficient)

    encoded_message[:len(message)] = message
    return encoded_message[len(message):]


error_correction_levels = {
    "low": [0, 1],          # 7%
    "medium": [0, 0],       # 14%
    "quartile": [1, 1],     # 25%
    "high": [1, 0]          # 30%
}



def _xor_bits(a, b):
    return [d ^ m for d, m in zip(a, b)]



def _bch_generator(data_bits):
    """
    The format information consists of a 15-bit sequence comprising 5 data bits and 10 BCH error correction bits.
    The Bose-Chaudhuri-Hocquenghem (15,5) code shall be used for error correction. The polynomial
    whose coefficient is the data bit string shall be divided by the generator polynomial
    G(x) = x^10 + x^8 + x^5 + x^4 + x^2 + x + 1.
    Source: https://franckybox.com/wp-content/uploads/qrcode.pdf"""
    # Generator polynomial coefficients for g( x) = x^10 + x^8 + x^5 + x^4 + x^2 + x + 1
    generator_poly = [1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1]
    # Append 10 zeros to the data_bits ( since the generator polynomial is of degree 10)
    data_bits_extended = data_bits + [0] * 10

    # Perform polynomial division ( modulo 2)
    for i in range(len(data_bits)):
        if data_bits_extended[i] == 1:     # Only if the bit is 1, we perform XOR with generator_poly
            for j in range(len(generator_poly)):
                data_bits_extended[i + j] ^= generator_poly[j]

    # The remainder is the parity bits
    parity_bits = data_bits_extended[-10:]

    # The final codeword is the concatenation of the original data_bits and the parity_bits
    return data_bits + parity_bits


def get_format_information_bits(qr_type, mask_pattern):
    """
    Gets the 15-bit information vector specifying which graphical output,
    the QR type (snake or real), and the masking pattern will be used for the
    QR code generation.

    Parameters:
    ----------
    qr_type : str
        A string of length 2 comprising 0s or 1s specifying which of the
        following encoding rules will be used:
        | qr_type |  Type  |  Output  |
        |  '00'   |  Snake | Terminal |
        |  '01'   |  Real  | Terminal |
        |  '10'   |  Snake | Graphical|
        |  '11'   |  Real  | Graphical|
    masking_patter : str
        A string of length 3 comprising 0s or 1s encoding the masking pattern.
        For example, '000' specifies that 0 == 1 masking pattern will be used.

    Returns:
    -------
    list
        A list of length 15 containing the bits used for the format information
        regions of the real QR code.

    """

    # "low": [0, 1],
    # "medium": [0, 0],
    # "quartile": [1, 1],
    # "high": [1, 0]
    if qr_type == '10': # GUI snake
        return _get_format_information_bits(mask_pattern, err_level="medium", qr_type="micro")
    elif qr_type == '01': # normal
        return _get_format_information_bits(mask_pattern, err_level="medium", qr_type="normal")
    elif qr_type == '00': # snake
        return _get_format_information_bits(mask_pattern, err_level="medium", qr_type="micro")
    elif qr_type == '11': # GUI normal
        return _get_format_information_bits(mask_pattern, err_level="medium", qr_type="normal")
    else:
        raise InformationBitsException(INVALID_ERROR_CORRECTION_LEVEL.format(qr_type))


def _get_format_information_bits(mask_pattern="111", err_level="medium", qr_type="normal"):
    if err_level not in error_correction_levels:
        raise ErrorCorrectionException(INVALID_ERROR_CORRECTION_LEVEL.format(err_level))
    data_bits = error_correction_levels[err_level].copy()

    if not mask_pattern or len(mask_pattern) != 3:
        raise ErrorCorrectionException(INVALID_MASK_PATTERN.format(mask_pattern))

    for i in mask_pattern:
        if i not in ['0', '1']:
            raise ErrorCorrectionException(INVALID_MASK_PATTERN.format(mask_pattern))

    data_bits.extend([int(i) for i in mask_pattern])
    codeword = _bch_generator(data_bits)
    mask_real = [1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0]
    mask_micro = [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1]
    if qr_type == "micro":
        return _xor_bits(codeword, mask_micro)
    else:
        return _xor_bits(codeword, mask_real)
