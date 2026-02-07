"""
Creator Engine - Content Generation Tools
Generates: websites, mobile apps, documents, images, video, audio
All creations encrypted locally, published only on user consent
"""

import asyncio
import json
import logging
import os
import subprocess
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from enum import Enum

import httpx
from jinja2 import Template

from ..config import get_settings
from ..utils.encryptor import DataEncryptor

logger = logging.getLogger(__name__)


class ContentType(Enum):
    WEBSITE = "website"
    MOBILE_APP = "mobile_app"
    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    CODE = "code"


@dataclass
class Creation:
    """Represents a creative work"""
    creation_id: str
    content_type: ContentType
    title: str
    content: Any
    metadata: Dict[str, Any]
    created_at: str
    encrypted_path: Optional[str] = None
    proof_hash: Optional[str] = None


class CreatorEngine:
    """
    Generates creative content across multiple mediums.
    All creations stored encrypted locally.
    """
    
    WEB_TEMPLATES = {
        "portfolio": {
            "html": """<!DOCTYPE html>
<html>
<head>
    <title>{{title}}</title>
    <style>{{style}}</style>
</head>
<body>
    <header><h1>{{title}}</h1></header>
    <main>{{content}}</main>
    <footer>Created by Pollen AI</footer>
</body>
</html>""",
            "css": """body { font-family: system-ui; max-width: 800px; margin: 0 auto; padding: 20px; }
header { border-bottom: 2px solid #333; margin-bottom: 20px; }
footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #ccc; color: #666; }"""
        },
        "landing": {
            "html": """<!DOCTYPE html>
<html>
<head>
    <title>{{title}}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>{{style}}</style>
</head>
<body>
    <section class="hero">
        <h1>{{title}}</h1>
        <p>{{subtitle}}</p>
        <button>{{cta}}</button>
    </section>
    <section class="content">{{content}}</section>
</body>
</html>""",
            "css": """.hero { text-align: center; padding: 80px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
.hero h1 { font-size: 3em; margin-bottom: 20px; }
.hero button { padding: 15px 30px; font-size: 1.2em; background: white; color: #667eea; border: none; border-radius: 5px; cursor: pointer; }
.content { max-width: 800px; margin: 40px auto; padding: 0 20px; }"""
        }
    }
    
    MOBILE_TEMPLATES = {
        "react_native": {
            "structure": {
                "App.js": "",
                "components/": {},
                "screens/": {},
                "assets/": {},
                "package.json": ""
            }
        },
        "flutter": {
            "structure": {
                "lib/main.dart": "",
                "lib/screens/": {},
                "lib/widgets/": {},
                "pubspec.yaml": ""
            }
        }
    }
    
    def __init__(self):
        self.settings = get_settings()
        self.encryptor = DataEncryptor()
        self.vault_path = Path(self.settings.VAULT_PATH)
        self.vault_path.mkdir(parents=True, exist_ok=True)
        self.creations: Dict[str, Creation] = {}
        
    async def initialize(self):
        """Initialize creator engine"""
        logger.info("🎨 Initializing Creator Engine")
        
        # Verify vault directory
        if not self.vault_path.exists():
            self.vault_path.mkdir(parents=True)
            
        logger.info("✅ Creator Engine initialized")
    
    async def generate_website(
        self,
        title: str,
        content: str,
        template: str = "portfolio",
        custom_style: Optional[str] = None
    ) -> Creation:
        """Generate HTML/CSS website"""
        if template not in self.WEB_TEMPLATES:
            template = "portfolio"
        
        tmpl = self.WEB_TEMPLATES[template]
        
        # Render HTML
        html_template = Template(tmpl["html"])
        html_content = html_template.render(
            title=title,
            content=content,
            style=custom_style or tmpl["css"]
        )
        
        creation = Creation(
            creation_id=f"web_{datetime.utcnow().timestamp()}",
            content_type=ContentType.WEBSITE,
            title=title,
            content={
                "html": html_content,
                "css": custom_style or tmpl["css"],
                "template": template
            },
            metadata={
                "template": template,
                "pages": 1,
                "word_count": len(content.split())
            },
            created_at=datetime.utcnow().isoformat()
        )
        
        # Encrypt and store
        await self._store_creation(creation)
        
        logger.info(f"🌐 Website created: {title}")
        return creation
    
    async def generate_mobile_app(
        self,
        name: str,
        platform: str = "react_native",
        screens: List[str] = None
    ) -> Creation:
        """Generate mobile app scaffold"""
        screens = screens or ["Home", "Profile", "Settings"]
        
        if platform == "react_native":
            content = self._generate_react_native_scaffold(name, screens)
        elif platform == "flutter":
            content = self._generate_flutter_scaffold(name, screens)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
        
        creation = Creation(
            creation_id=f"app_{datetime.utcnow().timestamp()}",
            content_type=ContentType.MOBILE_APP,
            title=name,
            content=content,
            metadata={
                "platform": platform,
                "screens": screens,
                "dependencies": ["navigation", "state_management"]
            },
            created_at=datetime.utcnow().isoformat()
        )
        
        await self._store_creation(creation)
        
        logger.info(f"📱 Mobile app created: {name} ({platform})")
        return creation
    
    def _generate_react_native_scaffold(self, name: str, screens: List[str]) -> Dict:
        """Generate React Native app structure"""
        screen_components = {}
        for screen in screens:
            screen_components[f"screens/{screen}.js"] = f"""import React from 'react';
import {{ View, Text, StyleSheet }} from 'react-native';

export default function {screen}Screen() {{
    return (
        <View style={styles.container}>
            <Text>{screen} Screen</Text>
        </View>
    );
}}

const styles = StyleSheet.create({{
    container: {{ flex: 1, justifyContent: 'center', alignItems: 'center' }}
}});"""
        
        return {
            "App.js": f"""import React from 'react';
import {{ NavigationContainer }} from '@react-navigation/native';
import {{ createStackNavigator }} from '@react-navigation/stack';
{chr(10).join([f"import {s}Screen from './screens/{s}';" for s in screens])}

const Stack = createStackNavigator();

export default function App() {{
    return (
        <NavigationContainer>
            <Stack.Navigator initialRouteName="{screens[0]}">
                {chr(10).join([f'<Stack.Screen name="{s}" component={{{s}Screen}} />' for s in screens])}
            </Stack.Navigator>
        </NavigationContainer>
    );
}}""",
            "screens": screen_components,
            "package.json": json.dumps({
                "name": name.lower().replace(" ", "-"),
                "version": "1.0.0",
                "dependencies": {
                    "react": "^18.2.0",
                    "react-native": "^0.73.0",
                    "@react-navigation/native": "^6.1.0",
                    "@react-navigation/stack": "^6.3.0"
                }
            }, indent=2)
        }
    
    def _generate_flutter_scaffold(self, name: str, screens: List[str]) -> Dict:
        """Generate Flutter app structure"""
        screen_widgets = {}
        for screen in screens:
            screen_widgets[f"lib/screens/{screen.lower()}_screen.dart"] = f"""import 'package:flutter/material.dart';

class {screen}Screen extends StatelessWidget {{
    const {screen}Screen({{Key? key}}) : super(key: key);

    @override
    Widget build(BuildContext context) {{
        return Scaffold(
            appBar: AppBar(title: const Text('{screen}')),
            body: const Center(child: Text('{screen} Screen')),
        );
    }}
}}"""
        
        return {
            "lib/main.dart": f"""import 'package:flutter/material.dart';
{chr(10).join([f"import 'screens/{s.lower()}_screen.dart';" for s in screens])}

void main() {{
    runApp(const MyApp());
}}

class MyApp extends StatelessWidget {{
    const MyApp({{Key? key}}) : super(key: key);

    @override
    Widget build(BuildContext context) {{
        return MaterialApp(
            title: '{name}',
            theme: ThemeData(primarySwatch: Colors.blue),
            home: const {screens[0]}Screen(),
        );
    }}
}}""",
            "screens": screen_widgets,
            "pubspec.yaml": f"""name: {name.lower().replace(' ', '_')}
description: Generated by Pollen AI
version: 1.0.0
environment:
    sdk: '>=3.0.0 <4.0.0'
dependencies:
    flutter:
        sdk: flutter
"""
        }
    
    async def generate_document(
        self,
        title: str,
        content: str,
        format: str = "pdf",
        style: str = "professional"
    ) -> Creation:
        """Generate document (PDF or Markdown)"""
        
        if format == "markdown":
            doc_content = f"""# {title}

Generated by Pollen AI on {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

---

{content}

---
*Created with Pollen - Sovereign AI Agent*
"""
        elif format == "html":
            doc_content = f"""<!DOCTYPE html>
<html>
<head><title>{title}</title></head>
<body>
<h1>{title}</h1>
{content}
</body>
</html>"""
        else:
            doc_content = content
        
        creation = Creation(
            creation_id=f"doc_{datetime.utcnow().timestamp()}",
            content_type=ContentType.DOCUMENT,
            title=title,
            content={
                "body": doc_content,
                "format": format
            },
            metadata={
                "format": format,
                "style": style,
                "word_count": len(content.split())
            },
            created_at=datetime.utcnow().isoformat()
        )
        
        await self._store_creation(creation)
        
        logger.info(f"📄 Document created: {title}.{format}")
        return creation
    
    async def generate_image(
        self,
        prompt: str,
        style: str = "photorealistic",
        size: str = "1024x1024"
    ) -> Creation:
        """Generate image using Stable Diffusion"""
        # In production, this would call SD API
        # For now, create metadata and placeholder
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.settings.SD_API_URL}/sdapi/v1/txt2img",
                    json={
                        "prompt": f"{prompt}, {style}",
                        "steps": 30,
                        "width": 1024,
                        "height": 1024
                    },
                    timeout=120.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    image_data = result.get("images", [None])[0]
                else:
                    image_data = None
                    
        except Exception as e:
            logger.warning(f"SD API unavailable: {e}")
            image_data = None
        
        creation = Creation(
            creation_id=f"img_{datetime.utcnow().timestamp()}",
            content_type=ContentType.IMAGE,
            title=f"Image: {prompt[:50]}...",
            content={
                "prompt": prompt,
                "style": style,
                "size": size,
                "image_data": image_data,  # Base64 encoded
                "source": "stable_diffusion" if image_data else "placeholder"
            },
            metadata={
                "prompt": prompt,
                "style": style,
                "size": size
            },
            created_at=datetime.utcnow().isoformat()
        )
        
        await self._store_creation(creation)
        
        logger.info(f"🖼️ Image generated: {prompt[:50]}...")
        return creation
    
    async def generate_code(
        self,
        description: str,
        language: str,
        context: Optional[str] = None
    ) -> Creation:
        """Generate code snippet or module"""
        # Code generation would use LLM in production
        # For now, create structured placeholder
        
        creation = Creation(
            creation_id=f"code_{datetime.utcnow().timestamp()}",
            content_type=ContentType.CODE,
            title=f"{language.upper()}: {description[:40]}",
            content={
                "description": description,
                "language": language,
                "context": context,
                "code": f"# TODO: Generate {language} code for: {description}\n# Context: {context}\n",
                "tests": f"# Tests for {description}\n"
            },
            metadata={
                "language": language,
                "lines_of_code": 0,
                "complexity": "medium"
            },
            created_at=datetime.utcnow().isoformat()
        )
        
        await self._store_creation(creation)
        
        logger.info(f"💻 Code module created: {language} - {description[:40]}")
        return creation
    
    async def generate_frequency_composition(
        self,
        frequencies: List[float],
        duration: int,
        waveform: str = "sine"
    ) -> Creation:
        """Generate audio frequency composition"""
        # Audio generation using FFmpeg
        
        creation = Creation(
            creation_id=f"audio_{datetime.utcnow().timestamp()}",
            content_type=ContentType.AUDIO,
            title=f"Frequency Composition: {', '.join(map(str, frequencies))}Hz",
            content={
                "frequencies": frequencies,
                "duration": duration,
                "waveform": waveform,
                "format": "wav",
                # In production, would generate actual audio file
                "generation_command": f"ffmpeg -f lavfi -i 'sine=frequency={frequencies[0]}:duration={duration}' output.wav"
            },
            metadata={
                "frequencies": frequencies,
                "duration": duration,
                "waveform": waveform
            },
            created_at=datetime.utcnow().isoformat()
        )
        
        await self._store_creation(creation)
        
        logger.info(f"🎵 Frequency composition created: {frequencies}Hz")
        return creation
    
    async def _store_creation(self, creation: Creation):
        """Encrypt and store creation in vault"""
        # Serialize creation
        creation_data = json.dumps({
            "creation_id": creation.creation_id,
            "content_type": creation.content_type.value,
            "title": creation.title,
            "content": creation.content,
            "metadata": creation.metadata,
            "created_at": creation.created_at
        }, default=str)
        
        # Encrypt
        encrypted = self.encryptor.encrypt(creation_data)
        
        # Store
        filepath = self.vault_path / f"{creation.creation_id}.enc"
        filepath.write_text(encrypted)
        
        # Update creation with path and hash
        creation.encrypted_path = str(filepath)
        creation.proof_hash = self.encryptor.hash_data(creation_data)
        
        # Track in memory
        self.creations[creation.creation_id] = creation
        
        logger.debug(f"Creation stored: {creation.creation_id}")
    
    async def get_creation(self, creation_id: str) -> Optional[Creation]:
        """Retrieve and decrypt creation"""
        if creation_id in self.creations:
            return self.creations[creation_id]
        
        # Try to load from disk
        filepath = self.vault_path / f"{creation_id}.enc"
        if filepath.exists():
            encrypted = filepath.read_text()
            decrypted = self.encryptor.decrypt(encrypted)
            data = json.loads(decrypted)
            
            creation = Creation(
                creation_id=data["creation_id"],
                content_type=ContentType(data["content_type"]),
                title=data["title"],
                content=data["content"],
                metadata=data["metadata"],
                created_at=data["created_at"],
                encrypted_path=str(filepath),
                proof_hash=self.encryptor.hash_data(decrypted)
            )
            
            self.creations[creation_id] = creation
            return creation
        
        return None
    
    async def list_creations(
        self,
        content_type: Optional[ContentType] = None
    ) -> List[Dict[str, Any]]:
        """List all creations with optional filtering"""
        results = []
        
        for creation in self.creations.values():
            if content_type and creation.content_type != content_type:
                continue
            
            results.append({
                "creation_id": creation.creation_id,
                "content_type": creation.content_type.value,
                "title": creation.title,
                "created_at": creation.created_at,
                "metadata": creation.metadata,
                "proof_hash": creation.proof_hash
            })
        
        return sorted(results, key=lambda x: x["created_at"], reverse=True)
    
    async def prepare_for_publish(
        self,
        creation_id: str
    ) -> Dict[str, Any]:
        """Prepare creation for user-approved publishing"""
        creation = await self.get_creation(creation_id)
        
        if not creation:
            raise ValueError(f"Creation not found: {creation_id}")
        
        return {
            "creation_id": creation.creation_id,
            "content_type": creation.content_type.value,
            "title": creation.title,
            "preview": self._generate_preview(creation),
            "metadata": creation.metadata,
            "proof_hash": creation.proof_hash,
            "ready_for_publish": True
        }
    
    def _generate_preview(self, creation: Creation) -> str:
        """Generate preview of creation for user review"""
        if creation.content_type == ContentType.WEBSITE:
            return creation.content.get("html", "")[:500] + "..."
        elif creation.content_type == ContentType.DOCUMENT:
            return creation.content.get("body", "")[:500] + "..."
        elif creation.content_type == ContentType.IMAGE:
            return f"Image: {creation.metadata.get('prompt', 'No preview available')}"
        else:
            return json.dumps(creation.metadata, indent=2)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get creator engine statistics"""
        type_counts = {}
        for creation in self.creations.values():
            ct = creation.content_type.value
            type_counts[ct] = type_counts.get(ct, 0) + 1
        
        return {
            "total_creations": len(self.creations),
            "by_type": type_counts,
            "vault_size_mb": sum(
                (self.vault_path / f).stat().st_size
                for f in os.listdir(self.vault_path)
                if f.endswith('.enc')
            ) / (1024 * 1024)
        }
