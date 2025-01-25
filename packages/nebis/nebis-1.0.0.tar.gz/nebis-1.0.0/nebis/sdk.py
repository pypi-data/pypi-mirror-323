import requests
import json
import time
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
import tempfile

class NebisSDK:
    def __init__(self, connection_url: str, m='both', ttl=300):
        self.base_url, self.username, self.password, self.db_name = self._parse_connection_url(connection_url)
        self.headers = {"Authorization": f"Bearer {self.password}"}
        self.save_location = m
        self.session = self._create_session()
        self._check_connection()

        self.memory_data = {}
        self.ttl = ttl 
        self.memory_timestamps = {}

    def _parse_connection_url(self, connection_url):
        if not connection_url.startswith('nebis://'):
            raise ValueError("URL de conexión inválida.")
        
        base_url_and_token = connection_url[len('nebis://'): ]
        parsed_url = urlparse(f"http://{base_url_and_token}") 
        
        username = parsed_url.username
        password = parsed_url.password
        db_name = parsed_url.path.lstrip('/')
        
        if not username or not password or not db_name:
            raise ValueError("URL de conexión inválida. Faltan partes de la URL.")
        
        return f"http://{parsed_url.hostname}", username, password, db_name

    def _check_connection(self):
        self.send_request("ping")
    
    def _create_session(self):
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
        session.mount('http://', HTTPAdapter(max_retries=retries))
        session.mount('https://', HTTPAdapter(max_retries=retries))  
        return session

    def send_request(self, endpoint, method="GET", data=None):
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.request(method, url, json=data, headers=self.headers, timeout=15)  # Aumentar el timeout
            if response.ok:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return response.text
            else:
                print("Error en la respuesta:", response.text)
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error al enviar la solicitud: {e}")
            raise 

    def c(self, data):
        self._save_in_memory(data)

        if self.save_location == 'local' or self.save_location == 'both':
            self._save_locally(data)

        if self.save_location == 'server' or self.save_location == 'both':
            self._save_to_server(data)

        self._verify_and_sync(data)

    def _save_in_memory(self, data):
        self.memory_data[data["key"]] = data["value"]
        self.memory_timestamps[data["key"]] = time.time()
        print("Datos guardados en memoria.")

    def _check_memory_ttl(self):
        current_time = time.time()
        keys_to_delete = [key for key, timestamp in self.memory_timestamps.items() if current_time - timestamp > self.ttl]
        for key in keys_to_delete:
            del self.memory_data[key]
            del self.memory_timestamps[key]
            print(f"Datos con clave {key} han caducado en memoria.")

    def _save_locally(self, data):
        try:
            try:
                with open(self.db_name, 'r') as f:
                    local_data = json.load(f)
            except FileNotFoundError:
                local_data = {}

            local_data[data["key"]] = data["value"]

            with tempfile.NamedTemporaryFile('w', delete=False, dir=os.path.dirname(self.db_name)) as temp_file:
                json.dump(local_data, temp_file)  
                temp_file.flush()
                os.fsync(temp_file.fileno())
            os.replace(temp_file.name, self.db_name)
            print("Datos guardados localmente de forma atómica.")
        except Exception as e:
            print("Error al guardar localmente:", str(e))
                                                 
    def _save_to_server(self, data):
        if not data.get("key") or not data.get("value"):
            raise ValueError("Los datos deben contener 'key' y 'value'.")
        
        payload = {
            "key": data["key"],
            "value": data["value"],
            "db_name": self.db_name,
            "username": self.username,
        }
        
        response = self.send_request("add", method="POST", data=payload)
        
        if response:
            print("Datos enviados al servidor exitosamente.")
        else:
            print("Error al enviar los datos al servidor.")

    def r(self):
        self._check_memory_ttl()  
        if self.save_location == 'local' or self.save_location == 'both':
            try:
                with open(self.db_name, 'r') as f:
                    return json.load(f)
            except FileNotFoundError:
                print(f"Archivo {self.db_name} no encontrado. Cargando desde el servidor...")
        
        return self._load_from_server()

    def _load_from_server(self, key):
        return self.send_request(f"get/{key}")

    def u(self, data):
        if "key" not in data or "value" not in data:
            print("Error: 'data' debe contener 'key' y 'value'.")
            return

        payload = {
            "key": data["key"],
            "value": data["value"],
            "db_name": self.db_name,
            "username": self.username,
        }

        response = self.send_request("update", method="PUT", data=payload)

        if response:
            print("Datos actualizados exitosamente.")
            if self.save_location == 'local' or self.save_location == 'both':
                self._update_locally(data)
        else:
            print("Error al actualizar los datos.")

        self._verify_and_sync(data)

    def _update_locally(self, data):
        try:
            local_data = self.r() 
            if local_data and data["key"] in local_data:
                local_data[data["key"]] = data["value"] 
                self._save_locally({"key": data["key"], "value": data["value"]}) 
                print("Datos actualizados localmente.")
            else:
                print(f"Error: La clave {data['key']} no se encuentra en los datos locales.")
        except Exception as e:
            print("Error al actualizar localmente:", str(e))

            
    def d(self, data):
        payload = {
            "key": data["key"],
            "db_name": self.db_name,
            "username": self.username,
        }

        response = self.send_request("delete", method="DELETE", data=payload)

        if response:
            print("Datos eliminados del servidor exitosamente.")
            if self.save_location == 'both':
                self._delete_locally(data["key"])
            return True
        else:
            print("Error al eliminar los datos del servidor.")
            return False

    def _delete_locally(self, key):
        try:
            local_data = self.r()  
            print(f"Datos locales antes de la eliminación: {local_data}") 

            if key in local_data:
                del local_data[key]  

                with open(self.db_name, 'w') as f:
                    json.dump(local_data, f, indent=4) 

                print("Datos eliminados localmente.")
            else:
                print("Clave no encontrada en los datos locales.")
        except Exception as e:
            print("Error al eliminar localmente:", str(e))



    def _verify_and_sync(self, key):
        for key in list(self.memory_data.keys()):
            if self._is_data_synced(key):
                del self.memory_data[key]
                del self.memory_timestamps[key]
                print(f"Datos con clave {key} sincronizados y limpiados de memoria.")
  
    def _is_data_synced(self, key):
        server_data = self._load_from_server(key)
        local_data = self.r()
        return (key in local_data and local_data[key] == self.memory_data[key] and
                key in server_data and server_data[key] == self.memory_data[key])