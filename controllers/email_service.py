import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import logging

sender_email = 'chicos.comunicaciones@gmail.com'
password_sender_email = 'Chicostiend@#2019'
smtp_server = 'smtp.gmail.com'
port_server = 465


def verify_email(receiver_email):
    resp = requests.get('https://todolist.example.com/tasks/')

    if resp.status_code != 200:
        return False
    else:
        return True


def send_email(receiver_email, bodyHtml):
    message = MIMEMultipart("alternative")
    message["Subject"] = "¡Gracias por apuntarte a la aventura de jugar con las matemáticas!"
    message["From"] = sender_email
    message["To"] = receiver_email

    body = MIMEText(bodyHtml, 'html')

    message.attach(body)

    try:
        context = ssl.create_default_context()
        server = smtplib.SMTP_SSL(smtp_server, port_server, context=context)
        server.login(sender_email, password_sender_email)

        server.sendmail(sender_email, receiver_email, message.as_string())

    except Exception as error:
        print('Ha ocurrido un error al intentar enviar el correo electrónico a: {0}'
              .format(receiver_email))
        print(error)
        
        logging.warning('Ha ocurrido un error al intentar enviar el correo electrónico a: {0}'
              .format(receiver_email))
        logging.warning(error)

    finally:
        server.quit()


def get_message(cliente, institucion, grado, code):
    message = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email</title>
    <link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet">
</head>
<body>
    <div style="padding: 5px;">
        <div style="width: 80%; margin: 0 auto;">
            <table align="center" cellpadding="0" cellspacing="0" width="600" style="border-collapse: collapse;">
                <tr>
                    <td align="center" style="padding: 40px 0 30px 0;" colspan="2">
                        <img src="http://drive.google.com/uc?export=view&id=1wboxe8dcLpfAQYL0jT4qIgsvf9nAHniY" alt="Chicos" width="160" style="display: block;" />
                    </td>
                    <td></td>
                </tr>
                <tr>
                    <td style="text-align: justify; color: #6d726e; font-family: 'Roboto'; font-size: 15px;" colspan="2">
                        Hola <strong>{0}</strong>
                    </td>
                    <td></td>
                </tr>
                <tr>
                    <td style="text-align: justify; padding: 20px 0 0 0; color: #6d726e; font-family: 'Roboto'; font-size: 15px;" colspan="2">
                        Estamos muy entusiasmados de acompañarte a desarrollar y experimentar nuevas formas de aprendizaje dentro, 
                        pero también fuera, del entorno de educación formal.
                    </td>
                    <td></td>
                </tr>
                
                <tr>
                    <td style="text-align: justify; padding: 20px 0 0 0; color: #6d726e; font-family: 'Roboto'; font-size: 15px;" colspan="2">
                        Eres parte de la comunidad <strong>CHICOS</strong> y del {1}, queremos apoyarte en la 
                            implementación del <strong>KIT CHICOS MATEMATICAS</strong> {2}
                    </td>
                    <td></td>
                </tr>

                <tr>
                    <td style="text-align: justify; padding: 20px 0 10px 0; color: #6d726e; font-family: 'Roboto'; font-size: 15px;" colspan="2">
                        A continuación, te damos un enlace donde podrás descargar un archivo en PDF que contiene el cuaderno de <strong>PLANTILLAS</strong>, 
                        en el se proponen diversos patrones que invitan a tu niño o tu niña a explorar con espontaneidad los juegos y 
                        así disfrutar del aprendizaje de las matemáticas con los productos físicos del KIT.
                    </td>
                    <td></td>
                </tr>
                <tr>
                    <td align="center" style="padding: 40px 0 30px 0; color: #04a32a;" colspan="2">
                        <a style="background-color: #04a32a;color: white; padding: 15px 15px 15px 15px; border-radius: 1.25rem; text-decoration: none; font-size: 20px; margin-top: 15px;" href="https://chicosimagen.com/shop/plantilla/{3}">
                            DESCARGAR
                        </a>                            
                    </td>
                    <td></td>
                </tr>
                <tr>
                    <td align="center" style="padding: 20px 0 30px 0; color: #6d726e; font-family: 'Roboto'; font-size: 15px;" colspan="2">
                        Tienes 48 horas para poder descargar las <strong>PLANTILLAS</strong>.
                    </td>
                    <td></td>
                </tr>

                <tr>
                    <td style="padding: 0 0 0 0; color: #6d726e; font-family: 'Roboto'; font-size: 15px;" colspan="2">
                        Estamos impacientes porque nos escribas tus consultas o comentarios de la implementación del KIT.
                    </td>
                    <td></td>
                </tr>

                <tr>
                    <td style="padding: 10px 0 0 0; color: #6d726e; font-family: 'Roboto'; font-size: 15px;" colspan="2">
                        Un abrazo
                    </td>
                    <td></td>
                </tr>

                <tr>
                    <td style="padding: 2px 0 35px 0; color: #6d726e; font-family: 'Roboto'; font-size: 15px;" colspan="2">
                        Erick
                    </td>
                    <td></td>
                </tr>
                
                <tr style="color: #04a32a;">
                    <td tyle="color: #ffffff; ">
                        <p style="margin-bottom: 1px; margin-top: 1px; font-family: 'Roboto'; font-size: 10px;">9a Calle Poniente 3972, San Salvador</p>                    
                        <p style="margin-bottom: 1px; margin-top: 1px;">
                            <a style="text-decoration: none; color: #04a32a; font-family: 'Roboto'; font-size: 10px;" href="tel: +503 2235-3824">Tel: +503 2235-3824</a>
                        </p>
                        <p style="margin-bottom: 1px; margin-top: 1px;">
                            <a style="text-decoration: none; color: #04a32a; font-family: 'Roboto'; font-size: 10px;" href="tel: +503 2264-9463">Tel: +503 2264-9463</a>
                        </p>
                    </td>
                    <td width="25%">
                        <table border="0" cellpadding="0" cellspacing="0">
                            <tr>
                                <td>
                                    <a href="https://www.facebook.com/ChicosJuguetesEducativos">
                                        <img src="http://drive.google.com/uc?export=view&id=1LDh1OvZLW_IE-T5osNsq6hdP8rMIN-u1" alt="Twitter" width="38" height="38" style="display: block;" border="0" />
                                    </a>
                                </td>
                                <td style="font-size: 0; line-height: 0;" width="20">&nbsp;</td>
                                <td>
                                    <a href="https://instagram.com/chicosjugueteseducativos?igshid=10rk64rcdh4q">
                                        <img src="http://drive.google.com/uc?export=view&id=1jfumg_7-FaTrnp3cdfw25_0Traf2lMfB" alt="Instagram" width="38" height="38" style="display: block;" border="0" />
                                    </a>
                                </td>
                                <td style="font-size: 0; line-height: 0;" width="20">&nbsp;</td>
                                <td>
                                    <a href="https://www.youtube.com/channel/UCsUhT8nQFX-l6qC-xAk2IWA">
                                        <img src="http://drive.google.com/uc?export=view&id=1den2YbV3ntgt-oBTKtZhCThy3aZY2TMR" alt="Youtube" width="38" height="38" style="display: block;" border="0" />
                                    </a>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </div>
    </div>
</body>
</html>
    """.format(cliente, institucion, grado, code)

    return message
