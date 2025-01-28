# Copyright 2024 Max Planck Institute for Software Systems, and
# National University of Singapore
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import aiohttp
import datetime
import typing
import contextlib
import json
from simbricks.utils import base as utils_base
from .auth import Token, TokenProvider
from .settings import client_settings
from simbricks.orchestration import system
from simbricks.orchestration import simulation
from simbricks.orchestration import instantiation


class BaseClient:
    def __init__(self, base_url=client_settings().base_url):
        self._base_url = base_url
        self._token_provider = TokenProvider()

    async def _get_headers(self, overwrite_headers: dict[str, typing.Any] | None = None) -> dict:
        headers = {}
        token = await self._token_provider.access_token()
        headers["Authorization"] = f"Bearer {token}"

        if overwrite_headers:
            headers.update(overwrite_headers)
            headers = {k: v for k, v in headers.items() if v is not None}

        return headers

    def build_url(self, url: str) -> str:
        return f"{self._base_url}{url}"

    @contextlib.asynccontextmanager
    async def session(
        self, overwrite_headers: dict[str, typing.Any] | None = None
    ) -> typing.AsyncIterator[aiohttp.ClientSession]:
        headers = await self._get_headers(overwrite_headers=overwrite_headers)
        timeout = aiohttp.ClientTimeout(total=client_settings().timeout_sec)
        session = aiohttp.ClientSession(headers=headers, timeout=timeout)
        try:
            yield session
        finally:
            await session.close()

    @contextlib.asynccontextmanager
    async def request(
        self, meth: str, url: str, data: typing.Any = None, retry: bool = True, **kwargs: typing.Any
    ) -> typing.AsyncIterator[aiohttp.ClientResponse]:
        async with self.session() as session:
            async with session.request(
                method=meth, url=self.build_url(url), data=data, **kwargs
            ) as resp:  # TODO: handel connection error
                if resp.status == 401 and "WWW-Authenticate" in resp.headers and retry:
                    wwa = resp.headers["WWW-Authenticate"]
                    parts = wwa.split(",")
                    ticket = None
                    for p in parts:
                        p = p.strip()
                        if p.startswith('ticket="'):
                            ticket = p[8:-1]

                    if ticket:
                        await self._token_provider.resource_token(ticket)
                        async with self.request(meth, url, data, False, **kwargs) as resp:
                            yield resp
                elif resp.status in [400, 402]:
                    msg = await resp.json()
                    raise Exception(f"Error sending request: {msg}")
                else:
                    resp.raise_for_status()  # TODO: handel gracefully
                    yield resp

    @contextlib.asynccontextmanager
    async def get(
        self,
        url: str,
        data: typing.Any = None,
        **kwargs: typing.Any,
    ) -> typing.AsyncIterator[aiohttp.ClientResponse]:
        async with self.request(meth=aiohttp.hdrs.METH_GET, url=url, data=data, **kwargs) as resp:
            yield resp

    @contextlib.asynccontextmanager
    async def post(
        self,
        url: str,
        data: typing.Any = None,
        **kwargs: typing.Any,
    ) -> typing.AsyncIterator[aiohttp.ClientResponse]:
        async with self.request(meth=aiohttp.hdrs.METH_POST, url=url, data=data, **kwargs) as resp:
            yield resp

    @contextlib.asynccontextmanager
    async def put(
        self,
        url: str,
        data: typing.Any = None,
        **kwargs: typing.Any,
    ) -> typing.AsyncIterator[aiohttp.ClientResponse]:
        async with self.request(meth=aiohttp.hdrs.METH_PUT, url=url, data=data, **kwargs) as resp:
            yield resp

    @contextlib.asynccontextmanager
    async def patch(
        self, url: str, data: typing.Any = None, **kwargs: typing.Any
    ) -> typing.AsyncIterator[aiohttp.ClientResponse]:
        async with self.request(meth=aiohttp.hdrs.METH_PATCH, url=url, data=data, **kwargs) as resp:
            yield resp

    @contextlib.asynccontextmanager
    async def delete(self, url: str, **kwargs: typing.Any) -> typing.AsyncIterator[aiohttp.ClientResponse]:
        async with self.request(meth=aiohttp.hdrs.METH_DELETE, url=url, **kwargs) as resp:
            yield resp

    async def info(self):
        async with self.get(url="/info") as resp:
            return await resp.json()


