import copy

# Theme Tokens
BACKGROUND = "#F6F8FA"
SURFACE = "#FFFFFF"
SURFACE_ALT = "#F3F6F4"
SURFACE_GREEN = "#EAF7EC"
BORDER = "#DDE3EA"
BORDER_GREEN = "#A8D8AF"
TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#667085"
TEXT_MUTED = "#98A2B3"
PRIMARY = "#2E9D3F"
PRIMARY_DARK = "#187A27"
PRIMARY_SOFT = "#E6FFFA"
SUCCESS = "#2E9D3F"
DANGER = "#D92D20"
WARNING = "#F59E0B"
INFO = "#2563EB"
NEUTRAL = "#667085"

def get_app_stylesheet() -> str:
    return f"""
    QWidget {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: {TEXT_PRIMARY};
    }}
    QMainWindow, QDialog {{
        background-color: {BACKGROUND};
    }}
    QGroupBox {{
        background-color: transparent;
        border: none;
        margin-top: 0px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0;
        color: {TEXT_PRIMARY};
        font-size: 14px;
        font-weight: bold;
    }}
    QPushButton {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 6px;
        padding: 6px 14px;
        color: {TEXT_PRIMARY};
        font-weight: 500;
    }}
    QPushButton:hover {{
        background-color: {SURFACE_ALT};
        border-color: {BORDER_GREEN};
    }}
    QPushButton:pressed {{
        background-color: {SURFACE_GREEN};
        border-color: {PRIMARY};
    }}
    QPushButton:disabled {{
        background-color: {BACKGROUND};
        color: {TEXT_MUTED};
        border-color: {BORDER};
    }}
    QPushButton:checked {{
        background-color: {SURFACE_GREEN};
        color: {PRIMARY_DARK};
        border: 1px solid {PRIMARY};
    }}
    
    QPushButton#primaryButton {{
        background-color: {PRIMARY};
        color: {SURFACE};
        border: 1px solid {PRIMARY_DARK};
    }}
    QPushButton#primaryButton:hover {{
        background-color: {PRIMARY_DARK};
    }}
    QPushButton#primaryButton:disabled {{
        background-color: {BORDER};
        color: {SURFACE};
        border: 1px solid {BORDER};
    }}
    
    QPushButton#dangerButton {{
        background-color: {SURFACE};
        color: {DANGER};
        border: 1px solid {BORDER};
    }}
    QPushButton#dangerButton:hover {{
        background-color: #FEF3F2;
        border-color: {DANGER};
    }}
    QPushButton#dangerButton:disabled {{
        background-color: {BACKGROUND};
        color: {TEXT_MUTED};
        border-color: {BORDER};
    }}
    
    QCheckBox {{
        color: {TEXT_PRIMARY};
        spacing: 8px;
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 1px solid {BORDER};
        background-color: {SURFACE};
    }}
    QCheckBox::indicator:checked {{
        background-color: {PRIMARY};
        border-color: {PRIMARY};
    }}
    QComboBox, QLineEdit {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 4px;
        padding: 6px 10px;
        color: {TEXT_PRIMARY};
    }}
    QComboBox:focus, QLineEdit:focus {{
        border-color: {PRIMARY};
    }}
    QTableWidget {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 6px;
        gridline-color: {BORDER};
        color: {TEXT_PRIMARY};
    }}
    QHeaderView::section {{
        background-color: {SURFACE_ALT};
        color: {TEXT_SECONDARY};
        padding: 6px;
        border: none;
        border-right: 1px solid {BORDER};
        border-bottom: 1px solid {BORDER};
        font-weight: bold;
    }}
    QMessageBox {{
        background-color: {BACKGROUND};
    }}
    """

def get_header_card_style() -> str:
    return f"background-color: {SURFACE}; border: 1px solid {BORDER}; border-radius: 8px;"

