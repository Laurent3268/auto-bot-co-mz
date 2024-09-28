from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from threading import Thread
from selenium.webdriver.chrome.service import Service


      
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Variáveis Globais
entrada = True
green = False
gale1 = False
green_no_gale1 = False
gale2 = False
green_no_gale2 = False
loss = False
check_resultado_final = []
resultado_final = []

class SeleniumThread(Thread):
    def __init__(self, user, password):
        super().__init__()
        self.user = user
        self.password = password
        self.driver = None

    def run(self):
        socketio.emit('log_message', {'message': "Iniciando o bot de apostas automáticas..."})

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-logging")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-blink-features=AutomationControlled")

        # Adicione o caminho do ChromeDriver para ser otimizado no Vercel
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        try:
            # O resto do código permanece o mesmo

            # Handle exception
            self.driver.get('https://www.megagamelive.com/login')
            time.sleep(3)
            self.driver.find_element(By.XPATH, '//*[@id="username_l"]').send_keys(self.user)
            socketio.emit('log_message', {'message': "Usuário inserido."})
            self.driver.find_element(By.XPATH, '//*[@id="password_l"]').send_keys(self.password)
            socketio.emit('log_message', {'message': "Senha inserida."})
            self.driver.find_element(By.XPATH, '//*[@id="mainDiv"]/app-load/app-widget-host/app-block/app-widget-host/app-block[1]/app-widget-host/app-block[2]/app-widget-host/app-block/app-widget-host/app-block[1]/app-widget-host/app-login/app-login-form/form/ui-button/button').click()
            socketio.emit('log_message', {'message': "Iniciando login..."})
            time.sleep(5)

            self.driver.get('https://www.megagamelive.com/aviator')
            socketio.emit('log_message', {'message': "Acessando Aviator..."})
            WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.ID, 'lobby-iframe')))

            iframe = self.driver.find_element(By.ID, 'lobby-iframe')
            self.driver.switch_to.frame(iframe)
            socketio.emit('log_message', {'message': "Velas encontradas."})

            # Loop contínuo para atualização de resultado e aplicação da estratégia
            global resultado_final
            global check_resultado_final
            while True:
                try:
                    numero = self.obter_numero()
                    if numero:
                        resultado_final = self.processar_numero(numero)
                        if resultado_final != check_resultado_final:
                            check_resultado_final = resultado_final
                            self.estrategia(resultado_final)
                            socketio.emit('resultado', {'resultado': resultado_final})
                    time.sleep(1)  # Ajuste o intervalo conforme necessário
                except Exception as e:
                    socketio.emit('log_message', {'message': f"Erro no loop principal: {e}"})

        except Exception as e:
            socketio.emit('log_message', {'message': f"Erro ao acessar a página: {e}"})
            if self.driver:
                self.driver.quit()

    def obter_numero(self):
        try:
            numero_element = self.driver.find_element(By.XPATH, '/html/body/app-root/app-game/div/div[1]/div[2]/div/div[2]/div[1]/app-stats-widget/div/div[1]/div')
            numero = numero_element.text.strip()
            socketio.emit('log_message', {'message': f"Vela encontrada: {numero}"})
            return numero
        except Exception as e:
            socketio.emit('log_message', {'message': f"Erro ao obter a vela: {e}"})
            return None

    def processar_numero(self, numero):
        try:
            lista = numero.split()
            # Garantir que a lista tem pelo menos 12 elementos
            if len(lista) < 12:
                socketio.emit('log_message', {'message': "Não há resultados suficientes para processar."})
                return []
            resultado_final = [float(num.translate(str.maketrans('', '', 'x'))) for num in lista[0:12]]
            socketio.emit('log_message', {'message': f"Resultado processado: {resultado_final}"})
            return resultado_final
        except Exception as e:
            socketio.emit('log_message', {'message': f"Erro ao processar a vela: {e}"})
            return []

    def estrategia(self, resultado):
        global entrada, green, gale1, green_no_gale1, gale2, green_no_gale2, loss

        if resultado[0] < 5.0 and resultado[1] < 5.0 and resultado[2] < 5.0 and resultado[3] < 5.0 and entrada == True:
            socketio.emit('log_message', {'message': f"\nENTRADA APÓS VELA {resultado[0]}\n\nDUAS TENTATIVAS (OPCIONAL)\n\n Proteccao 2 a 5x\n\n888BETS Mr_BOT\n"})
            entrada = False
            green = True
            gale1 = True
            self.clicar_botao_1()

        elif resultado[0] >= 5.0 and resultado[1] < 5.0 and resultado[2] < 5.0 and resultado[3] < 5.0 and green == True:
            socketio.emit('log_message', {'message': "GREEN"})
            entrada = True
            green = False
            gale1 = False

        elif resultado[0] < 5.0 and resultado[1] < 5.0 and resultado[2] < 5.0 and resultado[3] < 5.0 and gale1 == True:
            socketio.emit('log_message', {'message': "VELA 1"})
            green = False
            gale1 = False
            green_no_gale1 = True
            gale2 = True
            self.clicar_botao_1()

        elif resultado[0] >= 5.0 and resultado[1] < 5.0 and resultado[2] < 5.0 and resultado[3] < 5.0 and green_no_gale1 == True:
            socketio.emit('log_message', {'message': "GREEN NA VELA 1"})
            entrada = True
            green_no_gale1 = False
            gale2 = False

        elif resultado[0] < 5.0 and resultado[1] < 5.0 and resultado[2] < 5.0 and resultado[3] < 5.0 and gale2 == True:
            socketio.emit('log_message', {'message': "VELA 2"})
            green_no_gale1 = False
            gale2 = False
            green_no_gale2 = True
            loss = True
            self.clicar_botao_1()

        elif resultado[0] >= 5.0 and resultado[1] < 5.0 and resultado[2] < 5.0 and resultado[3] < 5.0 and green_no_gale2 == True:
            socketio.emit('log_message', {'message': "GREEN NA VELA 2"})
            entrada = True
            green_no_gale2 = False
            loss = False

        elif resultado[0] < 5.0 and resultado[1] < 5.0 and resultado[2] < 5.0 and resultado[3] < 5.0 and loss == True:
            socketio.emit('log_message', {'message': "LOSS"})
            entrada = True
            green_no_gale2 = False
            loss = False
        
        # Nova estratégia
        if resultado[0] > 2.0 and resultado[1] > 3.0:
            socketio.emit('log_message', {'message': "Estratégia Encontrada: resultado[0] = 5.0 e resultado[1] > 2.0"})
            self.clicar_botao_2()
            
        elif resultado[0] ==1.0:
            socketio.emit('log_message', {'message': f"\nEstratégia 8X Confirmada {resultado[0]}\n\nDUAS TENTATIVAS (OPCIONAL)\n"})
            self.clicar_botao_2()
            
        elif resultado[0] ==1.06:
            socketio.emit('log_message', {'message': f"\nEstratégia 5X Confirmada {resultado[0]}\n\nDUAS TENTATIVAS (OPCIONAL)\n"})
            self.clicar_botao_2()
            
        elif resultado[0] ==1.12:
            socketio.emit('log_message', {'message': f"\nEstratégia 5X Confirmada {resultado[0]}\n\nDUAS TENTATIVAS (OPCIONAL)\n"})
            self.clicar_botao_2()
            
        elif resultado[0] ==1.02:
            socketio.emit('log_message', {'message': f"\nEstratégia 5X Confirmada {resultado[0]}\n\nDUAS TENTATIVAS (OPCIONAL)\n"})
            self.clicar_botao_2()
            
        elif resultado[0] ==1.18:
            socketio.emit('log_message', {'message': f"\nEstratégia 5X Confirmada {resultado[0]}\n\nDUAS TENTATIVAS (OPCIONAL)\n"})
            self.clicar_botao_2()
            
        elif resultado[0] ==1.50:
            socketio.emit('log_message', {'message': f"\nEstratégia ROSA Confirmada {resultado[0]}\n\nDUAS TENTATIVAS (OPCIONAL)\n"})
            self.clicar_botao_2()

    def clicar_botao_1(self):
        try:
            botao = self.driver.find_element(By.XPATH, '/html/body/app-root/app-game/div/div[1]/div[2]/div/div[2]/div[3]/app-bet-controls/div/app-bet-control[1]/div/div[1]/div[2]/button')
            botao.click()
            socketio.emit('log_message', {'message': "APOSTA FEITA EM 1 devido à estratégia."})
        except Exception as e:
            socketio.emit('log_message', {'message': f"Erro ao Apostar em 1: {e}"})

    def clicar_botao_2(self):
        try:
            botao = self.driver.find_element(By.XPATH, '/html/body/app-root/app-game/div/div[1]/div[2]/div/div[2]/div[3]/app-bet-controls/div/app-bet-control[2]/div/div[2]/div[2]/button')
            botao.click()
            socketio.emit('log_message', {'message': "APOSTA FEITA EM 2 devido à estratégia."})
        except Exception as e:
            socketio.emit('log_message', {'message': f"Erro ao Apostar em 2: {e}"})

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_bot')
def start_bot(data):
    user = data.get('user')
    password = data.get('password')
    bot_thread = SeleniumThread(user, password)
    bot_thread.start()

if __name__ == '__main__':
    socketio.run(app, debug=True)