class AdminClient:

    def __init__(self, base_client: BaseClient = BaseClient()):
        self._base_client = base_client

    def _prefix(self, url: str) -> str:
        return f"/admin{url}"

    async def get_ns(self, ns_id: int):
        async with self._base_client.get(url=self._prefix(f"/{ns_id}")) as resp:
            return await resp.json()

    async def get_all_ns(self):
        async with self._base_client.get(url=self._prefix("/")) as resp:
            return await resp.json()

    async def create_ns(self, parent_id: int | None, name: str):
        namespace_json = {"name": name}
        if parent_id:
            namespace_json["parent_id"] = parent_id
        async with self._base_client.post(url=self._prefix("/"), json=namespace_json) as resp:
            return await resp.json()

    async def delete(self, ns_id: int):
        async with self._base_client.delete(url=self._prefix(f"/{ns_id}")) as resp:
            return await resp.json()


class OrgClient:

    def __init__(self, base_client: BaseClient = BaseClient()):
        self._base_client = base_client

    def _prefix(self, org: str, url: str) -> str:
        return f"/org/{org}{url}"

    async def get_members(self, org: str):
        async with self._base_client.get(url=self._prefix(org, f"/members")) as resp:
            return await resp.json()

    async def invite_member(self, org: str, email: str, first_name: str, last_name: str):
        namespace_json = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        }
        async with self._base_client.post(url=self._prefix(org, "/invite-member"),
                json=namespace_json) as resp:
            await resp.json()

    async def create_guest(self, org: str, email: str, first_name: str, last_name: str):
        namespace_json = {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
        }
        async with self._base_client.post(url=self._prefix(org, "/create-guest"),
                json=namespace_json) as resp:
            await resp.json()

    async def guest_token(self, org: str, email: str) -> Token:
        j = {
            "email": email,
        }
        async with self._base_client.post(url=self._prefix(org, "/guest-token"), json=j) as resp:
            tok = await resp.json()
            return Token.parse_from_resp(tok)

    async def guest_magic_link(self, org: str, email: str) -> str:
        j = {
            "email": email,
        }
        async with self._base_client.post(url=self._prefix(org, "/guest-magic-link"), json=j) as resp:
            return (await resp.json())['magic_link']

class NSClient:
    def __init__(self, base_client: BaseClient = BaseClient(), namespace: str = ""):
        self._base_client: BaseClient = base_client
        self._namespace = namespace

    def _build_ns_prefix(self, url: str) -> str:
        return f"/ns/{self._namespace}/-{url}"

    @contextlib.asynccontextmanager
    async def post(
        self, url: str, data: typing.Any = None, **kwargs: typing.Any
    ) -> typing.AsyncIterator[aiohttp.ClientResponse]:
        async with self._base_client.post(url=self._build_ns_prefix(url=url), data=data, **kwargs) as resp:
            yield resp

    @contextlib.asynccontextmanager
    async def put(
        self,
        url: str,
        data: typing.Any = None,
        **kwargs: typing.Any,
    ) -> typing.AsyncIterator[aiohttp.ClientResponse]:
        async with self._base_client.put(url=self._build_ns_prefix(url=url), data=data, **kwargs) as resp:
            yield resp

    @contextlib.asynccontextmanager
    async def patch(
        self, url: str, data: typing.Any = None, **kwargs: typing.Any
    ) -> typing.AsyncIterator[aiohttp.ClientResponse]:
        async with self._base_client.patch(url=self._build_ns_prefix(url=url), data=data, **kwargs) as resp:
            yield resp

    @contextlib.asynccontextmanager
    async def get(
        self, url: str, data: typing.Any = None, **kwargs: typing.Any
    ) -> typing.AsyncIterator[aiohttp.ClientResponse]:

        async with self._base_client.get(url=self._build_ns_prefix(url=url), data=data, **kwargs) as resp:
            yield resp

    @contextlib.asynccontextmanager
    async def delete(self, url: str, **kwargs: typing.Any) -> typing.AsyncIterator[aiohttp.ClientResponse]:
        async with self._base_client.delete(url=self._build_ns_prefix(url=url), **kwargs) as resp:
            yield resp

    async def info(self):
        async with self.get(url="/info") as resp:
            return await resp.json()

    async def create(self, parent_id: int, name: str):
        namespace_json = {"parent_id": parent_id, "name": name}
        async with self.post(url="/", json=namespace_json) as resp:
            return await resp.json()

    async def delete_ns(self, ns_id: int):
        async with self.delete(url=self._build_ns_prefix(f"/{ns_id}")) as _:
            return

    # retrieve namespace ns_id, useful for retrieving a child the current namespace
    async def get_ns(self, ns_id: int):
        async with self.get(url=f"/one/{ns_id}") as resp:
            return await resp.json()

    # retrieve the current namespace
    async def get_cur(self):
        async with self.get(url="/") as resp:
            return await resp.json()

    # recursively retrieve all namespaces beginning with the current including all children
    async def get_all(self):
        async with self.get(url="/all") as resp:
            return await resp.json()

    async def get_members(self) -> dict[str, list[dict]]:
        async with self.get(url="/members") as resp:
            return await resp.json()

    async def get_role_members(self, role: str) -> list[dict]:
        async with self.get(url=f"/members/{role}") as resp:
            return await resp.json()

    async def add_member(self, role: str, username: str) -> None:
        req_json = {"username": username}
        async with self.post(url=f"/members/{role}", json=req_json) as resp:
            await resp.json()


