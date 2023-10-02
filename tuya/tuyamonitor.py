import tuyapower
import tinytuya
import requests
import json
import threading
#tinytuya.set_debug(True)


def send_device_data(device_id, device_name, plug_id, plug_ip, plug_key, plug_vers='3.3'):
    (on, w, mA, V, err) = tuyapower.deviceInfo(plug_id, plug_ip, plug_key, plug_vers)
    data = tuyapower.deviceJSON(plug_id, plug_ip, plug_key, plug_vers)
    print(data)
    data_dict = json.loads(data)
    data_dict['device_id'] = device_id
    data_dict['device_name'] = device_name
    data = json.dumps(data_dict)

    def send_to_webhook(data, webhook_url):
        headers = {
            'Content-Type': 'application/json',
        }
        response = requests.get(webhook_url, data=data, headers=headers)
        return response.text

    webhook_url = "<WEBHOOK URL>"
    response_text = send_to_webhook(data, webhook_url)
    return response_text

# Example usage:
devices = [
    {
        "device_id": "d78eaf16c9fabccbeco7ly",
        "device_name": "SmartStrip2F",
        "plug_id": "d78eaf16c9fabccbeco7ly",
        "plug_ip": "192.168.0.93",
        "plug_key": ""
    },
    {
        "device_id": "d7d9f05b8a2963b458fjwu",
        "device_name": "SumpMotor",
        "plug_id": "d7d9f05b8a2963b458fjwu",
        "plug_ip": "192.168.0.151",
        "plug_key": ""
    }
    ,{
        "device_id": "d788920a6c67651ed92edu",
        "device_name": "Wipro2FTable",
        "plug_id": "d788920a6c67651ed92edu",
        "plug_ip": "192.168.0.98",
        "plug_key": r""
    }
    ,{
        "device_id": "d7c13d98acb37995b7tywi",
        "device_name": "2FUPSHomeMate",
        "plug_id": "d7c13d98acb37995b7tywi",
        "plug_ip": "192.168.0.126",
        "plug_key": r""
    }
    # Add more devices as needed...
]

def send_device_data_wrapper(device):
    global response_text
    response_text = send_device_data(
        device_id=device["device_id"],
        device_name=device["device_name"],
        plug_id=device["plug_id"],
        plug_ip=device["plug_ip"],
        plug_key=device["plug_key"]
    )


#for device in devices:
#    response = send_device_data(
#        device_id=device["device_id"],
#        device_name=device["device_name"],
#        plug_id=device["plug_id"],
#        plug_ip=device["plug_ip"],
#        plug_key=device["plug_key"]
#    )
#    print(response)
for device in devices:
    response_text = None
    thread = threading.Thread(target=send_device_data_wrapper, args=(device,))
    thread.start()
    thread.join(timeout=20)  # Wait for up to 60 seconds for the thread to complete

    if thread.is_alive():
        print(f"Device {device['device_name']} did not respond in 60 seconds. Skipping...")
        thread.join()  # Ensure the thread completes even if we move on
    else:
        print(response_text)
