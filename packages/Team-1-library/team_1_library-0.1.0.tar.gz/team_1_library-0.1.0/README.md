Team_1_library

Python library with two classes: 
-Automatic preprocess, with advaced functions for missing values imputations using clustering and statistical techniques, as well as outlier corrections.
-Manual prerpocess, with manual column statistical imputations, numerical outlier correction, and string focused advanced functions, like normalization and correction.

Characteristics

- Missing value imputation with clustering (K-Means).
- Missing value imputation with statistical values (mean,median,mode).
- Outlier detection and correction to mean with Z-score technique.
- Empty column elimination with customizable threshold.
- Low variance column elimination with customizable threshold.

-String normalization (lowercase and gap elimination)
-String correction depending on the similarity

Usage:

The usage of this library functions are explained in the file 'USER_GUIDE.md'. An example of the use is included in the file 'example_usage.py'. We higly recommend to take a look in those files to understand the functioning of the library.

Instalation:

To install the library, navigate to the folder containing 'Team_1_library' in your preferred environment and install it using 'pip':
```bash
pip install ./path/to/the/library

Make sure you have the required dependencies installed:
```bash
pip install pandas scipy numpy scikit-learn fuzzywuzzy

 