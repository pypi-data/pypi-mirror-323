from contextlib import contextmanager
from threading import Thread
import upgen.model.uphy as uphy_model
from uphy.device import DeviceError, Protocol
import logging
from http.server import BaseHTTPRequestHandler
from socketserver import TCPServer
from zeroconf import ServiceInfo, Zeroconf
import socket
import psutil

LOGGER = logging.getLogger(__name__)


@contextmanager
def _model_server(model: uphy_model.Root, address: str):
    print(address)

    path = "/model.json"

    class ModelHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == path:
                self.send_response(200)
                self.send_header("Content-type", "text/json")
                self.end_headers()
                self.wfile.write(model.json().encode())
            else:
                self.send_error(404, "File Not Found: %s" % self.path)

    class BasicServer(TCPServer):
        def server_bind(self):
            TCPServer.server_bind(self)
            host, port = self.server_address[:2]
            self.server_host = host
            self.server_port = port

    LOGGER.debug("Starting model server")
    server = BasicServer((address, 0), ModelHandler, bind_and_activate=True)

    def _run():
        LOGGER.info("Serving model on port %s and path %s", server.server_port, path)
        server.serve_forever()

    runner = Thread(
        target=_run,
        name="Model server",
        daemon=True,
    )
    runner.start()

    try:
        yield server.server_port, path
    finally:
        server.shutdown()


@contextmanager
def run(model: uphy_model.Root, device: uphy_model.Device, interface: str, protocol: Protocol):
    if protocol != Protocol.MODBUS:
        yield
        return

    interfaces = psutil.net_if_addrs()
    if not (interface_data := interfaces.get(interface, None)):
        raise DeviceError(f"Interface '{interface}' not found in {interfaces}")

    ips = [entry.address for entry in interface_data if entry.family == socket.AF_INET]
    addresses = [socket.inet_aton(ip) for ip in ips]

    with _model_server(model, ips[0]) as (model_port, model_path):
        info = ServiceInfo(
            "_modbus._tcp.local.",
            f"{device.name} ({addresses})._modbus._tcp.local.",
            int(device.modbus.port, 0) if device.modbus else 502,
            addresses=addresses,
            properties={
                "model-port": model_port,
                "model-path": model_path,
                "device-id": device.id,
            },
        )
        zeroconf = Zeroconf()
        try:
            zeroconf.register_service(info)
            yield
        finally:
            zeroconf.close()
