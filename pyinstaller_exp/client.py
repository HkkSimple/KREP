from flask import Flask, jsonify
import os
import requests
import json

def request_api(url, header, params):
    response = requests.post(url, headers=header, data=json.dumps(params))
    return response.text

def main():
    message = "Hello world!"
    params = {'imageData': message, "imageUUID": '11'}
    url = 'http://127.0.0.1:8071/test'
    headers = {'Content-Type':'application/json;charset=UTF-8'}
    response = request_api(url, headers, params)
    return response

if __name__ == '__main__':
    response = main()
    print('client request result is: ', response)
