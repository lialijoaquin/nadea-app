from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.utils import platform
from plyer import gps
import random
import time

KV = '''
MDBoxLayout:
    orientation: 'vertical'
    MDBottomNavigation:
        panel_color: 1, 1, 1, 1
        selected_color_background: 0, 0, 0, 0
        text_color_active: app.theme_cls.primary_color

        MDBottomNavigationItem:
            name: 'screen_monitor'
            text: 'Monitor'
            icon: 'heart-pulse'
            MDBoxLayout:
                orientation: 'vertical'
                padding: "20dp"
                spacing: "20dp"
                Widget:
                    size_hint_y: 0.1
                MDCard:
                    size_hint: None, None
                    size: "280dp", "280dp"
                    pos_hint: {"center_x": .5}
                    radius: [140]
                    elevation: 4
                    orientation: 'vertical'
                    padding: "40dp"
                    md_bg_color: 0.98, 0.98, 0.98, 1
                    MDIcon:
                        icon: "heart"
                        halign: "center"
                        font_size: "64sp"
                        theme_text_color: "Custom"
                        text_color: 1, 0, 0, 1
                    MDLabel:
                        id: label_ritmo
                        text: "--"
                        halign: "center"
                        font_style: "H1"
                        bold: True
                        theme_text_color: "Custom"
                        text_color: 0.2, 0.2, 0.2, 1
                    MDLabel:
                        text: "BPM"
                        halign: "center"
                        font_style: "Caption"
                        theme_text_color: "Secondary"
                MDLabel:
                    id: gps_status
                    text: "GPS: Inactivo"
                    halign: "center"
                    font_style: "Caption"
                    theme_text_color: "Hint"
                MDLabel:
                    id: status_label
                    text: "Sistema Listo"
                    halign: "center"
                    theme_text_color: "Secondary"
                    font_style: "Body1"
                    size_hint_y: None
                    height: "40dp"
                MDFloatingActionButton:
                    id: btn_start
                    icon: "play"
                    md_bg_color: app.theme_cls.primary_color
                    pos_hint: {"center_x": .5}
                    user_font_size: "32sp"
                    on_release: app.toggle_monitoring()
                Widget:
                    size_hint_y: 0.2

        MDBottomNavigationItem:
            name: 'screen_contacts'
            text: 'Contactos'
            icon: 'contacts'
            MDBoxLayout:
                orientation: 'vertical'
                padding: "30dp"
                spacing: "20dp"
                MDLabel:
                    text: "Agenda de Emergencia"
                    font_style: "H5"
                    halign: "center"
                    size_hint_y: None
                    height: "40dp"
                MDLabel:
                    text: "Numeros a notificar en caso de alerta:"
                    font_style: "Caption"
                    halign: "center"
                    theme_text_color: "Hint"
                MDTextField:
                    id: tel_1
                    hint_text: "Contacto Principal"
                    helper_text: "Ej: 1155554444"
                    icon_right: "numeric-1-box"
                    mode: "rectangle"
                    input_filter: "int"
                MDTextField:
                    id: tel_2
                    hint_text: "Contacto Secundario"
                    icon_right: "numeric-2-box"
                    mode: "rectangle"
                    input_filter: "int"
                MDTextField:
                    id: tel_3
                    hint_text: "Contacto Adicional"
                    icon_right: "medical-bag"
                    mode: "rectangle"
                    input_filter: "int"
                Widget:

        MDBottomNavigationItem:
            name: 'screen_profile'
            text: 'Perfil'
            icon: 'account-circle-outline'
            MDBoxLayout:
                orientation: 'vertical'
                padding: "30dp"
                spacing: "20dp"
                MDLabel:
                    text: "Ajustes de Usuario"
                    font_style: "H5"
                    halign: "center"
                    size_hint_y: None
                    height: "50dp"
                MDTextField:
                    id: input_nombre
                    hint_text: "Nombre del Usuario"
                    icon_right: "account"
                    mode: "rectangle"
                MDBoxLayout:
                    orientation: "horizontal"
                    size_hint_y: None
                    height: "50dp"
                    spacing: "20dp"
                    padding: [0, 10, 0, 0]
                    MDLabel:
                        text: "Modo Oscuro"
                        halign: "left"
                        valign: "center"
                    MDSwitch:
                        active: False
                        on_active: app.cambiar_tema(*args)
                Widget:
'''

