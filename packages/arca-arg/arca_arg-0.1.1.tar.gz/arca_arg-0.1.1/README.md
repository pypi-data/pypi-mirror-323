# Cliente de Servicios Web de ARCA

Cliente en Python para acceder a los servicios web de ARCA (Administración Federal de Ingresos Públicos de Argentina). Maneja la autenticación y la comunicación con los servicios SOAP de ARCA.

# Características

- Gestión de tokens de autenticación
- Integración con servicios SOAP de ARCA
- Consultas de metodos y elementos
- Soporte para entornos de producción y prueba

## Requisitos

- Python 3.8+
- cryptography
- zeep
- Certificados de ARCA (prueba o producción)

## Instalación

```bash
pip install arca_arg
```
## Configuración


1. Configurar los ajustes en `settings.py`:
```
CUIT = "TU_CUIT_AQUI"
PROD = False  # True para producción
CERT_PATH = "carpeta con el certificado de arca"
PRIVATE_KEY_PATH = "Carpeta con el la clave privada"
TA_FILES_PATH="donde se guardaran temporalmente los token de acceso"
```
## Uso

```python
from arca_arg.wsService import ArcaWebService 
from arca_arg.settings import WSDL_CPE_HOM, WS_LIST

arca_service = ArcaWebService(WSDL_CPE_HOM, 'wscpe') # Instancia del servicio web
print(arca_service.listMethods()) # Lista de métodos del servicio inicializado
print(arca_service.methodHelp('aceptarEmisionDestinoDG')) # Ayuda con el método consultarProvincias del servicio web
print(arca_service.elementDetails('ns0:AceptarEmisionDestinoDGSolicitud'))
  
```

## Estructura del Proyecto
```
arca_arg/
├── arca_api/
│   ├── auth.py
│   ├── settings.py
│   ├── wsService.py
└── README.md
```
## Contribuir

### Cómo Contribuir

1. Hacer un fork del [repositorio](https://github.com/relopezbriega/arca_arg)
2. Crear una rama para tu funcionalidad  (`git checkout -b feature/amazing-feature`)
3. Confirmar tus cambios (`git commit -m 'Add some amazing feature'`)
4. Subir a la rama(`git push origin feature/amazing-feature`)
5. Abrir un Pull Request

### Directrices de Desarrollo

- Seguir la guía de estilo PEP 8
- Añadir pruebas unitarias para nuevas funcionalidades
- Actualizar la documentación según sea necesario
- Usar anotaciones de tipo para el nuevo código

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Soporte

### Reporte de Problemas

Por favor, incluye la siguiente información al reportar problemas:

- Descripción detallada del problema
- Pasos para reproducir
- Comportamiento esperado vs comportamiento actual
- Versión de Python y detalles del entorno

### Contacto

- GitHub Issues: [Crear nuevo issue](https://github.com/relopezbriega/arca_arg/issues)
- Email: relopezbriega@gmail.com
