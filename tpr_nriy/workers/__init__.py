import importlib
import pkgutil
from typing import Dict, Type
from pathlib import Path

def _discover_workers() -> Dict[str, Type]:
    """workers 디렉토리에서 모든 worker 함수를 찾아서 등록합니다."""
    worker_registry = {}
    
    # 현재 디렉토리의 모든 Python 모듈을 찾습니다.
    package_path = Path(__file__).parent
    for module_info in pkgutil.iter_modules([str(package_path)]):
        # __init__.py는 건너뜁니다.
        if module_info.name == "__init__":
            continue
            
        try:
            # 모듈을 import합니다.
            module = importlib.import_module(f".{module_info.name}", package=__package__)
            
            # 모듈에서 run_worker 함수를 찾습니다.
            if hasattr(module, "run_worker"):
                # 파일 이름에서 worker 이름을 추출합니다 (예: hello_worker.py -> hello)
                worker_name = module_info.name.replace("_worker", "")
                worker_registry[worker_name] = module.run_worker
        except ImportError as e:
            print(f"Warning: {module_info.name} 모듈을 로드하는데 실패했습니다: {e}")
    
    return worker_registry

# worker registry를 동적으로 생성합니다.
worker_registry = _discover_workers()

def get_worker(worker_name: str):
    """worker 이름으로 worker 함수를 가져옵니다."""
    if worker_name not in worker_registry:
        raise ValueError(f"Unknown worker: {worker_name}")
    return worker_registry[worker_name]
