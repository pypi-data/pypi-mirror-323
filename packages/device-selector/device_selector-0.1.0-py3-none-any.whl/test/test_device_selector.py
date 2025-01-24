import pytest
import platform
import torch

from device_selector.device_selector import select_best_device, check_or_select_device

def test_select_best_device_cpu(monkeypatch):
    """
    If CUDA is not available and MPS is not available,
    select_best_device should return 'cpu'.
    We'll mock torch.cuda.is_available() to False and MPS to False.
    """
    monkeypatch.setattr(torch, "cuda", type("mock_cuda", (), {"is_available": lambda: False}))
    monkeypatch.setattr(torch.backends, "mps", type("mock_mps", (), {"is_available": lambda: False}))
    monkeypatch.setattr(platform, "system", lambda: "Darwin")  # We can even set to Darwin
    # but also mock MPS to be unavailable
    device = select_best_device()
    assert device == "cpu"

def test_select_best_device_cuda(monkeypatch):
    """
    If CUDA is available, select_best_device should return 'cuda'.
    """
    monkeypatch.setattr(torch, "cuda", type("mock_cuda", (), {"is_available": lambda: True}))
    # We don't care about MPS in this scenario, so let's just not override it
    device = select_best_device()
    assert device == "cuda"

def test_select_best_device_mps(monkeypatch):
    """
    If CUDA is not available but MPS is available on Darwin,
    select_best_device should return 'mps'.
    """
    monkeypatch.setattr(torch, "cuda", type("mock_cuda", (), {"is_available": lambda: False}))
    monkeypatch.setattr(torch.backends, "mps", type("mock_mps", (), {"is_available": lambda: True}))
    monkeypatch.setattr(platform, "system", lambda: "Darwin")
    device = select_best_device()
    assert device == "mps"

def test_check_or_select_device_no_arg(monkeypatch):
    """
    If no device is specified, it should auto-detect via select_best_device.
    Here, let's force it to CPU.
    """
    monkeypatch.setattr(torch, "cuda", type("mock_cuda", (), {"is_available": lambda: False}))
    monkeypatch.setattr(torch.backends, "mps", type("mock_mps", (), {"is_available": lambda: False}))
    monkeypatch.setattr(platform, "system", lambda: "Darwin")
    device = check_or_select_device()
    assert device == "cpu"

def test_check_or_select_device_cpu():
    """
    If user requests "cpu", we always return "cpu".
    """
    device = check_or_select_device("cpu")
    assert device == "cpu"

def test_check_or_select_device_cuda_available(monkeypatch):
    """
    If user requests 'cuda' and it's available, return 'cuda'.
    """
    monkeypatch.setattr(torch, "cuda", type("mock_cuda", (), {"is_available": lambda: True}))
    device = check_or_select_device("cuda")
    assert device == "cuda"

def test_check_or_select_device_cuda_unavailable(monkeypatch):
    """
    If user requests 'cuda' but it's unavailable, raise ValueError.
    """
    monkeypatch.setattr(torch, "cuda", type("mock_cuda", (), {"is_available": lambda: False}))
    with pytest.raises(ValueError, match="CUDA not available on this machine."):
        check_or_select_device("cuda")

def test_check_or_select_device_mps_available(monkeypatch):
    """
    If user requests 'mps' and it's available, return 'mps'.
    """
    monkeypatch.setattr(platform, "system", lambda: "Darwin")
    monkeypatch.setattr(torch.backends, "mps", type("mock_mps", (), {"is_available": lambda: True}))
    device = check_or_select_device("mps")
    assert device == "mps"

def test_check_or_select_device_mps_unavailable(monkeypatch):
    """
    If user requests 'mps' but it's unavailable, raise ValueError.
    """
    monkeypatch.setattr(platform, "system", lambda: "Darwin")
    monkeypatch.setattr(torch.backends, "mps", type("mock_mps", (), {"is_available": lambda: False}))
    with pytest.raises(ValueError, match="MPS not available on this machine."):
        check_or_select_device("mps")

def test_check_or_select_device_unknown():
    """
    If user requests something unknown, raise ValueError.
    """
    with pytest.raises(ValueError, match="Unknown or unsupported device requested"):
        check_or_select_device("foobar")

def test_check_or_select_device_cuda_custom(monkeypatch):
    """
    If user requests something like 'cuda:0' and CUDA is available,
    let it pass. If CUDA is unavailable, raise error.
    """
    monkeypatch.setattr(torch, "cuda", type("mock_cuda", (), {"is_available": lambda: True}))
    device = check_or_select_device("cuda:0")
    assert device == "cuda:0"

def test_check_or_select_device_cuda_custom_unavailable(monkeypatch):
    """
    If user requests 'cuda:0' but CUDA is not available, raise ValueError.
    """
    monkeypatch.setattr(torch, "cuda", type("mock_cuda", (), {"is_available": lambda: False}))
    with pytest.raises(ValueError, match="cuda:0 is unavailable because CUDA is not available."):
        check_or_select_device("cuda:0")