class SimBricksClient:

    def __init__(self, ns_client: NSClient = NSClient()) -> None:
        self._ns_client: NSClient = ns_client

    async def info(self):
        async with self._ns_client.get("/systems/info") as resp:
            return await resp.json()

    async def create_system(self, system: system.System) -> dict:
        sys_json = json.dumps(system.toJSON())
        json_obj = {"sb_json": sys_json}
        async with self._ns_client.post(url="/systems", json=json_obj) as resp:
            return await resp.json()

    async def delete_system(self, sys_id: int):
        async with self._ns_client.delete(url=f"/systems/{sys_id}") as resp:
            return await resp.json()

    async def get_systems(self) -> list[dict]:
        async with self._ns_client.get(url="/systems") as resp:
            return await resp.json()

    async def get_system(self, system_id: int) -> dict:
        async with self._ns_client.get(url=f"/systems/{system_id}") as resp:
            return await resp.json()

    async def create_simulation(self, system_db_id: int, simulation: simulation.Simulation) -> simulation.Simulation:
        sim_js = json.dumps(simulation.toJSON())
        json_obj = {"system_id": system_db_id, "sb_json": sim_js}
        async with self._ns_client.post(url="/simulations", json=json_obj) as resp:
            return await resp.json()

    async def delete_simulation(self, sim_id: int):
        async with self._ns_client.delete(url=f"/simulations/{sim_id}") as resp:
            return await resp.json()

    async def get_simulation(self, simulation_id: int) -> dict:
        async with self._ns_client.get(url=f"/simulations/{simulation_id}") as resp:
            return await resp.json()

    async def get_simulations(self) -> list[dict]:
        async with self._ns_client.get(url="/simulations") as resp:
            return await resp.json()

    async def create_instantiation(self, sim_db_id: int, instantiation: instantiation.Instantiation) -> dict:
        inst_json = json.dumps(instantiation.toJSON())
        json_obj = {"simulation_id": sim_db_id, "sb_json": inst_json}
        async with self._ns_client.post(url="/instantiations", json=json_obj) as resp:
            return await resp.json()

    async def delete_instantiation(self, inst_id: int):
        async with self._ns_client.delete(url=f"/instantiations/{inst_id}") as resp:
            return await resp.json()

    async def get_instantiation(self, instantiation_id: int) -> dict:
        async with self._ns_client.get(url=f"/instantiations/{instantiation_id}") as resp:
            return await resp.json()

    async def get_instantiations(self) -> list[dict]:
        async with self._ns_client.get(url="/instantiations") as resp:
            return await resp.json()

    async def create_run(self, inst_db_id: int) -> dict:
        json_obj = {
            "instantiation_id": inst_db_id,
            "state": "pending",
            "output": "",
        }
        async with self._ns_client.post(url="/runs", json=json_obj) as resp:
            return await resp.json()

    async def delete_run(self, rid: int):
        async with self._ns_client.delete(url=f"/runs/{rid}") as resp:
            return await resp.json()

    async def update_run(self, rid: int, updates: dict[str, typing.Any] = {"state": "pending"}) -> dict:
        async with self._ns_client.patch(url=f"/runs/{rid}", json=updates) as resp:
            return await resp.json()

    async def get_run(self, run_id: int) -> dict:
        async with self._ns_client.get(url=f"/runs/{run_id}") as resp:
            return await resp.json()

    async def get_runs(self) -> list[dict]:
        async with self._ns_client.get(url=f"/runs") as resp:
            return await resp.json()

    async def set_run_input(self, rid: int, uploaded_input_file: str):
        with open(uploaded_input_file, "rb") as f:
            file_data = {"file": f}
            async with self._ns_client.put(url=f"/runs/input/{rid}", data=file_data) as resp:
                return await resp.json()

    async def get_run_input(self, rid: int, store_path: str):
        async with self._ns_client.post(url=f"/runs/input/{rid}") as resp:
            content = await resp.read()
            with open(store_path, "wb") as f:
                f.write(content)

    async def set_run_artifact(self, rid: int, uploaded_output_file: str):
        with open(uploaded_output_file, "rb") as f:
            file_data = {"file": f}
            async with self._ns_client.put(url=f"/runs/output/{rid}", data=file_data) as resp:
                return await resp.json()

    async def get_run_artifact(self, rid: int, store_path: str):
        async with self._ns_client.post(url=f"/runs/output/{rid}") as resp:
            content = await resp.read()
            with open(store_path, "wb") as f:
                f.write(content)

    async def get_run_console(
        self, rid: int, simulators_seen_until: dict[int, datetime.datetime] = {}
    ) -> list[dict]:
        simulators = {}
        for simulator_id, until in simulators_seen_until.items():
            simulators[simulator_id] = until.isoformat()
        obj = {"simulators": simulators}
        async with self._ns_client.get(url=f"/runs/{rid}/console", json=obj) as resp:
            return await resp.json()


