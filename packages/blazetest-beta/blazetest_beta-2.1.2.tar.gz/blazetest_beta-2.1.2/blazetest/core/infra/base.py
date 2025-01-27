from blazetest.core.infra.tools import InfraSetupTool, AWSInfraSetup
from blazetest.core.utils.exceptions import UnsupportedInfraSetupTool


SUPPORTED_INFRA_SETUP_TOOLS = {
    "aws": AWSInfraSetup,
}


class InfraSetup:
    """
    Builder class which uses the given setup tool to deploy the infrastructure.

    Infrastructure setup class, used to deploy the artifacts to
    the cloud provider (currently, only AWS is supported)
    """

    def __init__(self, setup_tool: str = "aws", *args, **kwargs):
        if setup_tool not in SUPPORTED_INFRA_SETUP_TOOLS:
            raise UnsupportedInfraSetupTool(
                f"{setup_tool} is not supported for deploying, "
                f"supported: {','.join(list(SUPPORTED_INFRA_SETUP_TOOLS.keys()))}"
            )
        self.infra: InfraSetupTool = SUPPORTED_INFRA_SETUP_TOOLS[setup_tool](*args, **kwargs)

    def deploy(self):
        """
        Deploys the given infrastructure to the cloud provider using given setup tool
        """
        return self.infra.deploy()
