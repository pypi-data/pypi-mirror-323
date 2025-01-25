from hcs_core.sglib.client_util import hdc_service_client

from hcs_cli.service.task import TaskModel

_client = hdc_service_client("scm")


def run(org_id: str, name: str) -> TaskModel:
    return _client.post(f"/v1/auto-infra/operators/{name}?org_id={org_id}", type=TaskModel)


def logs(org_id: str, name: str) -> list:
    return _client.get(f"/v1/auto-infra/operators/{name}/logs?org_id={org_id}")
