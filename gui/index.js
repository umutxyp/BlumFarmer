window.addEventListener('DOMContentLoaded', () => {
    const numLines = 10;
    const body = document.body;

    for (let i = 0; i < numLines; i++) {
        const horizontalLine = document.createElement('div');
        horizontalLine.className = 'line horizontal';
        horizontalLine.style.top = `${(i + 1) * 10}%`;
        body.appendChild(horizontalLine);

        const verticalLine = document.createElement('div');
        verticalLine.className = 'line vertical';
        verticalLine.style.left = `${(i + 1) * 10}%`;
        body.appendChild(verticalLine);

        const movingLine = document.createElement('div');
        movingLine.className = 'moving-line';
        movingLine.style.left = `${(i + 1) * 10}%`;
        movingLine.style.animationDuration = `${Math.random() * 2 + 2}s`;
        body.appendChild(movingLine);
    }

    const numSnowflakes = 20;
    for (let i = 0; i < numSnowflakes; i++) {
        let random = Math.random() * 40 + 10;
        const snowflake = document.createElement('div');
        snowflake.className = 'snowflake';
        snowflake.style.left = `${Math.random() * 100}vw`;
        snowflake.style.animationDuration = `${Math.random() * 5 + 5}s`;
        snowflake.style.opacity = `${Math.random() * 0.5 + 0.5}`;
        snowflake.style.width = `${random}px`;
        snowflake.style.height = `${random}px`;
        body.appendChild(snowflake);
    }
});


window.addEventListener('DOMContentLoaded', () => {

    document.querySelector("button[id='join_our_blum_team']").addEventListener("click", () => {
        document.getElementById('header').classList.add('hidden');
        document.getElementById('blum_team').classList.remove('hidden');
    });

    document.querySelector("button[id='join_blum_team']").addEventListener("click", () => {
        const a = document.createElement('a');
        a.href = 'https://t.me/BlumCryptoBot/app?startapp=tribe_umutland-ref_xAb9VoGIDx';
        a.target = '_blank';
        document.body.appendChild(a);
        a.click();

        let blum_team = document.getElementById('blum_team');
        blum_team.querySelector('p').innerText = 'Thank you for joining our blum team!';

        let btn = document.getElementById('join_blum_team');
        btn.classList.add('hidden');
        btn = document.getElementById('launch_blum_farmer');
        btn.classList.remove('hidden');
    });

    document.querySelector("button[id='launch_blum_farmer']").addEventListener("click", () => {
        document.getElementById('blum_team').classList.add('hidden');
        document.getElementById('form-container').classList.remove('hidden');
    });
    
    document.querySelector("button[id='complete_and_start']").addEventListener("click", () => {
        const speed = document.getElementById('speed').value;
        const pause = document.getElementById('pause').value;
    
        document.getElementById('form-container').classList.add('hidden');
        document.querySelector('div[id="status"]').classList.remove('hidden');
    
        console.log(`Speed: ${speed}, Pause: ${pause}`);
    
        window.electron.ipcRenderer.send('start_blum_farmer', { speed, pause });

        window.electron.ipcRenderer.on('status', (event, arg) => {
            const json = JSON.parse(arg);
            if (json?.error) {
                document.querySelector('div[id="status"]').innerHTML = `
                <br>
                <p style="color: #ff0000;">${json.error}</p>
                `;
                return;
            } 
            document.querySelector('div[id="status"]').innerHTML = `
            <br>
            <p style="color: #68fc5d;">${json.message}</p>
            `;
        });
    });

});