import copy
import json
import os
from datetime import datetime

import requests
from flask import current_app


class ModelService:
    LEGACY_MODEL_ID_ALIASES = {
        "openai:project-edge": "openai:qwen3-vl:8b",
    }
    LEGACY_MODEL_NAME_ALIASES = {
        "project-edge": "qwen3-vl:8b",
    }

    @staticmethod
    def _settings_file():
        return current_app.config.get("MODEL_SETTINGS_FILE")

    @staticmethod
    def _catalog():
        return [dict(item) for item in current_app.config.get("MODEL_CATALOG", [])]

    @staticmethod
    def _default_provider_config():
        return copy.deepcopy(current_app.config.get("DEFAULT_PROVIDER_CONFIG", {}))

    @classmethod
    def _default_settings(cls):
        return {
            "active_model_id": current_app.config.get("DEFAULT_MODEL_ID"),
            "provider_config": cls._default_provider_config(),
            "runtime_models": [],
            "remote_fetch": {
                "status": "idle",
                "message": "",
                "fetched_at": "",
                "provider": cls._default_provider_config().get("provider", ""),
            },
            "connection_test": {
                "status": "idle",
                "message": "",
                "tested_at": "",
            },
        }

    @classmethod
    def _load_settings(cls):
        data = cls._default_settings()
        settings_file = cls._settings_file()
        if settings_file and os.path.exists(settings_file):
            try:
                with open(settings_file, "r", encoding="utf-8") as fh:
                    raw = json.load(fh)
                if isinstance(raw, dict):
                    data.update({k: v for k, v in raw.items() if k in data})
                    if isinstance(raw.get("provider_config"), dict):
                        provider_config = cls._default_provider_config()
                        provider_config.update(raw["provider_config"])
                        default_cfg = current_app.config.get("DEFAULT_PROVIDER_CONFIG") or {}
                        if not (provider_config.get("base_url") or "").strip():
                            provider_config["base_url"] = default_cfg.get("base_url") or ""
                        if not cls._normalize_manual_models(provider_config.get("manual_models")):
                            provider_config["manual_models"] = list(default_cfg.get("manual_models") or []) or ([default_cfg.get("preferred_model")] if default_cfg.get("preferred_model") else [])
                        data["provider_config"] = provider_config
                    if isinstance(raw.get("remote_fetch"), dict):
                        remote_fetch = data["remote_fetch"]
                        remote_fetch.update(raw["remote_fetch"])
                        data["remote_fetch"] = remote_fetch
                    if isinstance(raw.get("connection_test"), dict):
                        connection_test = data["connection_test"]
                        connection_test.update(raw["connection_test"])
                        data["connection_test"] = connection_test
                    if not isinstance(raw.get("runtime_models"), list):
                        data["runtime_models"] = []
            except Exception as exc:
                print(f"Load model settings failed: {exc}")
        cls._apply_legacy_aliases(data)
        return data

    @classmethod
    def _apply_legacy_aliases(cls, data):
        active_model_id = data.get("active_model_id")
        if active_model_id in cls.LEGACY_MODEL_ID_ALIASES:
            data["active_model_id"] = cls.LEGACY_MODEL_ID_ALIASES[active_model_id]

        provider_config = data.get("provider_config", {})
        preferred_model = provider_config.get("preferred_model")
        if preferred_model in cls.LEGACY_MODEL_NAME_ALIASES:
            provider_config["preferred_model"] = cls.LEGACY_MODEL_NAME_ALIASES[preferred_model]
        manual_models = provider_config.get("manual_models")
        if isinstance(manual_models, list):
            provider_config["manual_models"] = [
                cls.LEGACY_MODEL_NAME_ALIASES.get(str(item).strip(), str(item).strip())
                for item in manual_models
                if str(item).strip()
            ]
        elif preferred_model:
            provider_config["manual_models"] = [provider_config["preferred_model"]]
        else:
            provider_config["manual_models"] = []

    @staticmethod
    def _normalize_manual_models(models):
        if not isinstance(models, list):
            return []

        normalized = []
        seen = set()
        for item in models:
            model_name = str(item).strip()
            if not model_name or model_name in seen:
                continue
            seen.add(model_name)
            normalized.append(model_name)
        return normalized

    @classmethod
    def _save_settings(cls, data):
        settings_file = cls._settings_file()
        if not settings_file:
            return

        with open(settings_file, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)

    @staticmethod
    def _utc_now():
        return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    @classmethod
    def get_provider_config(cls):
        return copy.deepcopy(cls._load_settings().get("provider_config", {}))

    @classmethod
    def get_runtime_models(cls):
        return copy.deepcopy(cls._load_settings().get("runtime_models", []))

    @classmethod
    def get_remote_fetch_status(cls):
        return copy.deepcopy(cls._load_settings().get("remote_fetch", {}))

    @classmethod
    def get_connection_test_status(cls):
        return copy.deepcopy(cls._load_settings().get("connection_test", {}))

    @classmethod
    def save_runtime_settings(cls, provider_config=None, active_model_id=None, runtime_models=None):
        settings = cls._load_settings()
        if isinstance(provider_config, dict):
            merged_provider_config = cls._default_provider_config()
            merged_provider_config.update(settings.get("provider_config", {}))
            for k, v in provider_config.items():
                if v is None:
                    continue
                if k == "api_key":
                    continue
                if k == "base_url" and not (v and str(v).strip()):
                    continue
                if k == "manual_models":
                    merged_provider_config["manual_models"] = cls._normalize_manual_models(v) or merged_provider_config.get("manual_models") or []
                    continue
                merged_provider_config[k] = v
            if merged_provider_config.get("manual_models"):
                merged_provider_config["preferred_model"] = merged_provider_config["manual_models"][0]
            merged_provider_config.pop("api_key", None)
            settings["provider_config"] = merged_provider_config
        if active_model_id is not None:
            settings["active_model_id"] = active_model_id
        if runtime_models is not None:
            settings["runtime_models"] = runtime_models
        cls._save_settings(settings)
        return settings

    @classmethod
    def _normalize_model(cls, item, source="preset"):
        model = dict(item)
        provider = model.get("provider", "openai_compatible")
        base_url = model.get("base_url")
        api_key = model.get("api_key")

        if provider == "openai_compatible":
            provider_config = cls.get_provider_config()
            base_url = provider_config.get("base_url", base_url)
            api_key = provider_config.get("api_key", api_key)

        model["id"] = model.get("id") or f"{provider}:{model.get('model')}"
        model["label"] = model.get("label") or f"{provider} / {model.get('model')}"
        model["source"] = source
        model["base_url"] = base_url
        model["api_key"] = api_key
        return model

    @classmethod
    def _manual_model_entries(cls, provider_config):
        provider = (provider_config or {}).get("provider")
        manual_models = cls._normalize_manual_models((provider_config or {}).get("manual_models", []))
        if provider != "openai_compatible" or not manual_models:
            return []

        return [
            cls._normalize_model(
                {
                    "id": f"openai:{model_name}",
                    "label": f"OpenAI Compatible / {model_name}",
                    "provider": "openai_compatible",
                    "model": model_name,
                },
                source="manual",
            )
            for model_name in manual_models
        ]

    @classmethod
    def _fetch_ollama_models(cls):
        base_url = current_app.config.get("OLLAMA_BASE_URL")
        try:
            resp = requests.get(f"{base_url}/api/tags", timeout=5)
            resp.raise_for_status()
            data = resp.json()
            models = []
            for item in data.get("models", []):
                name = item.get("name")
                if not name:
                    continue
                models.append(
                    {
                        "id": f"ollama:{name}",
                        "label": f"Ollama / {name}",
                        "provider": "ollama",
                        "model": name,
                        "base_url": base_url,
                        "source": "dynamic_local",
                    }
                )
            return models
        except Exception as exc:
            print(f"Ollama Connection Error: {exc}")
            return []

    @staticmethod
    def _headers_for_provider(provider_config):
        headers = {"Content-Type": "application/json"}
        api_key = (provider_config or {}).get("api_key")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        return headers

    @staticmethod
    def _build_models_url(provider_config):
        base_url = (provider_config or {}).get("base_url", "").rstrip("/")
        provider = (provider_config or {}).get("provider")
        if provider == "ollama":
            return f"{base_url}/api/tags"
        return f"{base_url}/models"

    @classmethod
    def _fetch_remote_models(cls, provider_config):
        provider = (provider_config or {}).get("provider")
        if provider == "ollama":
            return cls._fetch_ollama_models()
        if provider != "openai_compatible":
            raise ValueError(f"Unsupported provider for refresh: {provider}")

        base_url = (provider_config or {}).get("base_url", "").rstrip("/")
        if not base_url:
            raise ValueError("base_url required")

        resp = requests.get(
            cls._build_models_url(provider_config),
            headers=cls._headers_for_provider(provider_config),
            timeout=20,
        )
        resp.raise_for_status()

        data = resp.json()
        remote_models = []
        for item in data.get("data", []):
            model_name = item.get("id")
            if not model_name:
                continue
            remote_models.append(
                {
                    "id": f"openai:{model_name}",
                    "label": f"OpenAI Compatible / {model_name}",
                    "provider": "openai_compatible",
                    "model": model_name,
                    "source": "remote",
                }
            )

        for item in data.get("models", []):
            if isinstance(item, str):
                model_name = item
            else:
                model_name = item.get("id") or item.get("name")
            if not model_name:
                continue
            remote_models.append(
                {
                    "id": f"openai:{model_name}",
                    "label": f"OpenAI Compatible / {model_name}",
                    "provider": "openai_compatible",
                    "model": model_name,
                    "source": "remote",
                }
            )

        unique_models = []
        seen_ids = set()
        for item in remote_models:
            if item["id"] in seen_ids:
                continue
            seen_ids.add(item["id"])
            unique_models.append(item)
        return unique_models

    @classmethod
    def list_models(cls):
        catalog = [cls._normalize_model(item, source="preset") for item in cls._catalog()]
        runtime_models = [cls._normalize_model(item, source=item.get("source", "remote")) for item in cls.get_runtime_models()]

        known_ids = {item["id"] for item in catalog}
        for item in runtime_models:
            if item["id"] not in known_ids:
                catalog.append(item)
                known_ids.add(item["id"])

        for manual_model_entry in cls._manual_model_entries(cls.get_provider_config()):
            if manual_model_entry["id"] not in known_ids:
                catalog.append(manual_model_entry)
                known_ids.add(manual_model_entry["id"])

        for item in cls._fetch_ollama_models():
            normalized = cls._normalize_model(item, source=item.get("source", "dynamic_local"))
            if normalized["id"] not in known_ids:
                catalog.append(normalized)
                known_ids.add(normalized["id"])

        active_model_id = cls._load_settings().get("active_model_id")
        for item in catalog:
            item["selected"] = item["id"] == active_model_id
            item["has_api_key"] = bool(item.get("api_key"))
        return catalog

    @classmethod
    def _resolve_model(cls, model_id=None):
        target_id = model_id or cls.get_active_model_id()
        models = cls.list_models()
        for item in models:
            if item["id"] == target_id:
                return item
        return models[0]

    @classmethod
    def get_active_model_id(cls):
        model_id = cls._load_settings().get("active_model_id")
        available_ids = {item["id"] for item in cls.list_models()}
        if model_id in available_ids:
            return model_id
        return current_app.config.get("DEFAULT_MODEL_ID")

    @classmethod
    def get_active_model(cls):
        return cls._resolve_model()

    @classmethod
    def save_active_model_id(cls, model_id):
        model = None
        for item in cls.list_models():
            if item["id"] == model_id:
                model = item
                break
        if not model:
            raise ValueError(f"Unknown model_id: {model_id}")

        settings = cls._load_settings()
        settings["active_model_id"] = model["id"]
        cls._save_settings(settings)
        return model

    @classmethod
    def refresh_remote_models(cls, provider_config=None):
        settings = cls._load_settings()
        current_provider_config = settings.get("provider_config", {})
        if isinstance(provider_config, dict):
            current_provider_config = dict(current_provider_config)
            current_provider_config.update({k: v for k, v in provider_config.items() if v is not None})
            settings["provider_config"] = current_provider_config

        runtime_models = cls._fetch_remote_models(current_provider_config)
        settings["runtime_models"] = runtime_models
        settings["remote_fetch"] = {
            "status": "success",
            "message": f"已获取 {len(runtime_models)} 个远端模型",
            "fetched_at": cls._utc_now(),
            "provider": current_provider_config.get("provider", ""),
        }
        cls._save_settings(settings)
        return {
            "models": cls.list_models(),
            "runtime_models": runtime_models,
            "remote_fetch": settings["remote_fetch"],
        }

    @classmethod
    def _get_model_by_id(cls, model_id):
        if not model_id:
            return None
        for item in cls.list_models():
            if item["id"] == model_id:
                return item
        return None

    @classmethod
    def _resolve_test_model_name(cls, provider_config=None, model_id=None):
        merged_provider = cls.get_provider_config()
        if isinstance(provider_config, dict):
            merged_provider.update({k: v for k, v in provider_config.items() if v is not None})

        model = cls._get_model_by_id(model_id)
        if model and model.get("provider") == merged_provider.get("provider"):
            return model.get("model")

        preferred_model = (merged_provider.get("preferred_model") or "").strip()
        if preferred_model:
            return preferred_model

        manual_models = cls._normalize_manual_models(merged_provider.get("manual_models", []))
        if manual_models:
            return manual_models[0]

        active_model = cls.get_active_model()
        if active_model and active_model.get("provider") == merged_provider.get("provider"):
            return active_model.get("model")
        return None

    @classmethod
    def _test_openai_compatible_connection(cls, provider_config, model_name):
        base_url = (provider_config or {}).get("base_url", "").rstrip("/")
        api_key = (provider_config or {}).get("api_key")
        if not base_url:
            raise ValueError("base_url required")
        if not api_key:
            raise ValueError("api_key required")
        if not model_name:
            raise ValueError("preferred_model or model_id required")

        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello!",
                }
            ],
            "stream": False,
        }
        resp = requests.post(
            f"{base_url}/chat/completions",
            headers=cls._headers_for_provider(provider_config),
            json=payload,
            timeout=15,
        )
        resp.raise_for_status()
        return resp

    @classmethod
    def test_provider_connection(cls, provider_config=None, model_id=None):
        settings = cls._load_settings()
        current_provider_config = dict(settings.get("provider_config", {}))
        if isinstance(provider_config, dict):
            current_provider_config.update({k: v for k, v in provider_config.items() if v is not None})
            settings["provider_config"] = current_provider_config

        provider = current_provider_config.get("provider")
        try:
            if provider == "openai_compatible":
                test_model_name = cls._resolve_test_model_name(current_provider_config, model_id=model_id)
                cls._test_openai_compatible_connection(current_provider_config, test_model_name)
                message = f"{provider} 连接正常，测试模型: {test_model_name}"
            else:
                resp = requests.get(
                    cls._build_models_url(current_provider_config),
                    headers=cls._headers_for_provider(current_provider_config),
                    timeout=10,
                )
                resp.raise_for_status()
                message = f"{provider} 连接正常"
            status = {
                "status": "success",
                "message": message,
                "tested_at": cls._utc_now(),
            }
        except Exception as exc:
            status = {
                "status": "error",
                "message": str(exc),
                "tested_at": cls._utc_now(),
            }

        settings["connection_test"] = status
        cls._save_settings(settings)
        return copy.deepcopy(status)

    @classmethod
    def get_model_config_payload(cls):
        provider_config = cls.get_provider_config()
        api_key = provider_config.get("api_key", "")
        default_cfg = current_app.config.get("DEFAULT_PROVIDER_CONFIG") or {}
        base_url = (provider_config.get("base_url") or "").strip() or default_cfg.get("base_url") or ""
        manual_models = cls._normalize_manual_models(provider_config.get("manual_models")) or default_cfg.get("manual_models") or []
        if not manual_models and default_cfg.get("preferred_model"):
            manual_models = [default_cfg["preferred_model"]]
        preferred_model = (provider_config.get("preferred_model") or "").strip() or (manual_models[0] if manual_models else default_cfg.get("preferred_model") or "")
        return {
            "active_model_id": cls.get_active_model_id(),
            "active_model": cls.get_active_model(),
            "provider_config": {
                "provider": provider_config.get("provider") or current_app.config.get("DEFAULT_PROVIDER"),
                "base_url": base_url,
                "api_key": "",
                "api_key_masked": cls.mask_api_key(api_key),
                "has_api_key": bool(api_key),
                "preferred_model": preferred_model,
                "manual_models": manual_models,
            },
            "models": cls.list_models(),
            "remote_fetch": cls.get_remote_fetch_status(),
            "connection_test": cls.get_connection_test_status(),
        }

    @staticmethod
    def mask_api_key(api_key):
        if not api_key:
            return ""
        if len(api_key) <= 8:
            return "*" * len(api_key)
        return f"{api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}"

    @classmethod
    def generate(cls, prompt, model_id=None, image_b64=None, system_prompt=None):
        model = cls._resolve_model(model_id)
        provider = model.get("provider")

        if provider == "ollama":
            return cls._generate_with_ollama(model, prompt, image_b64=image_b64, system_prompt=system_prompt)
        if provider == "openai_compatible":
            return cls._generate_with_openai_compatible(
                model,
                prompt,
                image_b64=image_b64,
                system_prompt=system_prompt,
            )
        return {
            "ok": False,
            "content": "",
            "error": f"Unsupported provider {provider}",
            "debug": {
                "provider": provider,
            },
        }

    @staticmethod
    def _mask_headers(headers):
        masked = {}
        for key, value in (headers or {}).items():
            if key.lower() == "authorization" and isinstance(value, str) and value.startswith("Bearer "):
                token = value[7:]
                masked[key] = f"Bearer {ModelService.mask_api_key(token)}"
            else:
                masked[key] = value
        return masked

    @staticmethod
    def _sanitize_debug_value(value):
        if isinstance(value, dict):
            sanitized = {}
            for key, item in value.items():
                if key == "url" and isinstance(item, str) and item.startswith("data:image/"):
                    prefix, _, base64_data = item.partition("base64,")
                    sanitized[key] = f"{prefix}base64,<omitted:{len(base64_data)} chars>"
                else:
                    sanitized[key] = ModelService._sanitize_debug_value(item)
            return sanitized
        if isinstance(value, list):
            return [ModelService._sanitize_debug_value(item) for item in value]
        return value

    @staticmethod
    def _response_preview(resp):
        try:
            body = resp.text
        except Exception:
            body = "<unreadable response body>"
        if len(body) > 4000:
            body = body[:4000] + "\n...<truncated>"
        return body

    @staticmethod
    def _debug_bundle(provider, request_url, request_headers, request_payload, resp=None, error=None):
        bundle = {
            "provider": provider,
            "request": {
                "method": "POST",
                "url": request_url,
                "headers": ModelService._mask_headers(request_headers),
                "json": ModelService._sanitize_debug_value(request_payload),
            },
        }
        if resp is not None:
            bundle["response"] = {
                "status_code": resp.status_code,
                "headers": {
                    "content-type": resp.headers.get("Content-Type", ""),
                },
                "body_preview": ModelService._response_preview(resp),
            }
        if error:
            bundle["error"] = str(error)
        return bundle

    @staticmethod
    def _generate_with_ollama(model, prompt, image_b64=None, system_prompt=None):
        request_url = f"{model['base_url']}/api/generate"
        payload = {
            "model": model["model"],
            "prompt": prompt,
            "stream": False,
        }
        if image_b64:
            payload["images"] = [image_b64]
        if system_prompt:
            payload["system"] = system_prompt

        headers = {"Content-Type": "application/json"}
        try:
            resp = requests.post(request_url, json=payload, headers=headers, timeout=120)
            if resp.status_code == 200:
                return {
                    "ok": True,
                    "content": resp.json().get("response", ""),
                    "error": "",
                    "debug": ModelService._debug_bundle("ollama", request_url, headers, payload, resp=resp),
                }
            return {
                "ok": False,
                "content": "",
                "error": resp.text,
                "debug": ModelService._debug_bundle("ollama", request_url, headers, payload, resp=resp),
            }
        except Exception as exc:
            return {
                "ok": False,
                "content": "",
                "error": str(exc),
                "debug": ModelService._debug_bundle("ollama", request_url, headers, payload, error=exc),
            }

    @staticmethod
    def _generate_with_openai_compatible(model, prompt, image_b64=None, system_prompt=None):
        if not model.get("base_url"):
            return {
                "ok": False,
                "content": "",
                "error": "Missing base_url for openai-compatible provider",
                "debug": {"provider": "openai_compatible"},
            }
        if not model.get("api_key"):
            return {
                "ok": False,
                "content": "",
                "error": "Missing api_key for openai-compatible provider",
                "debug": {"provider": "openai_compatible"},
            }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        user_content = []
        if prompt:
            user_content.append({"type": "text", "text": prompt})
        if image_b64:
            user_content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                }
            )
        if not user_content:
            user_content.append({"type": "text", "text": ""})

        messages.append({"role": "user", "content": user_content})

        headers = {
            "Authorization": f"Bearer {model['api_key']}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model["model"],
            "messages": messages,
            "stream": False,
        }
        request_url = f"{model['base_url'].rstrip('/')}/chat/completions"

        try:
            resp = requests.post(
                request_url,
                headers=headers,
                json=payload,
                timeout=120,
            )
            if resp.status_code != 200:
                return {
                    "ok": False,
                    "content": "",
                    "error": resp.text,
                    "debug": ModelService._debug_bundle("openai_compatible", request_url, headers, payload, resp=resp),
                }

            data = resp.json()
            choices = data.get("choices", [])
            if not choices:
                return {
                    "ok": False,
                    "content": "",
                    "error": "Empty completion response",
                    "debug": ModelService._debug_bundle("openai_compatible", request_url, headers, payload, resp=resp),
                }

            message = choices[0].get("message", {})
            content = message.get("content", "")
            if isinstance(content, list):
                text_parts = [
                    item.get("text", "")
                    for item in content
                    if isinstance(item, dict) and item.get("type") == "text"
                ]
                content = "\n".join(part for part in text_parts if part)
            return {
                "ok": True,
                "content": content,
                "error": "",
                "debug": ModelService._debug_bundle("openai_compatible", request_url, headers, payload, resp=resp),
            }
        except Exception as exc:
            return {
                "ok": False,
                "content": "",
                "error": str(exc),
                "debug": ModelService._debug_bundle("openai_compatible", request_url, headers, payload, error=exc),
            }
