import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import logging


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
                        Eres parte de la comunidad <strong>CHICOS</strong> y del <strong>{1}</strong>, queremos apoyarte en la 
                            implementación del <strong>KIT CHICOS MATEMATICAS {2}</strong>
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
                        <a style="background-color: #04a32a;color: white; padding: 15px 15px 15px 15px; border-radius: 1.25rem; text-decoration: none; font-size: 20px; margin-top: 15px;" href="https://chicosimagen.com/shop/plantilla/{3}" target="_blank">
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
                        Estamos impacientes porque nos escribas tus consultas o comentarios de la implementación del KIT al email <a href='mailto:chicos.comunicaciones@gmail.com'>chicos.comunicaciones@gmail.com</a>
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
                    <td></td>                    
                    <td colspan="2" >
                        <table border="0" cellpadding="0" cellspacing="0">
                            <tr>
                                <td>
                                    <a href="tel: +503 2235-3824">
                                        <img src="http://drive.google.com/uc?export=view&id=1GugeOZLhsMgk8L88Hgmk5nFBjX70P2n8" alt="Phone" width="38" height="38" style="display: block;" border="0" />
                                    </a>
                                </td>
                                <td style="font-size: 0; line-height: 0;" width="20">&nbsp;</td>
                                <td>
                                    <a href="https://goo.gl/maps/goiH78rvynovt3pV9">
                                        <img src="http://drive.google.com/uc?export=view&id=1oIfB02GqcQEMq61Mw0tjrDKb7zbcBO3h" alt="Location" width="38" height="38" style="display: block;" border="0" />
                                    </a>
                                </td>
                                <td style="font-size: 0; line-height: 0;" width="20">&nbsp;</td>
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