class NadeaApp(MDApp):
    my_lat, my_lon = None, None

    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.is_monitoring = False
        self.simulation_event = None
        self.sms_cooldown = 0
        self.historial_alertas = []
        return Builder.load_string(KV)

    def cambiar_tema(self, checkbox, value):
        self.theme_cls.theme_style = "Dark" if value else "Light"

    def on_start(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.SEND_SMS,
                Permission.READ_SMS,
                Permission.ACCESS_FINE_LOCATION,
                Permission.ACCESS_COARSE_LOCATION
            ])

    def toggle_monitoring(self):
        if not self.is_monitoring:
            self.is_monitoring = True
            self.root.ids.btn_start.icon = "stop"
            self.root.ids.btn_start.md_bg_color = (1, 0.2, 0.2, 1)
            self.root.ids.status_label.text = "Vigilancia Activa"
            self.start_gps()
            self.simulation_event = Clock.schedule_interval(self.update_simulation, 1)
        else:
            self.is_monitoring = False
            self.root.ids.btn_start.icon = "play"
            self.root.ids.btn_start.md_bg_color = self.theme_cls.primary_color
            self.root.ids.status_label.text = "Pausado"
            self.root.ids.label_ritmo.text = "--"
            self.root.ids.gps_status.text = "GPS: Detenido"
            self.stop_gps()
            if self.simulation_event:
                self.simulation_event.cancel()

    def start_gps(self):
        try:
            gps.configure(on_location=self.on_location_update)
            gps.start(minTime=1000, minDistance=0)
            self.root.ids.gps_status.text = "Buscando satelites..."
        except:
            self.root.ids.gps_status.text = "GPS no disponible"

    def stop_gps(self):
        try:
            gps.stop()
        except:
            pass

    def on_location_update(self, **kwargs):
        self.my_lat = kwargs.get('lat')
        self.my_lon = kwargs.get('lon')
        self.root.ids.gps_status.text = f"GPS: OK ({self.my_lat:.4f}, {self.my_lon:.4f})"

    def update_simulation(self, dt):
        if self.sms_cooldown > 0:
            self.sms_cooldown -= 1
        bpm = random.randint(60, 95)
        if random.random() < 0.20:
            bpm = random.randint(125, 160)
            self.root.ids.status_label.text = "ATENCION: RITMO ALTO!"
            self.root.ids.status_label.theme_text_color = "Error"
            self.root.ids.label_ritmo.text_color = (1, 0, 0, 1)
            if self.sms_cooldown == 0:
                self.enviar_sms_multicontacto(bpm)
                self.sms_cooldown = 40
        else:
            self.root.ids.status_label.text = "Ritmo Normal"
            self.root.ids.status_label.theme_text_color = "Secondary"
            self.root.ids.label_ritmo.text_color = (0.2, 0.2, 0.2, 1)
        self.root.ids.label_ritmo.text = str(bpm)

    def enviar_sms_multicontacto(self, bpm):
        numeros = []
        t1 = self.root.ids.tel_1.text
        t2 = self.root.ids.tel_2.text
        t3 = self.root.ids.tel_3.text
        if t1: numeros.append(t1)
        if t2: numeros.append(t2)
        if t3: numeros.append(t3)
        if not numeros:
            self.root.ids.status_label.text = "Faltan Contactos!"
            return
        nombre_usuario = self.root.ids.input_nombre.text.strip() or "El usuario"
        if self.my_lat and self.my_lon:
            link_maps = f"http://maps.google.com/?q={self.my_lat},{self.my_lon}"
        else:
            link_maps = "Buscando GPS..."
        ahora = time.time()
        self.historial_alertas.append(ahora)
        self.historial_alertas = [t for t in self.historial_alertas if ahora - t <= 3600]
        cantidad = len(self.historial_alertas)
        mensaje = f"Atencion! {nombre_usuario} registra {bpm} BPM. Alertas(1h): {cantidad}. Ver mapa: {link_maps}"
        if platform == 'android':
            try:
                from jnius import autoclass
                SmsManager = autoclass('android.telephony.SmsManager')
                sms_manager = SmsManager.getDefault()
                enviados = 0
                for numero in numeros:
                    sms_manager.sendTextMessage(numero, None, mensaje, None, None)
                    enviados += 1
                self.root.ids.status_label.text = f"SMS a {enviados} contactos"
            except:
                self.root.ids.status_label.text = "Error al enviar"
        else:
            print(f"--- SIMULANDO ENVIO A: {numeros} ---\nMensaje: {mensaje}")
            self.root.ids.status_label.text = f"Simulado a {len(numeros)} nums"

if __name__ == "__main__":
    NadeaApp().run()