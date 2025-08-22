# backend/agents/case_generator.py (parte actualizada)
def generate_soap_envelope(operation, body_content, soap_action=None):
    """Generar envoltorio SOAP básico"""
    # Crear el elemento raíz
    envelope = ET.Element('soap:Envelope')
    envelope.set('xmlns:soap', 'http://schemas.xmlsoap.org/soap/envelope/')
    envelope.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    envelope.set('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema')
    
    # Crear el cuerpo
    body = ET.SubElement(envelope, 'soap:Body')
    
    # Crear el elemento de operación
    operation_elem = ET.SubElement(body, operation)
    operation_elem.set('xmlns', 'http://tempuri.org/')
    
    # Si body_content es un string XML, parsearlo y agregar los elementos
    if isinstance(body_content, str) and body_content.strip().startswith('<'):
        try:
            # Parsear el contenido XML
            # Usamos un wrapper temporal para manejar múltiples elementos raíz
            wrapped_content = f"<root>{body_content}</root>"
            temp_root = ET.fromstring(wrapped_content)
            
            # Agregar todos los hijos al elemento de operación
            for child in temp_root:
                operation_elem.append(child)
                
        except ET.ParseError:
            # Si falla el parsing, agregar como texto
            operation_elem.text = body_content
    else:
        # Si no es XML, agregar como texto
        operation_elem.text = str(body_content)
    
    # Convertir a string XML formateado
    rough_string = ET.tostring(envelope, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    
    # Retornar el string XML directamente, no el objeto minidom
    return reparsed.toprettyxml(indent="  ")