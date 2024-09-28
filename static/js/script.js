document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const startButton = document.getElementById('start-btn');
    const stopButton = document.getElementById('stop-btn'); // Novo botão "Parar"
    const restartButton = document.getElementById('restart-btn'); // Novo botão "Reiniciar"
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const logContainer = document.getElementById('log-container');
    let messageHistory = new Set(); // Set para armazenar IDs de mensagens já exibidas

    startButton.addEventListener('click', () => {
        const user = usernameInput.value;
        const password = passwordInput.value;

        if (!user || !password) {
            addLogMessage('Por favor, preencha todos os campos.');
            return;
        }

        logContainer.innerHTML = ''; // Limpar mensagens antigas antes de iniciar o bot

        socket.emit('start_bot', { user, password });
    });

    // Event listeners para os novos botões
    stopButton.addEventListener('click', () => {
        socket.emit('stop_bot');
    });

    restartButton.addEventListener('click', () => {
        const user = usernameInput.value;
        const password = passwordInput.value;

        if (!user || !password) {
            addLogMessage('Por favor, preencha todos os campos.');
            return;
        }

        logContainer.innerHTML = ''; // Limpar mensagens antigas antes de reiniciar o bot

        socket.emit('restart_bot', { user, password });
    });

    socket.on('log_message', (data) => {
        if (!messageHistory.has(data.message)) {
            const messageType = getMessageType(data.message);
            addLogMessage(data.message, messageType);
            messageHistory.add(data.message);

            // Remover mensagem após 10 segundos
            setTimeout(() => {
                messageHistory.delete(data.message);
                removeLogMessage(data.message);
            }, 10000); // 10000ms = 10 segundos
        }
    });

    socket.on('resultado', (data) => {
        const resultadoMessage = `Resultado: ${data.resultado}`;
        if (!messageHistory.has(resultadoMessage)) {
            addLogMessage(resultadoMessage, false);
            messageHistory.add(resultadoMessage);

            // Remover mensagem após 10 segundos
            setTimeout(() => {
                messageHistory.delete(resultadoMessage);
                removeLogMessage(resultadoMessage);
            }, 10000); // 10000ms = 10 segundos
        }
    });

    // Função para verificar o tipo da mensagem
    function getMessageType(message) {
        if (message.includes("LOSS")) {
            return "loss-message";
        } else if (message.includes("GREEN")) {
            return "green-message";
        } else {
            return checkIfStrategyMessage(message) ? "estrategia-message" : "";
        }
    }

    // Função para verificar se a mensagem está relacionada a uma estratégia
    function checkIfStrategyMessage(message) {
        const strategyKeywords = ["Estratégia", "VELA", "888BETS"];
        return strategyKeywords.some(keyword => message.includes(keyword));
    }

    function addLogMessage(message, messageType) {
        const messageElement = document.createElement('p');
        messageElement.textContent = message;
        messageElement.dataset.message = message; // Usar dataset para armazenar a mensagem

        if (messageType) {
            messageElement.classList.add(messageType);
        }

        logContainer.appendChild(messageElement);
    }

    function removeLogMessage(message) {
        const messages = logContainer.querySelectorAll(`p[data-message="${message}"]`);
        messages.forEach(msg => logContainer.removeChild(msg));
    }
});
