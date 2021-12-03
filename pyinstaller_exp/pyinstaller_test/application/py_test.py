from simple_service.application.build import APPLICATION_REGISTRY
from simple_service.application.base import BaseApplication


'''
use register to define a application
'''


@APPLICATION_REGISTRY.register()
class testApp(BaseApplication):
    def __init__(self, cfg):
        self.cfg = cfg

        self.input_param_message_name = self.cfg.SERVICE.INPUT.IMAGE

    def preprocessing(self, data):
        decoded_data = data[self.input_param_message_name]
        new_data = decoded_data + '--->' + 'Receive the hello world'
        return new_data

    def decode_predict_data(self, data):
        return data

    def format_output_data(self, data):
        return data

    def inference(self, data):
        return data
