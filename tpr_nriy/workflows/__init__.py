import importlib
import pkgutil
from typing import Dict, Type, Any
from pathlib import Path
from temporalio import workflow

def _discover_workflows() -> Dict[str, Type]:
    """workflows 디렉토리에서 모든 workflow 클래스를 찾아서 등록합니다."""
    workflow_registry = {}
    
    # 현재 디렉토리의 모든 Python 모듈을 찾습니다.
    package_path = Path(__file__).parent
    for module_info in pkgutil.iter_modules([str(package_path)]):
        # __init__.py는 건너뜁니다.
        if module_info.name == "__init__":
            continue
            
        try:
            # 모듈을 import합니다.
            module = importlib.import_module(f".{module_info.name}", package=__package__)
            
            # 모듈에서 @workflow.defn 데코레이터가 붙은 모든 클래스를 찾습니다.
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and hasattr(attr, "__temporal_workflow_definition__"):
                    # 클래스 이름을 workflow 이름으로 사용합니다.
                    workflow_name = attr_name.lower()
                    workflow_registry[workflow_name] = attr
        except ImportError as e:
            print(f"Warning: {module_info.name} 모듈을 로드하는데 실패했습니다: {e}")
    
    return workflow_registry

# workflow registry를 동적으로 생성합니다.
workflow_registry = _discover_workflows()

def get_workflow(workflow_name: str) -> Any:
    """workflow 이름으로 workflow 클래스를 가져옵니다."""
    if workflow_name not in workflow_registry:
        raise ValueError(f"Unknown workflow: {workflow_name}")
    return workflow_registry[workflow_name]

def get_all_workflows() -> Dict[str, Type]:
    """등록된 모든 workflow를 반환합니다."""
    return workflow_registry
