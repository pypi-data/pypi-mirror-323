# device-selector

A small Python library to automatically pick the best available PyTorch device.

- `select_best_device()`  
  Automatically returns one of:
  - `"cuda"` if an NVIDIA GPU is available via CUDA
  - `"mps"` if you're on Apple Silicon with Metal Performance Shaders available
  - `"cpu"` otherwise

- `check_or_select_device(requested_device: Optional[str])`
  - If `requested_device` is `None`, it behaves like `select_best_device()`.
  - Otherwise, checks if the requested device is actually available and raises an error if not.

## Installation

```bash
pip install https://github.com/darizae/device-selector/releases/download/v0.1.0/device_selector-0.1.0-py3-none-any.whl
