# Topsis
A Python package for implementing the TOPSIS method for multi-criteria decision-making.
![PyPI version](https://img.shields.io/pypi/v/topsis)
![License](https://img.shields.io/pypi/l/topsis)
TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution) is a multi-criteria decision-making (MCDM) method. This package allows users to easily apply the TOPSIS method to datasets to rank alternatives based on multiple criteria.
## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)
## Installation

Install the package using pip:
```bash
pip install topsis

---

### **6. Usage**
Provide instructions on how to use the package, including code examples:
```markdown
## Usage

Import the package and use it in your Python scripts:
```python
from topsis import topsis

# Example usage
data = [[250, 16, 12, 5],
        [200, 16, 8, 3],
        [300, 32, 16, 4],
        [275, 32, 8, 4],
        [225, 16, 16, 2]]
weights = [0.25, 0.25, 0.25, 0.25]
impacts = ['+', '+', '-', '-']
rankings = topsis(data, weights, impacts)
print(rankings)

---

### **7. Examples**
Add real-world examples or use cases to help users understand how to apply the package:
```markdown
## Examples

Here’s how you can use the package to rank different laptops based on criteria like price, performance, and battery life.
## Contributing

Contributions are welcome! Please fork the repository and submit a pull request. For major changes, open an issue first to discuss what you would like to change.
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
## Contact

For questions or support, reach out at your.email@example.com.
