function toggleExtension() {
    let button = document.getElementById('toggle-button');
    let container = document.getElementById('extension-container');
    let bodywidth = document.body.clientWidth;
    if (container.classList.contains('extension-minimized')) {
        container.classList.remove('extension-minimized');
        container.classList.add('extension-expanded');
        document.getElementById('toggle-button').textContent = '←'; 
        let width = document.getElementById('extension-container').offsetWidth;
        button.style.removeProperty('left')
        button.style.right = (bodywidth-width+15) + "px";   
    } else {
        container.classList.remove('extension-expanded');
        container.classList.add('extension-minimized');
        document.getElementById('toggle-button').textContent = '→'; 
        button.style.left = 0;
        button.style.position = absolute;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    async function fetchAndUpdateUnitsData() {
        const token = localStorage.getItem('access_token');

        // if (!token) {
        //     window.location.href = 'login.html'; 
        //     return;
        // }

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
