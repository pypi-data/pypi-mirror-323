# GRID Python SDK
Python SDK to simplify integration with GRID services: https://gridgs.com

**It's in beta state now. Please expect changes (we'll try to keep them backward-compatible).**

# Main parts
GridAuthClient - Used to authorize on GRID SSO server.

GridApiClient - Client for GRID RespAPI that can work with main Grid entities (right now with sessions only).

GridEventSubscriber - subscriber to receive real-time events about changes in sessions (creation, deletion, starting and so on).

GridMQTTClient - Client for GRID MQTT API. It useful for realtime connection (receive downlink frames and send uplink frames).

# Examples how to use
## GridAuthClient
```
keycloak_openid = KeycloakOpenID(server_url="https://login.gridgs.com", client_id="grid-api", realm_name="grid")
grid_auth_client = GridAuthClient(open_id_client=keycloak_openid, username="user@gridgs.com", password="userpass", company_id=1, logger=logging.getLogger('grid_auth_client'))
```

## GridApiClient

```
grid_api_client = GridApiClient(base_url="https://api.gridgs.com" auth_client=grid_auth_client, logger=logging.getLogger('grid_api_client'))
```

### Get predicted sessions
```
sessions = grid_api_client.get_predicted_sessions() 
```

### Create a session

```
session = Session() # A session from get_predicted_sessions
session = grid_api_client.create_session(session)
```

## GridEventSubscriber

Receive statuses of sessions

```
grid_event_subscriber = GridEventSubscriber(host="api.gridgs.com", port=1883, auth_client=grid_auth_client, logger=logging.getLogger('grid_event_subscriber'))

def on_event(self, event: SessionEvent):
    session = event.session

grid_event_subscriber.on_event(on_event)

grid_event_subscriber.run()
```

## GridMQTTClient

```
grid_mqtt_client = GridMQTTClient(host="api.gridgs.com", port=1883, auth_client=grid_auth_client, logger=logging.getLogger('grid_event_subscriber'))

def on_downlink_frame(frame: Frame):
    pass

grid_mqtt_client.on_downlink(on_downlink_frame)

grid_mqtt_client.connect(session)
```

### Sending a frame

```
grid_mqtt_client.send(b'Uplink frame data')
```
