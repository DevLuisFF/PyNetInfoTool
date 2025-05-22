<h1 align="left">PyNetInfoTool</h1>

[![Python CI](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY/actions/workflows/ci.yml)

###

<p align="left">PyNetInfoTool es una herramienta de línea de comandos para obtener y registrar información detallada sobre la configuración de red de un sistema. Esta información incluye el hostname, direcciones IP asociadas, dirección IP externa, y detalles sobre las interfaces de red (IPv4, IPv6, MAC).</p>

###

<h2 align="left">Tecnologías</h2>

###

<div align="center">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" height="40" alt="python logo"  />
  <img width="12" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/git/git-original.svg" height="40" alt="git logo"  />
  <img width="12" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg" height="40" alt="github logo"  />
  <img width="12" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/vscode/vscode-original.svg" height="40" alt="vscode logo"  />
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

<h2 align="left">Contributing</h2>

###

<p align="left">Contributions are welcome! Please feel free to submit a pull request or open an issue.</p>

###

<h2 align="left">Development</h2>

###

<p align="left">This project uses Black for code formatting and Flake8 for linting.</p>

<p align="left">To format the code, run:</p>

```bash
black .
```

<p align="left">To check for linting issues, run:</p>

```bash
flake8 .
```

<p align="left">It's recommended to run these before committing changes.<br>
Make sure to install these tools first: <code>pip install black flake8</code> or by installing all dependencies from <code>requirements.txt</code>.</p>

###

<h2 align="left">Running Tests</h2>

###

<p align="left">To run the unit tests, execute the following command from the root directory:</p>

```bash
python -m unittest discover tests
```
<p align="left">Ensure you have installed all dependencies from <code>requirements.txt</code> first.</p>

###

<h2 align="left">CI/CD</h2>

###

<p align="left">This project uses GitHub Actions for Continuous Integration. The workflow is defined in <code>.github/workflows/ci.yml</code> and includes steps for linting with Flake8 and running unit tests with unittest on pushes and pull requests to the main branch.</p>

###
