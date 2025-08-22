# backend/agents/spec_parser.py
import os
import yaml
import json
import xml.etree.ElementTree as ET
from openapi_spec_validator import validate_spec
from xml.dom import minidom

def parse_spec(filepath):
    _, ext = os.path.splitext(filepath)
    
    # Verificar si es XML/WSDL primero
    if ext in ['.xml', '.wsdl']:
        return parse_soap_spec(filepath)
    
    # Para JSON/YAML (OpenAPI/Postman)
    with open(filepath, 'r', encoding='utf-8') as f:
        if ext == '.yaml' or ext == '.yml':
            spec = yaml.safe_load(f)
        elif ext == '.json':
            spec = json.load(f)
        else:
            raise ValueError("Formato no soportado: solo .json, .yaml, .yml, .xml, .wsdl")

    # Validar OpenAPI
    try:
        validate_spec(spec)
        return _parse_openapi(spec)
    except Exception:
        pass

    # Verificar Postman
    if "item" in spec and "info" in spec:
        return _parse_postman(spec)

    raise ValueError("No es un archivo OpenAPI, Postman o SOAP válido")

def parse_soap_spec(filepath):
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        
        # Namespace handling para WSDL
        namespaces = {
            'wsdl': 'http://schemas.xmlsoap.org/wsdl/',
            'soap': 'http://schemas.xmlsoap.org/wsdl/soap/',
            'xsd': 'http://www.w3.org/2001/XMLSchema'
        }
        
        # Detectar si es WSDL
        if root.tag.endswith('definitions') or any('definitions' in tag for tag in root.tag.split()):
            return parse_wsdl(root, namespaces, filepath)
        else:
            # Asumir que es un XML de ejemplo de solicitud SOAP
            return parse_soap_example(root, filepath)
            
    except ET.ParseError as e:
        raise ValueError(f"Error parsing XML: {str(e)}")

def parse_wsdl(root, namespaces, filepath):
    """Parsear archivo WSDL"""
    # Obtener nombre del servicio
    service_name = root.get('name', 'UnknownService')
    if not service_name:
        # Intentar obtener de forma diferente
        service_elem = root.find('wsdl:service', namespaces)
        if service_elem is not None:
            service_name = service_elem.get('name', 'UnknownService')
    
    # Obtener operaciones (métodos)
    endpoints = []
    for port_type in root.findall('wsdl:portType', namespaces) or []:
        for operation in port_type.findall('wsdl:operation', namespaces) or []:
            op_name = operation.get('name')
            if op_name:
                # Buscar documentación de la operación
                doc_elem = operation.find('wsdl:documentation', namespaces)
                summary = doc_elem.text if doc_elem is not None else f"SOAP Operation: {op_name}"
                
                # Buscar SOAP Action
                soap_action = None
                for binding in root.findall('wsdl:binding', namespaces) or []:
                    for op_binding in binding.findall('wsdl:operation', namespaces) or []:
                        if op_binding.get('name') == op_name:
                            soap_action_elem = op_binding.find('soap:operation', namespaces)
                            if soap_action_elem is not None:
                                soap_action = soap_action_elem.get('soapAction')
                                break
                
                endpoints.append({
                    'method': 'POST',  # SOAP siempre usa POST
                    'path': op_name,
                    'summary': summary,
                    'soap_action': soap_action,
                    'type': 'SOAP'
                })
    
    if not endpoints:
        # Si no encontramos operaciones, intentar método alternativo
        for binding in root.findall('wsdl:binding', namespaces) or []:
            for operation in binding.findall('wsdl:operation', namespaces) or []:
                op_name = operation.get('name')
                if op_name:
                    endpoints.append({
                        'method': 'POST',
                        'path': op_name,
                        'summary': f"SOAP Operation: {op_name}",
                        'soap_action': None,
                        'type': 'SOAP'
                    })
    
    return {
        'title': service_name,
        'version': '1.0',
        'type': 'SOAP',
        'endpoints': endpoints,
        'raw_spec': prettify_xml(root)
    }

def parse_soap_example(root, filepath):
    """Parsear un ejemplo de mensaje SOAP"""
    # Buscar la operación en el cuerpo SOAP
    namespaces = {'soap': 'http://schemas.xmlsoap.org/soap/envelope/'}
    body = root.find('.//soap:Body', namespaces)
    if body is None:
        # Intentar sin namespace
        body = root.find('.//Body')
    
    operation_name = "UnknownOperation"
    if body is not None and len(body) > 0:
        operation_element = body[0]
        operation_name = operation_element.tag
        if '}' in operation_name:
            operation_name = operation_name.split('}')[1]  # Remover namespace
    
    return {
        'title': f"SOAP Operation from {os.path.basename(filepath)}",
        'version': '1.0',
        'type': 'SOAP',
        'endpoints': [{
            'method': 'POST',
            'path': operation_name,
            'summary': f"SOAP Operation: {operation_name}",
            'soap_action': None,
            'type': 'SOAP'
        }],
        'raw_spec': prettify_xml(root)
    }

def prettify_xml(elem):
    """Convertir elemento XML a string formateado"""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def _parse_openapi(spec):
    paths = spec.get('paths', {})
    endpoints = []

    for path, methods in paths.items():
        for method, details in methods.items():
            if method in ['get', 'post', 'put', 'delete', 'patch']:
                endpoint = {
                    'method': method.upper(),
                    'path': path,
                    'summary': details.get('summary', 'Sin descripción'),
                    'parameters': details.get('parameters', []),
                    'requestBody': details.get('requestBody', {}),
                    'responses': details.get('responses', {}),
                    'type': 'REST'
                }
                endpoints.append(endpoint)

    return {
        "type": "openapi",
        "title": spec.get('info', {}).get('title', 'API'),
        "version": spec.get('info', {}).get('version', '1.0'),
        "endpoints": endpoints
    }

def _parse_postman(collection):
    endpoints = []
    
    def process_items(items):
        for item in items:
            if 'request' in item:
                req = item['request']
                url = req.get('url', {})
                if isinstance(url, dict):
                    path = url.get('raw', 'desconocido')
                    # Extraer path base si es una URL completa
                    if '://' in path:
                        from urllib.parse import urlparse
                        parsed = urlparse(path)
                        path = parsed.path
                else:
                    path = str(url)
                
                endpoint = {
                    'method': req.get('method', 'GET'),
                    'path': path,
                    'summary': item.get('name', 'Sin nombre'),
                    'parameters': req.get('url', {}).get('query', []),
                    'requestBody': req.get('body', {}),
                    'responses': item.get('response', []),
                    'type': 'REST'
                }
                endpoints.append(endpoint)
            elif 'item' in item:  # Carpetas
                process_items(item['item'])
    
    process_items(collection.get('item', []))
    
    return {
        "type": "postman",
        "title": collection.get('info', {}).get('name', 'Colección'),
        "version": "1.0",
        "endpoints": endpoints
    }