class ResourceGroupClient:

    def __init__(self, ns_client) -> None:
        self._ns_client: NSClient = ns_client

    async def create_rg(self, label: str, available_cores: int, available_memory: int) -> dict:
        obj = {"label": label, "available_cores": available_cores, "available_memory": available_memory}
        async with self._ns_client.post(url="/resource_group", json=obj) as resp:
            return await resp.json()

    async def update_rg(
        self,
        rg_id: int,
        label: str | None = None,
        available_cores: int | None = None,
        available_memory: int | None = None,
        cores_left: int | None = None,
        memory_left: int | None = None,
    ) -> dict:
        obj = {
            "id": rg_id,
            "label": label,
            "available_cores": available_cores,
            "available_memory": available_memory,
            "cores_left": cores_left,
            "memory_left": memory_left,
        }
        obj = utils_base.filter_None_dict(to_filter=obj)
        async with self._ns_client.put(url=f"/resource_group/{rg_id}", json=obj) as resp:
            return await resp.json()

    async def get_rg(self, rg_id: int) -> dict:
        async with self._ns_client.get(url=f"/resource_group/{rg_id}") as resp:
            return await resp.json()

    async def filter_get_rg(self) -> dict:  # TODO: add filtering object...
        async with self._ns_client.get(url=f"/resource_group") as resp:
            return await resp.json()


