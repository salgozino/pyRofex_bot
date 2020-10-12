# pyRofex_bot

Código para empezar a conectarse al mercado de MATBA/ROFEX usando la librería [pyRofex](https://github.com/matbarofex/pyRofex) provista por Primary.

Para correr el ejemplo de challenge.py, se debe correr ingresando los argumentos ticker -u USER -p PASSWORD -a ACCOUNT
Este usuario, contraseña y cuenta son provistos por [REMARKETS](https://remarkets.primary.ventures)
Dicho Script se conectará al mercado, se subscribe al ticker específicado y envía una orden de compra por 1 contrato al precio de 1 centavo por debajo de la mayor punta compradora, o a 75.25 si no hay punta compradora.
