"""
Web 路由
"""

from flask import jsonify, request, current_app, send_file
from pathlib import Path
import io
import cv2
from utils.validators import validate_file

def create_routes(app):
    @app.route('/', methods=['GET'])
    def index():
        return jsonify({'status': 'running', 'name': 'Virtual Camera Live System', 'version': '1.0.0'})
    
    @app.route('/api/status', methods=['GET'])
    def get_status():
        virtual_app = current_app.config.get('VIRTUAL_CAMERA_APP')
        if not virtual_app:
            return jsonify({'error': 'Virtual Camera App not available'}), 500
        stats = {
            'camera': virtual_app.camera_manager.get_stats() if virtual_app.camera_manager else {},
            'video': virtual_app.video_loader.get_stats() if virtual_app.video_loader and virtual_app.video_loader.is_loaded else {},
            'face_detector': virtual_app.face_detector.get_stats() if virtual_app.face_detector else {},
            'effect_processor': virtual_app.effect_processor.get_stats() if virtual_app.effect_processor else {},
        }
        return jsonify(stats)
    
    @app.route('/api/effect/set', methods=['POST'])
    def set_effect():
        virtual_app = current_app.config.get('VIRTUAL_CAMERA_APP')
        if not virtual_app or not virtual_app.effect_processor:
            return jsonify({'error': 'Effect processor not available'}), 500
        data = request.get_json()
        effect = data.get('effect')
        if not effect:
            return jsonify({'error': 'No effect specified'}), 400
        if not virtual_app.effect_processor.set_current_effect(effect):
            return jsonify({'error': f'Unknown effect: {effect}'}), 400
        return jsonify({'success': True, 'message': f'Effect changed to: {effect}'})
    
    @app.route('/api/effect/list', methods=['GET'])
    def list_effects():
        virtual_app = current_app.config.get('VIRTUAL_CAMERA_APP')
        if not virtual_app or not virtual_app.effect_processor:
            return jsonify({'error': 'Effect processor not available'}), 500
        effects = virtual_app.effect_processor.get_available_effects()
        return jsonify({'effects': effects})
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