class RunnerClient:

    def __init__(self, ns_client, id: int) -> None:
        self._ns_client: NSClient = ns_client
        self._runner_id = id

    def _build_prefix(self, url: str) -> str:
        return f"/runners/{self._runner_id}{url}"

    @contextlib.asynccontextmanager
    async def post(
        self, url: str, data: typing.Any = None, **kwargs: typing.Any
    ) -> typing.AsyncIterator[aiohttp.ClientResponse]:
        async with self._ns_client.post(url=self._build_prefix(url=url), data=data, **kwargs) as resp:
            yield resp

    @contextlib.asynccontextmanager
    async def delete(
        self, url: str, data: typing.Any = None, **kwargs: typing.Any
    ) -> typing.AsyncIterator[aiohttp.ClientResponse]:
        async with self._ns_client.delete(url=self._build_prefix(url=url), data=data, **kwargs) as resp:
            yield resp

    @contextlib.asynccontextmanager
    async def put(
        self, url: str, data: typing.Any = None, **kwargs: typing.Any
    ) -> typing.AsyncIterator[aiohttp.ClientResponse]:
        async with self._ns_client.put(url=self._build_prefix(url=url), data=data, **kwargs) as resp:
            yield resp

    @contextlib.asynccontextmanager
    async def get(
        self, url: str, data: typing.Any = None, **kwargs: typing.Any
    ) -> typing.AsyncIterator[aiohttp.ClientResponse]:

        async with self._ns_client.get(url=self._build_prefix(url=url), data=data, **kwargs) as resp:
            yield resp

    async def create_runner(self, resource_group_id: int, label: str, tags: list[str]) -> dict:
        tags_obj = list(map(lambda t: {"label": t}, tags))
        obj = {"resource_group_id": resource_group_id, "label": label, "tags": tags_obj}
        async with self._ns_client.post(url=f"/runners", json=obj) as resp:
            return await resp.json()

    async def create_runner_event(self, action: str, run_id: int | None) -> dict:
        obj = {"runner_id": self._runner_id, "action": action, "run_id": run_id}
        async with self.post(url=f"/events", json=obj) as resp:
            return await resp.json()

    async def delete_runner_event(self, event_id: int) -> None:
        async with self.delete(url=f"/events/{event_id}") as resp:
            await resp.json()

    async def update_runner_event(
        self, event_id: int, action: str | None, run_id: int | None, event_status: str | None
    ) -> dict:
        obj = {
            "id": event_id,
            "runner_id": self._runner_id,
            "action": action,
            "run_id": run_id,
            "event_status": event_status,
        }
        obj = utils_base.filter_None_dict(to_filter=obj)
        async with self.put(url=f"/events", json=obj) as resp:
            return await resp.json()

    async def get_events(
        self, action: str | None, run_id: int | None, limit: int | None, event_status: str | None
    ) -> dict:
        params = {"action": action, "run_id": run_id, "event_status": event_status, "limit": limit}
        params = utils_base.filter_None_dict(to_filter=params)
        async with self.get(url=f"/events", params=params) as resp:
            return await resp.json()

    async def update_runner(self, updates: dict[str, typing.Any]) -> dict:
        async with self.post(url="", json=updates) as resp:
            return await resp.json()

    async def delete_runner(self) -> dict:
        async with self.delete(url="") as resp:
            return await resp.json()

    async def get_runner(self) -> dict:
        async with self.get(url=f"") as resp:
            return await resp.json()

    async def list_runners(self) -> dict:
        async with self._ns_client.get(url=f"/runners") as resp:
            return await resp.json()

    async def send_heartbeat(self) -> None:
        async with self.put(url="/heartbeat") as resp:
            await resp.json()

    async def filter_get_runs(
        self,
        run_id: int | None = None,
        instantiation_id: int | None = None,
        state: str | None = None,
        limit: int | None = None,
    ):
        obj = {
            "id": run_id,
            "instantiation_id": instantiation_id,
            "state": state,
            "limit": limit,
        }
        utils_base.filter_None_dict(to_filter=obj)
        async with self.post(url="/filter_get_run", json=obj) as resp:
            return await resp.json()

    async def next_run(self) -> dict | None:
        async with self.get(f"/next_run") as resp:
            if resp.status == 200:
                return await resp.json()
            elif resp.status == 202:
                return None
            else:
                resp.raise_for_status()

    async def update_run(
        self,
        run_id: int,
        state: str,
        output: str,
    ) -> None:
        obj = {
            "state": state,
            "output": output,
            "id": run_id,
            "instantiation_id": None, # TODO: FIXME
        }
        obj = utils_base.filter_None_dict(to_filter=obj)
        async with self.put(url=f"/update_run/{run_id}", json=obj) as resp:
            await resp.json()

    async def update_state_simulator(
        self, run_id: int, sim_id: int, sim_name: str, state: str, cmd: str
    ) -> None:
        obj = {
            "run_id": run_id,
            "simulator_id": sim_id,
            "simulator_name": sim_name,
            "state": state,
            "command": cmd,
        }
        async with self.post(url=f"/run/{run_id}/simulator/{sim_id}/state", json=obj) as resp:
            await resp.json()

    async def update_proxy(self, run_id: int, proxy_id: int, state: str, cmd: str) -> None:
        obj = {"run_id": run_id, "proxy_id": proxy_id, "state": state, "cmd": cmd}
        async with self.put(url=f"/{run_id}/proxy/{proxy_id}/state", json=obj) as resp:
            await resp.json()

    async def send_out_simulation(
        self,
        run_id: int,
        cmd: int,
        is_stderr: bool,
        output: list[str],
    ) -> None:
        objs = []
        for line in output:
            obj = {
                "run_id": run_id,
                "cmd": cmd,
                "is_stderr": is_stderr,
                "output": line,
            }
            objs.append(obj)
        async with self.post(url=f"/{run_id}/simulation/console", json=objs) as resp:
            _ = await resp.json()

    async def send_out_simulator(
        self,
        run_id: int,
        sim_id: int,
        sim_name: str,
        is_stderr: bool,
        output: list[str],
        created_at: datetime.datetime,
    ) -> None:
        objs = []
        for line in output:
            obj = {
                "run_id": run_id,
                "simulator_id": sim_id,
                "simulator_name": sim_name,
                "is_stderr": is_stderr,
                "output": line,
                "created_at": created_at.isoformat(),
            }
            objs.append(obj)
        async with self.post(url=f"/run/{run_id}/simulator/{sim_id}/console", json=objs) as resp:
            _ = await resp.json()

    async def send_out_proxy(
        self,
        run_id: int,
        proxy_id: int,
        is_stderr: bool,
        output: list[str],
    ) -> None:
        objs = []
        for line in output:
            obj = {
                "run_id": run_id,
                "proxy_id": proxy_id,
                "is_stderr": is_stderr,
                "output": line,
            }
            objs.append(obj)
        async with self.post(url=f"/{run_id}/proxy/{proxy_id}/console", json=objs) as resp:
            _ = await resp.json()
