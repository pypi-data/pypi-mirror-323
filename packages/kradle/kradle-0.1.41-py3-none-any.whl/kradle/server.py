from flask import Flask, jsonify, request
import threading
import socket
from werkzeug.serving import make_server
import signal
from flask_cors import CORS
import logging
from kradle.models import Observation
from dataclasses import dataclass
import requests
from dotenv import load_dotenv
import os
from kradle.ssh_tunnel import create_tunnel

load_dotenv()

@dataclass
class AgentConfig:
    participant_id: str
    session_id: str
    task: str
    agent_modes: list
    commands: list
    js_functions: list
    available_events: list

class Kradle:
    _instance = None
    _server = None
    _server_ready = threading.Event()
    _shutdown_event = threading.Event()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Kradle, cls).__new__(cls)
            cls._instance._agents = {}  # participant_id -> agent instance
            cls._instance._agent_classes = {}  # slug -> {class: agent_class, count: int}
            cls._instance._app = None
            cls._instance.port = None
            cls._instance._server_thread = None
            cls._instance._main_thread = None
            cls._instance._api_key = os.getenv("KRADLE_API_KEY")
        return cls._instance

    def _is_port_available(self, port, host='localhost'):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port))
                return True
        except OSError:
            return False

    def _find_free_port(self, start_port=1500, end_port=1549):
        for port in range(start_port, end_port + 1):
            if self._is_port_available(port):
                return port
        raise RuntimeError(f"No free ports available in range {start_port}-{end_port}")

    def _get_or_create_agent(self, participant_id, slug):
        # if we already have an agent for this participant, return it
        if participant_id in self._agents:
            return self._agents[participant_id]

        # if we don't have an agent, create one
        # if we don't have a slug, use the first one
        if slug is None:
            if not self._agent_classes:
                raise ValueError("No agent classes registered")
            # get the first agent class
            slug = next(iter(self._agent_classes))

        # if we have a class for this slug, use it
        if slug in self._agent_classes:
            agent_class = self._agent_classes[slug]['class']
        else:        
            # if we have a catch-all class, use it
            if "*" in self._agent_classes:
                agent_class = self._agent_classes["*"]['class']
            else:
                raise ValueError(f"No agent class registered for slug: {slug}, no catch-all agent found")
        
        # Create new agent instance with slug parameter
        agent = agent_class(slug=slug)
        agent.participant_id = participant_id
        self._agents[participant_id] = agent
            
        return self._agents[participant_id]

    def _get_instance_counts(self, slug=None):
        if slug:
            if slug not in self._agent_classes:
                return None
            class_name = self._agent_classes[slug]['class'].__name__
            count = self._agent_classes[slug]['count']
            return {'class_name': class_name, 'instances': count}
            
        counts = {}
        for slug, info in self._agent_classes.items():
            counts[slug] = {
                'class_name': info['class'].__name__,
                'instances': info['count']
            }
        return counts

    def _create_app(self):
        app = Flask(__name__)
        app.config['DEBUG'] = True
        app.config['ENV'] = 'development'
        logging.getLogger('werkzeug').disabled = False
        logging.basicConfig(level=logging.DEBUG)  # Set the logging level to DEBUG
        CORS(app)

        @app.route('/')
        def index():
            base_url = f"http://localhost:{self.port}"
            response = {
                'status': 'online',
                'agents': {},
            }
            
            for slug in self._agent_classes.keys():
                agent_urls = {
                    'base': f"{base_url}/{slug}",
                    'ping': f"{base_url}/{slug}/ping",
                    'init': f"{base_url}/{slug}/init",
                    'event': f"{base_url}/{slug}/event"
                }
                response['agents'][slug] = agent_urls
                
            return jsonify(response)

        @app.route('/<slug>')
        def agent_index(slug):
            if slug not in self._agent_classes:
                return '', 404
                
            base_url = f"http://localhost:{self.port}/{slug}"
            stats = self._get_instance_counts(slug)
            
            return jsonify({
                'status': 'online',
                'class_name': stats['class_name'],
                'instances': stats['instances'],
                'urls': {
                    'ping': f"{base_url}/ping",
                    'init': f"{base_url}/init",
                    'event': f"{base_url}/event"
                }
            })

        @app.route('/ping', defaults={'slug': None})
        @app.route('/<slug>/ping')
        def ping(slug):
            if slug:
                if slug not in self._agent_classes:
                    return '', 404
                stats = self._get_instance_counts(slug)
                return jsonify({
                    'status': 'online',
                    'class_name': stats['class_name'],
                    'instances': stats['instances']
                })

            return jsonify({
                'status': 'online',
                'agents': self._get_instance_counts()
            })

        @app.route('/init', defaults={'slug': None}, methods=['POST'])
        @app.route('/<slug>/init', methods=['POST'])
        def init(slug):
            data = request.get_json() or {}
            participant_id = data.get('participantId')

            if participant_id is None:
                return jsonify({'error': 'participantId is required'}), 400

            try:
                agent = self._get_or_create_agent(participant_id, slug)
                agent_config = AgentConfig(
                    participant_id=participant_id,
                    session_id=data.get('sessionId'),
                    task=data.get('task'),
                    agent_modes=data.get('agent_modes'),
                    commands=data.get('commands'),
                    js_functions=data.get('js_functions'),
                    available_events=data.get('available_events')
                )
                init_data = agent.initialize_agent(agent_config)
                return jsonify({'choices': init_data})
            except ValueError as e:
                return jsonify({'error': str(e)}), 400

        @app.route('/event', defaults={'slug': None}, methods=['POST'])
        @app.route('/<slug>/event', methods=['POST'])
        def event(slug):
            data = request.get_json() or {}
            observation = Observation.from_event(data)
            participant_id = data.get('participantId')
            
            if participant_id is None:
                return jsonify({'error': 'participantId is required'}), 400

            try:
                agent = self._get_or_create_agent(participant_id, slug)
                result = agent.on_event(observation)
                return jsonify(result)
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
            
        return app

    def _run_server(self):
        try:
            self._server = make_server('0.0.0.0', self.port, self._app)
            self._server_ready.set()
            self._server.serve_forever()
        except Exception as e:
            self._shutdown_event.set()
            raise e
            
    def _setup_signal_handlers(self):
        def handle_shutdown(signum, frame):
            print("\nShutting down server...")
            self._shutdown_event.set()
            if self._server:
                self._server.shutdown()
        
        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)


    @classmethod
    def register_agent(cls, slug, url):
        #make a call to setAgentUrl api endpoint with params agentSlug and agentUrl
        # Environment-specific URLs

        if slug == "*":
            print("Cannot register a catch-all slug")
            return False

        instance = cls()

        KRADLE_APP_URL = (
            "http://localhost:3000" 
            if os.getenv("KRADLE_DEV") 
            else "https://mckradleai.vercel.app"
        )

        try:
        
            # Make API request
            response = requests.post(
                f'{KRADLE_APP_URL}/api/setAgentUrl',
                headers={
                    'Content-Type': 'application/json',
                    'kradle-api-key': instance._api_key
                },
                json={
                    'agentSlug': slug,
                    'agentUrl': url
                },
                timeout=30
            )
            
            if response.status_code in (200, 201):
                print(f"Agent {slug} registered successfully")
                return True
                    
        except Exception as e:
            print(f"Update agentUrl failed: {e}")
            return False

    def _create_tunnel(self, port):
        tunnel_instance, tunnel_url = create_tunnel(port)
        if tunnel_instance:
            self._tunnel = tunnel_instance
            return tunnel_url
        else:
            print("Warning: Failed to create tunnel, falling back to local URL")
            return None
    
    @classmethod
    def serve_agent(cls, agent_class, slug, port=None, tunnel=True, host='localhost'):
        instance = cls()
        
        # Initialize or increment instance count for this slug
        if slug not in instance._agent_classes:
            instance._agent_classes[slug] = {
                'class': agent_class,
                'count': 1
            }
        else:
            instance._agent_classes[slug]['count'] += 1
        
        if not instance._app:
            instance._app = instance._create_app()
            instance.port = port if port is not None else instance._find_free_port()
            
            if not instance._is_port_available(instance.port):
                raise ValueError(f"Port {instance.port} is not available")
            
            instance._setup_signal_handlers()
            instance._server_thread = threading.Thread(target=instance._run_server, daemon=True)
            instance._server_thread.start()
            
            if not instance._server_ready.wait(timeout=5.0):
                raise RuntimeError("Server failed to start within timeout")
            
            print("Server is running. Press Ctrl+C to stop.")
            
            instance._main_thread = threading.Thread(target=instance._shutdown_event.wait)
            instance._main_thread.daemon = False
            instance._main_thread.start()
        
            agent_url =  f"http://localhost:{instance.port}/{slug}"

            if tunnel:
                tunnel_url = instance._create_tunnel(instance.port)
                agent_url = f"{tunnel_url}/{slug}"
            
            if slug != "*":
                # slug = "*" is a catch-all, so we don't need to register it
                instance.register_agent(slug, agent_url)

            return agent_url
        

    @classmethod
    def get_agent_behavior(cls, slug):
        #make a call to setAgentUrl api endpoint with params agentSlug and agentUrl
        # Environment-specific URLs

        instance = cls()

        KRADLE_APP_URL = (
            "http://localhost:3000" 
            if os.getenv("KRADLE_DEV") 
            else "https://mckradleai.vercel.app"
        )

        try:
            # Make API request
            response = requests.post(
                f'{KRADLE_APP_URL}/api/getAgentBehavior',
                headers={
                    'Content-Type': 'application/json',
                    'kradle-api-key': instance._api_key
                },
                json={
                    'agentSlug': slug,
                },
                timeout=30
            )
            
            if response.status_code in (200, 201):
                print(f"Agent {slug} behavior retrieved successfully")
                return response.json()
            else:
                print(f"Agent {slug} behavior retrieval failed")  
                return None
                    
        except Exception as e:
            print(f"Agent {slug} behavior retrieval failed: {e}")
            return None
