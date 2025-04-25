import importlib
import pkgutil
from typing import Dict, Type, Any
from pathlib import Path
from temporalio import activity

def _discover_activities() -> Dict[str, Type]:
    """activities 디렉토리에서 모든 activity 함수를 찾아서 등록합니다."""
    activity_registry = {}
    
    # 현재 디렉토리의 모든 Python 모듈을 찾습니다.
    package_path = Path(__file__).parent
    for module_info in pkgutil.iter_modules([str(package_path)]):
        # __init__.py는 건너뜁니다.
        if module_info.name == "__init__":
            continue
            
        try:
            # 모듈을 import합니다.
            module = importlib.import_module(f".{module_info.name}", package=__package__)
            
            # 모듈에서 @activity.defn 데코레이터가 붙은 모든 함수를 찾습니다.
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if hasattr(attr, "__wrapped__") and isinstance(attr.__wrapped__, activity.Activity):
                    # 함수 이름을 activity 이름으로 사용합니다.
                    activity_registry[attr_name] = attr
        except ImportError as e:
            print(f"Warning: {module_info.name} 모듈을 로드하는데 실패했습니다: {e}")
    
    return activity_registry

# activity registry를 동적으로 생성합니다.
activity_registry = _discover_activities()

def get_activity(activity_name: str) -> Any:
    """activity 이름으로 activity 함수를 가져옵니다."""
    if activity_name not in activity_registry:
        raise ValueError(f"Unknown activity: {activity_name}")
    return activity_registry[activity_name]

def get_all_activities() -> Dict[str, Type]:
    """등록된 모든 activity를 반환합니다."""
    return activity_registry
