from flask import Blueprint, jsonify, request, current_app
from app.services.model_svc import ModelService
import os
import werkzeug

api_bp = Blueprint('api', __name__)

@api_bp.route('/status', methods=['GET'])
def system_status():
    active_model = ModelService.get_active_model()
    return jsonify({
        "status": "online",
        "model": active_model.get("model"),
        "model_id": active_model.get("id"),
        "model_label": active_model.get("label"),
    })

@api_bp.route('/models', methods=['GET'])
def list_models():
    models = ModelService.list_models()
    return jsonify({"models": models})

@api_bp.route('/model-config', methods=['GET'])
def get_model_config():
    return jsonify(ModelService.get_model_config_payload())

@api_bp.route('/model-config', methods=['POST'])
def update_model_config():
    data = request.get_json(silent=True) or {}
    provider_config = {
        "provider": data.get("provider"),
        "base_url": data.get("base_url"),
        "api_key": data.get("api_key"),
        "preferred_model": data.get("preferred_model"),
        "manual_models": data.get("manual_models"),
    }
    ModelService.save_runtime_settings(provider_config=provider_config)

    model_id = data.get("model_id")
    if not model_id and provider_config.get("provider") == "openai_compatible":
        manual_models = provider_config.get("manual_models") or []
        if manual_models:
            model_id = f"openai:{str(manual_models[0]).strip()}"
        elif provider_config.get("preferred_model"):
            model_id = f"openai:{provider_config.get('preferred_model').strip()}"
    if model_id:
        try:
            ModelService.save_active_model_id(model_id)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    payload = ModelService.get_model_config_payload()
    payload["status"] = "success"
    return jsonify(payload)

@api_bp.route('/model-config/refresh', methods=['POST'])
def refresh_model_config():
    data = request.get_json(silent=True) or {}
    provider_config = {
        "provider": data.get("provider"),
        "base_url": data.get("base_url"),
        "api_key": data.get("api_key"),
        "preferred_model": data.get("preferred_model"),
        "manual_models": data.get("manual_models"),
    }
    try:
        refresh_result = ModelService.refresh_remote_models(provider_config=provider_config)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

    payload = ModelService.get_model_config_payload()
    payload["status"] = "success"
    payload["remote_fetch"] = refresh_result.get("remote_fetch", payload.get("remote_fetch"))
    return jsonify(payload)

@api_bp.route('/model-config/test', methods=['POST'])
def test_model_provider():
    data = request.get_json(silent=True) or {}
    provider_config = {
        "provider": data.get("provider"),
        "base_url": data.get("base_url"),
        "api_key": data.get("api_key"),
        "preferred_model": data.get("preferred_model"),
        "manual_models": data.get("manual_models"),
    }
    test_result = ModelService.test_provider_connection(
        provider_config=provider_config,
        model_id=data.get("model_id"),
    )
    status_code = 200 if test_result.get("status") == "success" else 400
    return jsonify(test_result), status_code

@api_bp.route('/analyze', methods=['POST'])
def analyze_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    mode = request.form.get('mode', 'detection')
    model_id = request.form.get('model_id')
    
    # Save file temporarily
    filename = werkzeug.utils.secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Process with Ollama
    # Convert to base64 for internal logic? 
    # Actually OllamaService expects path or base64. Let's modify OllamaService to handle path if needed or just read it.
    
    system_prompt = "你是一个专注智慧农牧领域的视觉分析助手，请严格按照要求输出结果。"
    if mode == 'detection':
        # Load targets dynamically
        target_file = current_app.config['TARGETS_FILE']
        target_list = ["Person", "Car", "Pig", "Rat", "Bird", "Cat", "Dog", "Chicken"] # Fallback
        
        if os.path.exists(target_file):
            try:
                import json
                with open(target_file, 'r', encoding='utf-8') as f:
                    targets_data = json.load(f)
                    # Use label_cn if available for better understanding by Chinese users/model, or name
                    # Combining them might be best: "Person(人员)"
                    target_list = [t['name'] for t in targets_data]
            except Exception as e:
                print(f"Error loading targets: {e}")

        targets_str = ", ".join(target_list)
        user_query = f"""请检测图中是否存在以下目标：{targets_str}。
仅输出 JSON 数组。每个元素包含字段: "label", "bbox_2d", "confidence"。
"bbox_2d" 格式为 [xmin, ymin, xmax, ymax]，坐标使用 0-1000 归一化整数。
如果没有检测到目标，请输出 []。"""
    else:
        # Review mode
        event_info = request.form.get('event_info', 'Unknown Event')
        user_query = f"""用户上报的事件为："{event_info}"。
请仔细分析图片，判断该事件是否成立。
仅输出一个 JSON 对象，字段包括：
"status": "复核正确" 或 "复核错误"
"reason": 简短说明判断依据
"confidence": 0.0 到 1.0 之间的分数"""
        
    # Read file and encode
    import base64
    with open(filepath, "rb") as image_file:
        image_b64 = base64.b64encode(image_file.read()).decode('utf-8')
        
    result = ModelService.generate(
        user_query,
        model_id=model_id,
        image_b64=image_b64,
        system_prompt=system_prompt,
    )

    if not result.get("ok"):
        return jsonify({
            "status": "error",
            "message": "Analyze failed",
            "error": result.get("error", "Unknown model error"),
            "data": result.get("content", ""),
            "debug": result.get("debug", {}),
        }), 502

    return jsonify({
        "status": "success",
        "message": "Analyzed",
        "data": result.get("content", ""),
        "debug": result.get("debug", {}),
    })

@api_bp.route('/targets', methods=['GET'])
def get_targets():
    target_file = current_app.config['TARGETS_FILE']
    if not os.path.exists(target_file):
        return jsonify([])
    import json
    with open(target_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

@api_bp.route('/targets', methods=['POST'])
def add_target():
    data = request.json
    name = data.get('name')
    if not name:
        return jsonify({"error": "Name required"}), 400
        
    target_file = current_app.config['TARGETS_FILE']
    import json
    
    current_targets = []
    if os.path.exists(target_file):
        with open(target_file, 'r', encoding='utf-8') as f:
            current_targets = json.load(f)
            
    # Check duplicate
    for t in current_targets:
        if t['name'] == name:
            return jsonify({"error": "Target already exists"}), 400
            
    new_target = {
        "name": name, 
        "type": "custom", 
        "label_cn": name # Default to same name if no translation provided
    }
    current_targets.append(new_target)
    
    with open(target_file, 'w', encoding='utf-8') as f:
        json.dump(current_targets, f, ensure_ascii=False, indent=2)
        
    return jsonify({"status": "success", "target": new_target})
