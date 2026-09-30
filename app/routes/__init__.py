from flask import session

PUBLICO_PREFIXOS = ("/login", "/static/", "/uploads/", "/css/", "/js/", "/img/")


def guardar_form(session_key, dados):
    session[session_key] = dados


def recuperar_form(session_key):
    return session.pop(session_key, None)