from .configuration import Configuration
from connectus.tools.structure.data import DataResponse, DataRequest
from abc import ABC, abstractmethod
import asyncio

class BaseDevice(ABC, Configuration):
    def __init__(self, name: str, device_type: str, node_params: dict[str, str] = None):
        self.id = name
        self.device_type = device_type
        self.node_params = node_params
        self.node = None
        self.experiment_id = None
        Configuration.__init__(self)

    def get(self, request_list: list[DataRequest]) -> list[DataResponse]:
        try:
            response = []
            for request in request_list:
                if request.action == 'get_state':
                    response += [DataResponse(response= request.action, device_ids= [self.id], data= self.state)]
                elif request.action == 'get_config':
                    response += [DataResponse(response= request.action, device_ids= [self.id], data= self.config)]
                else:
                    raise ValueError('Request not recognized')
            return response
        except Exception as e:
            print('An error occurred during get request: ', e)

    def set(self, request_list: list[DataRequest]): ## improve this
        try:
            for request in request_list:
                requests = self.acquisition.process_request(request)
                asyncio.create_task(self.data_processing.process_data(requests)) ## improve this
        except Exception as e:
            print('An error occurred during set request: ', e)

    async def run(self):
        data = await self.acquisition.run()
        await self.data_processing.process_data(data)
        self.total_time += self.step_time

    async def stop(self): ## should send data to the database (NULL)
        data = await self.acquisition.stop()
        await self.data_processing.process_data(data)
