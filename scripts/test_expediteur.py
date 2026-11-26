#!/usr/bin/env python3
"""26/11/2026 : vérifie si le Gmail de Deway peut envoyer au nom de contact@qosmi.be (alias « Envoyer en tant que »)."""
import os, re, smtplib
from email.message import EmailMessage
BOITE = "contact@deway.be"
msg = EmailMessage()
msg["From"] = "Qosmi <contact@qosmi.be>"
msg["To"] = BOITE
msg["Reply-To"] = "contact@qosmi.be"
msg["Subject"] = "Test expéditeur Qosmi (à ignorer)"
msg.set_content("Test technique : cet e-mail doit apparaître comme envoyé par contact@qosmi.be.")
with smtplib.SMTP("smtp.gmail.com", 587, timeout=60) as smtp:
    smtp.starttls()
    smtp.login(BOITE, re.sub(r"\s+", "", os.environ["GMAIL_APP_PASSWORD"]))
    smtp.send_message(msg)
print("envoyé")
