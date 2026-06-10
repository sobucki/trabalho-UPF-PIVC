def get_app_stylesheet() -> str:
    return """
    QWidget {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    QGroupBox {
        font-weight: bold;
        margin-top: 2ex;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 3px;
    }
    """

def get_processing_view_style() -> str:
    return "background-color: #f0f0f0; border: 1px solid #cccccc; border-radius: 4px;"

def get_processing_card_style() -> str:
    return "background-color: #ffffff; border: 1px solid #dddddd; border-radius: 4px;"

def get_processing_title_style() -> str:
    return "font-weight: bold; font-size: 14px;"

def get_processing_description_style() -> str:
    return "color: #666666; font-size: 11px;"

def get_roi_style() -> str:
    return """
        QFrame {
            border: 2px dashed #4caf50;
            background-color: transparent;
        }
    """

def get_roi_label_style() -> str:
    return "color: #4caf50; font-size: 10px; border: none;"

def get_recognition_title_style() -> str:
    return "color: #555555; font-size: 12px;"

def get_recognition_value_style() -> str:
    return "font-size: 16px; font-weight: bold;"

def get_status_label_style(status: str) -> str:
    if status == "ATIVO" or status == "COMANDO EXECUTADO":
        return "color: green; font-weight: bold;"
    elif status == "ERRO DE CÂMERA" or status == "SEM MÃO DETECTADA":
        return "color: red; font-weight: bold;"
    elif status == "AGUARDANDO":
        return "color: orange; font-weight: bold;"
    elif status == "COOLDOWN":
        return "color: blue; font-weight: bold;"
    else:
        # PARADO ou default
        return "color: gray; font-weight: bold;"