def get_header_icon_style() -> str:
    return f"background-color: {SURFACE_GREEN}; color: {PRIMARY}; border-radius: 20px; font-size: 20px; font-weight: bold;"

def get_header_title_style() -> str:
    return f"font-size: 20px; font-weight: 800; color: {TEXT_PRIMARY};"

def get_header_subtitle_style() -> str:
    return f"font-size: 13px; color: {TEXT_SECONDARY};"

def get_integration_card_style() -> str:
    return f"background-color: {SURFACE_ALT}; border: 1px solid {BORDER}; border-radius: 6px;"

def get_header_integration_style() -> str:
    return f"font-size: 13px; font-weight: 600; color: {TEXT_PRIMARY};"

def get_footer_bar_style() -> str:
    return f"background-color: {SURFACE}; border: 1px solid {BORDER}; border-radius: 8px;"

def get_processing_view_style() -> str:
    return f"background-color: {SURFACE}; border: 1px solid {BORDER}; border-radius: 12px;"

def get_processing_viewport_style() -> str:
    return f"background-color: {BACKGROUND}; border: 1px solid {BORDER}; border-radius: 8px;"

def get_processing_card_style() -> str:
    return f"background-color: {SURFACE}; border: 1px solid {BORDER}; border-radius: 8px;"

def get_processing_title_style() -> str:
    return f"color: {TEXT_PRIMARY}; font-weight: bold; font-size: 15px;"

def get_processing_description_style() -> str:
    return f"color: {TEXT_SECONDARY}; font-size: 12px;"

def get_roi_style() -> str:
    return f"""
        QFrame {{
            border: 2px dashed {PRIMARY};
            background-color: transparent;
            border-radius: 4px;
        }}
    """

def get_roi_label_style() -> str:
    return f"color: {PRIMARY}; font-size: 11px; font-weight: bold; background-color: {SURFACE}; padding: 2px; border-radius: 2px;"

def get_recognition_panel_style() -> str:
    return f"background-color: {SURFACE}; border: 1px solid {BORDER}; border-radius: 12px;"

def get_recognition_item_style() -> str:
    return f"border-bottom: 1px solid {BORDER};"

def get_recognition_icon_style() -> str:
    return f"color: {TEXT_MUTED}; font-size: 14px;"

def get_recognition_title_style() -> str:
    return f"color: {TEXT_SECONDARY}; font-size: 12px; font-weight: 600;"

def get_recognition_value_style() -> str:
    return f"color: {TEXT_PRIMARY}; font-size: 15px; font-weight: 700;"

def get_low_light_panel_style() -> str:
    return f"background-color: {SURFACE_ALT}; border: 1px solid {BORDER}; border-radius: 6px;"

def get_checkbox_inline_style() -> str:
    return "font-weight: 500;"

def get_status_label_style(status: str) -> str:
    return get_status_badge_style(status)

def get_status_badge_style(status: str) -> str:
    status_upper = status.upper()
    if status_upper in ["ATIVO", "COMANDO EXECUTADO", "SUCESSO"]:
        color = SUCCESS
        bg = SURFACE_GREEN
        border = PRIMARY_SOFT
    elif status_upper in ["ERRO DE CÂMERA", "SEM MÃO DETECTADA", "ERRO"]:
        color = DANGER
        bg = "#FEF3F2"
        border = "#FECDCA"
    elif status_upper in ["AGUARDANDO"]:
        color = WARNING
        bg = "#FFFAEB"
        border = "#FEF0C7"
    elif status_upper in ["COOLDOWN"]:
        color = INFO
        bg = "#EFF8FF"
        border = "#D1E9FF"
    else:
        color = NEUTRAL
        bg = BACKGROUND
        border = BORDER
        
    return f"""
        color: {color};
        font-size: 11px;
        font-weight: 800;
        background-color: {bg};
        border: 1px solid {border};
        border-radius: 10px;
        padding: 4px 8px;
    """

