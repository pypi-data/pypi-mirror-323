from typing import Any, List, Tuple
import requests
import json
import time
import httpx
import asyncio

from .sign import query, sign, get_pid


class ZKWasmAppRpc:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def send_raw_transaction(self, cmd: list[int], prikey: str) -> dict:
        data = sign(cmd, prikey)
        print("SendRawTransaction", data)
        response = self.session.post(f"{self.base_url}/send", json=data)
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception("SendTransactionError")

    def send_transaction(self, cmd: list[int], prikey: str) -> dict:
        resp = self.send_raw_transaction(cmd, prikey)
        for _ in range(5):
            time.sleep(1)
            try:
                job_status = self.query_job_status(resp["jobid"])
                if "finishedOn" not in job_status:
                    raise Exception("WaitingForProcess")
            except Exception:
                continue
            if job_status:
                if "finishedOn" in job_status and "failedReason" not in job_status:
                    return job_status["returnvalue"]
                else:
                    raise Exception(job_status["failedReason"])
        raise Exception("MonitorTransactionFail")

    def query_state(self, prikey: str) -> dict:
        data = query(prikey)
        response = self.session.post(f"{self.base_url}/query", json=data)
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception("UnexpectedResponseStatus")

    def query_config(self) -> dict:
        response = self.session.post(f"{self.base_url}/config")
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception("QueryConfigError")

    def query_job_status(self, job_id: int) -> dict:
        response = self.session.get(f"{self.base_url}/job/{job_id}")
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception("QueryJobError")

    @staticmethod
    def create_command(nonce: int, command: int, params: List[int]) -> List[int]:
        cmd = (nonce << 16) + ((len(params) + 1) << 8) + command
        buf = [cmd] + params
        print("CreateCommand", buf)
        return buf

    def compose_withdraw_params(self, address: str, nonce: int, command: int, amount: int, token_index: int)\
            -> List[int]:
        if address.startswith("0x"):
            address = address[2:]
        address_be = bytes.fromhex(address)
        first_limb = int.from_bytes(address_be[:4][::-1], byteorder="big")
        snd_limb = int.from_bytes(address_be[4:12][::-1], byteorder="big")
        third_limb = int.from_bytes(address_be[12:20][::-1], byteorder="big")
        one = (first_limb << 32) + amount
        return self.create_command(nonce, command, [token_index, one, snd_limb, third_limb])

    def get_nonce(self, prikey: str) -> int:
        state = self.query_state(prikey)
        data = json.loads(state["data"])
        return int(data["player"]["nonce"])

    def get_pid(self, prikey:str) -> Tuple[int, int]:
        return get_pid(prikey)

class AsyncZKWasmAppRpc:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
        self.headers = {"Content-Type": "application/json"}

    async def send_raw_transaction(self, cmd: list[int], prikey: str) -> dict:
        data = sign(cmd, prikey)
        response = await self.client.post(
            f"{self.base_url}/send", json=data, headers=self.headers
        )
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception("SendTransactionError")

    async def send_transaction(self, cmd: list[int], prikey: str) -> int:
        try:
            resp = await self.send_raw_transaction(cmd, prikey)
            for _ in range(5):
                await asyncio.sleep(1)
                try:
                    job_status = await self.query_job_status(resp["jobid"])
                    if "finishedOn" not in job_status:
                        raise Exception("WaitingForProcess")
                except Exception:
                    continue
                if job_status:
                    if "finishedOn" in job_status and "failedReason" not in job_status:
                        return job_status["returnvalue"]
                    else:
                        raise Exception(job_status["failedReason"])
            raise Exception("MonitorTransactionFail")
        except Exception as e:
            raise e

    async def query_state(self, prikey: str) -> dict:
        data = query(prikey)
        response = await self.client.post(
            f"{self.base_url}/query", json=data, headers=self.headers
        )
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception("UnexpectedResponseStatus")

    async def query_config(self) -> dict:
        response = await self.client.post(
            f"{self.base_url}/config", headers=self.headers
        )
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception("QueryConfigError")

    async def query_job_status(self, job_id: int) -> dict:
        response = await self.client.get(
            f"{self.base_url}/job/{job_id}", headers=self.headers
        )
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception("QueryJobError")

    @staticmethod
    async def create_command(nonce: int, command: int, params: List[int]) -> List[int]:
        cmd = (nonce << 16) + ((len(params) + 1) << 8) + command
        buf = [cmd] + params
        print("CreateCommand", buf)
        return buf

    async def compose_withdraw_params(self, address: str, nonce: int, command: int, amount: int, token_index: int) \
            -> List[int]:
        if address.startswith("0x"):
            address = address[2:]
        address_be = bytes.fromhex(address)
        first_limb = int.from_bytes(address_be[:4][::-1], byteorder="big")
        snd_limb = int.from_bytes(address_be[4:12][::-1], byteorder="big")
        third_limb = int.from_bytes(address_be[12:20][::-1], byteorder="big")
        one = (first_limb << 32) + amount
        return await self.create_command(nonce, command, [token_index, one, snd_limb, third_limb])
    
    async def get_nonce(self, prikey: str) -> int:
        state = await self.query_state(prikey)
        data = json.loads(state["data"])
        return int(data["player"]["nonce"])

    async def get_pid(self, prikey:str) -> Tuple[int, int]:
        return get_pid(prikey)
