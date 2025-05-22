<h1 align="left">PyNetInfoTool</h1>

[![Integración Continua Python](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY/actions/workflows/ci.yml)

###

<p align="left">PyNetInfoTool es una herramienta de línea de comandos para obtener y registrar información detallada sobre la configuración de red de un sistema. Esta información incluye el hostname, direcciones IP asociadas, dirección IP externa, y detalles sobre las interfaces de red (IPv4, IPv6, MAC).</p>

###

<h2 align="left">Tecnologías</h2>

###

<div align="center">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" height="40" alt="logo de python"  />
  <img width="12" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/git/git-original.svg" height="40" alt="logo de git"  />
  <img width="12" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg" height="40" alt="logo de github"  />
  <img width="12" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/vscode/vscode-original.svg" height="40" alt="logo de vscode"  />
</div>

###

<h2 align="left">Funcionalidades:</h2>

###

<p align="left">-Mostrar el hostname del sistema y todas las direcciones IP asociadas.<br>-Obtener y mostrar la dirección IP pública del sistema.<br>-Proporcionar información detallada de las interfaces de red, incluyendo direcciones IPv4, IPv6 y MAC.<br>-Guardar toda la información obtenida en un archivo en el directorio `output/` para referencia futura.<br>-Interfaz de usuario interactiva que permite al usuario elegir entre diferentes opciones.</p>

###

<h2 align="left">Ejecución:</h2>

###

<p align="left">Para utilizar PyNetInfoTool, simplemente ejecute el script y siga las instrucciones del menú interactivo para mostrar la información en la consola o guardarla en un archivo.</p>

###

<p align="left">python src/netinfotool.py</p>

###

<h2 align="left">Requisitos:</h2>

###

<p align="left">Python 3.x<br>Bibliotecas psutil y requests<br><br>Para instalar las dependencias, ejecute:</p>

###

<p align="left">pip install -r requirements.txt</p>

###

<h2 align="left">Contribuciones</h2>

###

<p align="left">¡Las contribuciones son bienvenidas! No dude en enviar un pull request o abrir un issue.</p>

###

<h2 align="left">Desarrollo</h2>

###

<p align="left">Este proyecto utiliza Black para el formateo de código y Flake8 para el linting.</p>

<p align="left">Para formatear el código, ejecute:</p>

```bash
black .
```

<p align="left">Para verificar problemas de linting, ejecute:</p>

```bash
flake8 .
```

<p align="left">Se recomienda ejecutar estos comandos antes de confirmar los cambios (commit).<br>
Asegúrese de instalar primero estas herramientas: <code>pip install black flake8</code> o instalando todas las dependencias desde <code>requirements.txt</code>.</p>

###

<h2 align="left">Ejecución de Pruebas</h2>

###

<p align="left">Para ejecutar las pruebas unitarias, ejecute el siguiente comando desde el directorio raíz:</p>

```bash
python -m unittest discover tests
```
<p align="left">Asegúrese de haber instalado primero todas las dependencias desde <code>requirements.txt</code>.</p>

###

<h2 align="left">CI/CD (Integración Continua/Entrega Continua)</h2>

###

<p align="left">Este proyecto utiliza GitHub Actions para la Integración Continua. El flujo de trabajo está definido en <code>.github/workflows/ci.yml</code> e incluye pasos para el linting con Flake8 y la ejecución de pruebas unitarias con unittest en cada push y pull request a la rama principal (main).</p>

###
