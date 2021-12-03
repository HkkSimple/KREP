from simple_service.application.build import APPLICATION_REGISTRY
from flask import Flask, jsonify
from simple_service.config.config import Config
from simple_service.config.options import Options
from simple_service.service.default import DefaultServer
# from simple_service.application.base import BaseApplication

app = Flask(__name__)
from . import application

# '''
# use register to define a application
# '''
# @APPLICATION_REGISTRY.register()
# class testApp(BaseApplication):
#     def __init__(self, cfg):
#         self.cfg = cfg

#         self.input_param_message_name = self.cfg.SERVICE.INPUT.IMAGE

#     def preprocessing(self, data):
#         decoded_data = data[self.input_param_message_name]
#         new_data = decoded_data + '--->' + 'Receive the hello world'
#         return new_data

#     def decode_predict_data(self, data):
#         return data

#     def format_output_data(self, data):
#         return data

#     def inference(self, data):
#         return data

def main():
    opt = Options().parse()
    cfg = Config().default_setup(opt)

    server = DefaultServer(cfg)
    server(app)


if __name__ == '__main__':
    main()
