function toggleExtension() {
    let container = document.getElementById('extension-container');
    if (container.classList.contains('extension-minimized')) {
        container.classList.remove('extension-minimized');
        container.classList.add('extension-expanded');
        adjustWidthBasedOnContent();
        document.getElementById('toggle-button').textContent = '←'; 
    } else {
        container.classList.remove('extension-expanded');
        container.classList.add('extension-minimized');
        container.style.width = "25px";
        document.getElementById('toggle-button').textContent = '→'; 
    }
}

function adjustWidthBasedOnContent() {
    let tabs = document.querySelectorAll('.tab');
    let maxWidth = 400;
    tabs.forEach(function(tab) {
        let tabWidth = tab.scrollWidth + 40;
        if (tabWidth > maxWidth) {
            maxWidth = tabWidth;
        }
    });
    document.getElementById('extension-container').style.width = maxWidth + "px";
}

document.addEventListener('DOMContentLoaded', function() {
    async function fetchAndUpdateUnitsData() {
        const token = localStorage.getItem('access_token');

        if (!token) {
            window.location.href = 'login.html'; 
            return;
        }

        try {
            const response = await fetch('https://epic-seven-armory.onrender.com/api/get_selected_units_data', {
                method: 'GET',
                headers: {
                    'Authorization': 'Bearer ' + token
                }
            });

            const data = await response.json();

            if (response.ok) {
                console.log(data);
                const units_data = data.reduce((map, obj) => {
                    map[obj.name] = obj;
                    return map;
                }, {});
                updateUnitData(units_data);
            } else {
                console.error('Error fetching unit data:', data);
                if (data.msg === 'Token has expired' || data.msg === 'Token is invalid') {
                    window.location.href = 'login.html';
                }
            }
        } catch (error) {
            console.error('Error fetching unit data:', error);
        }
    }

    fetchAndUpdateUnitsData();

    setInterval(fetchAndUpdateUnitsData, 5000);
});

function updateUnitData(unitData) {
    let tabContent = document.querySelector('.overlay');
    tabContent.innerHTML = '';
    
    console.log(unitData)
    for (let unit of Object.values(unitData)) 
        if (unit) {
            const unitDiv = document.createElement("div")
            unitDiv.innerHTML = `
            <div class="tab-content" id="unit-${unit.id}" style = "display:block">
                <div class="unit-stats">
                    <div class="stat">Unit Name: ${unit.name}</div>
                    <div class="stat">Health: ${unit.health}</div>
                    <div class="stat">Attack: ${unit.attack}</div>
                    <div class="stat">Defense: ${unit.defense}</div>
                    <div class="stat">Speed: ${unit.speed}</div>
                    <div class="stat">Critical Hit Chance: ${unit.critical_hit_chance}</div>
                    <div class="stat">Critical Hit Damage: ${unit.critical_hit_damage}</div>
                    <div class="stat">Effectiveness: ${unit.effectiveness}</div>
                    <div class="stat">Effect Resistance: ${unit.effect_resistance}</div>
                </div>
            </div>
            `;

            tabContent.appendChild(unitDiv)}
    }
