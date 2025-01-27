# SafeDict

SafeDict is a Python library providing a safe way to access nested dictionary keys with default handling for missing or `None` values.

## Installation

```bash
pip install safe-dict
```

## Usage
```python
from safe_dict import SafeDict

data = SafeDict({"a": {"b": 1}})
print(data["a"]["b"])  # Output: 1
print(data["a"]["c"])  # Output: {}
```


#### LICENSE
Thêm một license (ví dụ MIT). Bạn có thể lấy mẫu [MIT License](https://choosealicense.com/licenses/mit/).
