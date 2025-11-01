"""
LLM Management Routes
Handles LLM configuration, testing, and management

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

from flask import request, render_template, jsonify, session
from datetime import datetime
import time
import json
import os
from routes.base_routes import BaseRoutes

class LLMRoutes(BaseRoutes):
    """LLM management routes handler"""

    def __init__(self, app, llm_facade_class, login_required, admin_required):
        """
        Initialize LLM routes
        
        Args:
            app: Flask app instance
            llm_facade_class: LLMFacade class (not instance)
            login_required: Login decorator
            admin_required: Admin decorator
        """
        super().__init__()

        self.app = app
        self.LLMFacade = llm_facade_class
        self.login_required = login_required
        self.admin_required = admin_required
        self.register_routes()

    def get_user_from_session(self):
        """Get user object from session"""
        from core.user_registry import UserRegistry
        if 'user_id' in session:
            user_registry = UserRegistry()
            return user_registry.get_user(session['user_id'])
        return None

    def load_llm_config(self):
        """Load LLM configuration from file"""
        try:
            # Try multiple paths
            config_paths = [
                'config/llm/llm_config.json',
                'llm_config.json',
                '/home/claude/llm_config.json',
                'llm/llm_config.json'
            ]
            
            for path in config_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        return json.load(f)
            
            # If not found, return default config
            return {
                'default_provider': 'mock',
                'default_model': 'mock-llm',
                'providers': {
                    'mock': {
                        'enabled': True,
                        'models': {
                            'mock-llm': {
                                'enabled': True,
                                'model_id': 'mock-llm-v1',
                                'description': 'Mock LLM for testing',
                                'context_window': 100000,
                                'max_tokens': 100000,
                                'cost_per_1m_input_tokens': 0.0,
                                'cost_per_1m_output_tokens': 0.0,
                                'best_for': ['testing', 'development'],
                                'supports_vision': False,
                                'supports_function_calling': False,
                                'supports_streaming': False
                            }
                        }
                    }
                }
            }
        except Exception as e:
            print(f"Error loading LLM config: {e}")
            return {'providers': {}}

    def save_llm_config(self, config):
        """Save LLM configuration to file"""
        try:
            config_paths = [
                'config/llm/llm_config.json',
                'llm_config.json',
                '/home/claude/llm_config.json'
            ]
            
            for path in config_paths:
                if os.path.exists(path):
                    with open(path, 'w') as f:
                        json.dump(config, f, indent=2)
                    return True
            
            # If no file exists, create in current directory
            with open('llm_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            return True
            
        except Exception as e:
            print(f"Error saving LLM config: {e}")
            return False

    def register_routes(self):
        """Register all LLM management routes"""

        @self.app.route('/llm-management')
        @self.login_required
        def llm_management():
            """LLM Management page"""
            user = self.get_user_from_session()
            config = self.load_llm_config()
            
            # Calculate statistics
            total_providers = len(config.get('providers', {}))
            enabled_providers = sum(1 for p in config.get('providers', {}).values() if p.get('enabled', False))
            
            total_models = 0
            enabled_models = 0
            for provider_info in config.get('providers', {}).values():
                models = provider_info.get('models', {})
                total_models += len(models)
                enabled_models += sum(1 for m in models.values() if m.get('enabled', False))
            
            # Get last refresh time
            last_refresh = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if hasattr(self.LLMFacade, '_config_instance') and self.LLMFacade._config_instance:
                if self.LLMFacade._config_instance.last_loaded:
                    last_refresh = self.LLMFacade._config_instance.last_loaded.strftime('%Y-%m-%d %H:%M:%S')
            
            config_summary = {
                'total_providers': total_providers,
                'enabled_providers': enabled_providers,
                'total_models': total_models,
                'enabled_models': enabled_models,
                'default_provider': config.get('default_provider', 'Not set'),
                'default_model': config.get('default_model', 'Not set'),
                'last_refresh': last_refresh
            }
            
            return render_template(
                'llm_management.html',
                user=user,
                config=config_summary,
                providers=config.get('providers', {})
            )

        @self.app.route('/api/llm/refresh', methods=['POST'])
        @self.admin_required
        def api_refresh_llm_config():
            """Refresh LLM configuration from file"""
            try:
                # Force reload of configuration
                if hasattr(self.LLMFacade, '_config_instance') and self.LLMFacade._config_instance:
                    self.LLMFacade._config_instance.load_config()
                    return jsonify({'success': True, 'message': 'Configuration refreshed'})
                else:
                    return jsonify({'success': False, 'error': 'Config manager not initialized'})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/api/llm/test-all', methods=['POST'])
        @self.admin_required
        def api_test_all_llm_connections():
            """Test connections to all enabled providers"""
            try:
                config = self.load_llm_config()
                results = {}
                
                for provider_name, provider_info in config.get('providers', {}).items():
                    if not provider_info.get('enabled', False):
                        continue
                    
                    # Get first enabled model for this provider
                    test_model = None
                    for model_name, model_info in provider_info.get('models', {}).items():
                        if model_info.get('enabled', False):
                            test_model = model_name
                            break
                    
                    if not test_model:
                        results[provider_name] = {'success': False, 'error': 'No enabled models'}
                        continue
                    
                    try:
                        llm = self.LLMFacade(provider=provider_name, model=test_model)
                        response = llm.generate("Hello, respond with 'OK'", max_tokens=10)
                        results[provider_name] = {'success': True, 'response': response[:50]}
                    except Exception as e:
                        results[provider_name] = {'success': False, 'error': str(e)}
                
                return jsonify({'success': True, 'results': results})
            
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/api/llm/model-details', methods=['GET'])
        @self.login_required
        def api_get_llm_model_details():
            """Get detailed information about a specific model"""
            try:
                provider = request.args.get('provider')
                model = request.args.get('model')
                
                if not provider or not model:
                    return jsonify({'success': False, 'error': 'Provider and model required'}), 400
                
                config = self.load_llm_config()
                provider_info = config.get('providers', {}).get(provider)
                
                if not provider_info:
                    return jsonify({'success': False, 'error': 'Provider not found'}), 404
                
                model_info = provider_info.get('models', {}).get(model)
                
                if not model_info:
                    return jsonify({'success': False, 'error': 'Model not found'}), 404
                
                return jsonify({'success': True, 'details': model_info})
            
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/api/llm/test-model', methods=['POST'])
        @self.login_required
        def api_test_llm_model():
            """Test a specific LLM model"""
            try:
                data = request.get_json()
                provider = data.get('provider')
                model = data.get('model')
                
                if not provider or not model:
                    return jsonify({'success': False, 'error': 'Provider and model required'}), 400
                
                # Test the model
                start_time = time.time()
                
                try:
                    llm = self.LLMFacade(provider=provider, model=model)
                    test_prompt = "Hello! Please respond with a brief greeting to confirm you're working."
                    response = llm.generate(test_prompt, max_tokens=50)
                    
                    duration = time.time() - start_time
                    
                    return jsonify({
                        'success': True,
                        'response': response,
                        'duration': duration,
                        'model_info': llm.get_model_info()
                    })
                
                except Exception as e:
                    duration = time.time() - start_time
                    return jsonify({
                        'success': False,
                        'error': str(e),
                        'duration': duration
                    })
            
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/api/llm/set-default', methods=['POST'])
        @self.admin_required
        def api_set_default_llm():
            """Set default LLM provider and model"""
            try:
                data = request.get_json()
                provider = data.get('provider')
                model = data.get('model')
                
                if not provider or not model:
                    return jsonify({'success': False, 'error': 'Provider and model required'}), 400
                
                config = self.load_llm_config()
                
                # Verify provider and model exist
                if provider not in config.get('providers', {}):
                    return jsonify({'success': False, 'error': 'Provider not found'}), 404
                
                if model not in config['providers'][provider].get('models', {}):
                    return jsonify({'success': False, 'error': 'Model not found'}), 404
                
                # Update default
                config['default_provider'] = provider
                config['default_model'] = model
                
                if self.save_llm_config(config):
                    # Force reload
                    if hasattr(self.LLMFacade, '_config_instance') and self.LLMFacade._config_instance:
                        self.LLMFacade._config_instance.load_config()
                    
                    return jsonify({
                        'success': True,
                        'message': f'Default LLM set to {provider}/{model}'
                    })
                else:
                    return jsonify({'success': False, 'error': 'Failed to save configuration'}), 500
            
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/api/llm/toggle-model', methods=['POST'])
        @self.admin_required
        def api_toggle_llm_model():
            """Enable or disable a specific model"""
            try:
                data = request.get_json()
                provider = data.get('provider')
                model = data.get('model')
                action = data.get('action')  # 'enable' or 'disable'
                
                if not provider or not model or not action:
                    return jsonify({'success': False, 'error': 'Provider, model, and action required'}), 400
                
                config = self.load_llm_config()
                
                if provider not in config.get('providers', {}):
                    return jsonify({'success': False, 'error': 'Provider not found'}), 404
                
                if model not in config['providers'][provider].get('models', {}):
                    return jsonify({'success': False, 'error': 'Model not found'}), 404
                
                # Update model status
                config['providers'][provider]['models'][model]['enabled'] = (action == 'enable')
                
                if self.save_llm_config(config):
                    # Force reload
                    if hasattr(self.LLMFacade, '_config_instance') and self.LLMFacade._config_instance:
                        self.LLMFacade._config_instance.load_config()
                    
                    return jsonify({
                        'success': True,
                        'message': f'Model {provider}/{model} {action}d'
                    })
                else:
                    return jsonify({'success': False, 'error': 'Failed to save configuration'}), 500
            
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/api/llm/toggle-provider', methods=['POST'])
        @self.admin_required
        def api_toggle_llm_provider():
            """Enable or disable all models for a provider"""
            try:
                data = request.get_json()
                provider = data.get('provider')
                action = data.get('action')  # 'enable' or 'disable'
                
                if not provider or not action:
                    return jsonify({'success': False, 'error': 'Provider and action required'}), 400
                
                config = self.load_llm_config()
                
                if provider not in config.get('providers', {}):
                    return jsonify({'success': False, 'error': 'Provider not found'}), 404
                
                # Update provider status
                enabled = (action == 'enable')
                config['providers'][provider]['enabled'] = enabled
                
                # Also update all models
                for model_name in config['providers'][provider].get('models', {}).keys():
                    config['providers'][provider]['models'][model_name]['enabled'] = enabled
                
                if self.save_llm_config(config):
                    # Force reload
                    if hasattr(self.LLMFacade, '_config_instance') and self.LLMFacade._config_instance:
                        self.LLMFacade._config_instance.load_config()
                    
                    return jsonify({
                        'success': True,
                        'message': f'Provider {provider} {action}d'
                    })
                else:
                    return jsonify({'success': False, 'error': 'Failed to save configuration'}), 500
            
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/api/llm/available-models', methods=['GET'])
        @self.login_required
        def api_get_available_models():
            """Get list of all available models (for dropdowns, etc.)"""
            try:
                models = self.LLMFacade.list_available_models()
                return jsonify({'success': True, 'models': models})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/api/llm/recommend-model', methods=['GET'])
        @self.login_required
        def api_recommend_llm_model():
            """Get recommended model for a task type"""
            try:
                task_type = request.args.get('task_type', 'general')
                provider, model = self.LLMFacade.get_recommended_model(task_type)
                
                return jsonify({
                    'success': True,
                    'provider': provider,
                    'model': model,
                    'task_type': task_type
                })
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500
