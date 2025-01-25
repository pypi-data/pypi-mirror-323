# sendmail-docx

Para enviar emails usando una plantilla docx.

## Installación

```sh
pip install sendmail-docx
```

## Dependencias
```sh
pip install python-docx python-dotenv mammoth
```

## Uso

```python
from sendmail_docx import enviar_correo_electronico
import os

def main():
    # Enviar un mail de prueba
    resultado = enviar_correo_electronico(
        template_path=os.path.join("tests", "templates", "plantilla-ejemplo.docx"),
        datos={"nombre": "John Doe", "saldo": "1.235,50 €"},
        asunto="Comunicación de saldo",
        destinatarios=["destinatario@mail.com"],
        cc=[],
        cco=[],
        adjuntos=['factura.pdf', 'images/logo.png']
    )

    print(f"{resultado=}")


if __name__ == '__main__':
    main()
```
