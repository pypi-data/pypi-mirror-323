# SU project libs for Python 3 for CS113/4

`su-cs114-projectlibs` is a support library for 2025 CS113/4 semester project conducted in computer science department at Stellenbosch University.

## Installation

This library requires a functioning Python 3 environment.

### With pip
For Python versions 3.8 - 3.10, due to compatability infeasibilities, the current safest option is to install most requirements manually before installing this package.

```bash
python3 -m pip --upgrade pip
python3 -m pip --upgrade wheel
python3 -m pip --upgrade setuptools
```

After the above commands execute sucessfully, install `su-cs114-projectlibs` simply with
```bash
python3 -m pip install --upgrade su-cs114-projectlibs
```

To test that you have installed the library correctly, run this command:
```bash
python3 -c 'from qrcodelib import get_format_information_bits; print(get_format_information_bits("00", "000"))'
```
This should print a list of integer of length 15.

## Contributors

- Marcel Dunaiski

## License

This project is licensed. See the [LICENSE](LICENSE) file for details.
