from ..common import cloudcli_server_request


def test_schema():
  res = cloudcli_server_request("/schema")
  assert len(res["schema_version"]) == 3
  assert len(res["commands"]) > 0
  assert len(res["schema_generated_at"]) > 10
