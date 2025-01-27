import dataclasses
from typing import List, Dict, Optional

from blazetest.core.project_config.validators import (
    ValidationBase,
    ecr_repository_name_is_valid,
    resource_prefix_is_valid,
    s3_bucket_name_is_valid,
    lambda_function_memory_size_is_valid,
    lambda_function_timeout_is_valid,
    junit_results_file_link_is_valid,
    tests_per_dispatch_is_valid,
    selected_framework_is_supported,
)


@dataclasses.dataclass
class LicenceConfig(ValidationBase):
    license_key: Optional[str] = None
    license_file: Optional[str] = None


@dataclasses.dataclass
class FlakeDetectionConfig(ValidationBase):
    failure_retry_attempts: int = 0
    fail_on_flake: bool = True
    remove_flakes: bool = False
    exit_on_flake_detection: bool = True


@dataclasses.dataclass
class PurgeConfig(ValidationBase):
    purge_time_limit: int = 168  # hours
    purge_exclude_tags: List[str] = dataclasses.field(default_factory=lambda: [])  # tags that will be excluded


@dataclasses.dataclass
class GeneralConfig(ValidationBase):
    tests_per_dispatch: int = 1
    junit_results_file_link: str = "private"
    artifacts_dir: str = ""

    project_name: Optional[str] = None
    runtime: str = "python"
    java_version: str = "17"
    build_tool: str = "mvn"  # Applicable for Java runtimes

    license: LicenceConfig = dataclasses.field(default_factory=lambda: LicenceConfig())
    flaky: FlakeDetectionConfig = dataclasses.field(default_factory=lambda: FlakeDetectionConfig())
    purge: PurgeConfig = dataclasses.field(default_factory=lambda: PurgeConfig())

    def get_validators(self) -> Dict:
        return {
            "tests_per_dispatch": tests_per_dispatch_is_valid,
            "junit_results_file_link": junit_results_file_link_is_valid,
        }


@dataclasses.dataclass
class AWSConfig(ValidationBase):
    region: str
    resource_prefix: str = "blazetest-stack"
    s3_bucket_prefix: str = "blazetest-s3"
    ecr_repository_prefix: str = "blazetest-repo"

    lambda_function_memory_size: int = 4096  # MB
    lambda_function_timeout: int = 900  # seconds
    lambda_ephemeral_storage_size: int = 2048  # MB

    tags: dict = dataclasses.field(default_factory=lambda: {})

    def get_resource_name(self, uuid: str):
        return f"{self.resource_prefix}-{uuid}"

    def get_ecr_repository_prefix(self, uuid: str):
        return f"{self.ecr_repository_prefix}-{uuid}"

    def get_validators(self) -> Dict:
        return {
            "ecr_repository_prefix": ecr_repository_name_is_valid,
            "resource_prefix": resource_prefix_is_valid,
            "s3_bucket_prefix": s3_bucket_name_is_valid,
            "lambda_function_memory_size": lambda_function_memory_size_is_valid,
            "lambda_function_timeout": lambda_function_timeout_is_valid,
        }


@dataclasses.dataclass
class AzureConfig(ValidationBase):
    ...


@dataclasses.dataclass
class GCPConfig(ValidationBase):
    ...


@dataclasses.dataclass
class CloudConfig(ValidationBase):
    aws: AWSConfig
    azure: AzureConfig = dataclasses.field(default_factory=lambda: AzureConfig())
    gcp: GCPConfig = dataclasses.field(default_factory=lambda: GCPConfig())


@dataclasses.dataclass
class ChromeConfig(ValidationBase):
    version: str = "latest"


@dataclasses.dataclass
class FirefoxConfig(ValidationBase):
    version: str = "latest"


@dataclasses.dataclass
class EdgeConfig(ValidationBase):
    version: str = "latest"


@dataclasses.dataclass
class BrowserConfig(ValidationBase):
    """
    The list of supported browsers within blazetest docker image can be found at https://blazetest.io/browsers
    """

    firefox: FirefoxConfig = dataclasses.field(default_factory=lambda: FirefoxConfig())
    edge: EdgeConfig = dataclasses.field(default_factory=lambda: EdgeConfig())
    chrome: ChromeConfig = dataclasses.field(default_factory=lambda: ChromeConfig())


@dataclasses.dataclass
class PytestConfig(ValidationBase):
    collection_args: List[str] = dataclasses.field(default_factory=lambda: [])
    execution_args: List[str] = dataclasses.field(default_factory=lambda: [])


@dataclasses.dataclass
class JUnitConfig(ValidationBase):
    discovery_selectors: List[str] = dataclasses.field(default_factory=lambda: [])
    config_params: List[str] = dataclasses.field(default_factory=lambda: [])


@dataclasses.dataclass
class TestNGConfig(ValidationBase):
    params: List[str] = dataclasses.field(default_factory=lambda: [])


@dataclasses.dataclass
class FrameworkConfig(ValidationBase):
    selected: str = "pytest"

    pytest: PytestConfig = dataclasses.field(default_factory=lambda: PytestConfig())
    junit: JUnitConfig = dataclasses.field(default_factory=lambda: JUnitConfig())
    testng: TestNGConfig = dataclasses.field(default_factory=lambda: TestNGConfig())

    def get_validators(self) -> Dict:
        return {
            "selected": selected_framework_is_supported,
        }


@dataclasses.dataclass
class BuildConfig(ValidationBase):
    backend: str = "docker"


@dataclasses.dataclass
class BlazetestConfig(ValidationBase):
    general: GeneralConfig
    cloud: CloudConfig
    framework: FrameworkConfig = dataclasses.field(default_factory=lambda: FrameworkConfig())
    build: BuildConfig = dataclasses.field(default_factory=lambda: BuildConfig())
    browser: BrowserConfig = dataclasses.field(default_factory=lambda: BrowserConfig())
