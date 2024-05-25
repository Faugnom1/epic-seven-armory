// /**
//  * tabs no longer used
//  * Opens the specified tab and highlights the tab button.
//  * Hides all other tab contents and resets their background color.
//  */
// function openTab(evt, tabName) {
//     let i, tabcontent, tabs;
//     tabcontent = document.getElementsByClassName("tab-content");
//     for (i = 0; i < tabcontent.length; i++) {
//       tabcontent[i].style.display = "none";
//     }
//     tabs = document.getElementsByClassName("tab");
//     for (i = 0; i < tabs.length; i++) {
//       tabs[i].style.backgroundColor = "";
//     }
//     document.getElementById(tabName).style.display = "block";
//     evt.currentTarget.style.backgroundColor = "#ccc";
//   }

  /**
 * Toggles the extension container between minimized and expanded states.
 * Adjusts the width based on the content when expanded.
 */
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

/**
 * Adjusts the width of the extension container based on the width of the content.
 * Finds the maximum width required by any tab and sets the container width accordingly.
 */
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
  
/**
 * Fetches unit data from the server once the DOM content is fully loaded.
 * Stores the unit data in a global variable for later use.
 */
document.addEventListener('DOMContentLoaded', function() {
    fetch('/get_unit_data')
    .then(response => response.json())
    .then(data => {
        unitsData = data.reduce((map, obj) => {
            map[obj.name] = obj;
            return map;
        }, {});
    });
});

/**
 * Ensures that no more than a specified number of checkboxes can be selected.
 * If the limit is exceeded, displays an alert and prevents further selections.
 * Updates the server and UI based on the selected units.
 */
function checkCheckboxLimit(event) {
    const MAX_UNITS = 4;
    let checkedCheckboxes = document.querySelectorAll('#unit-selector input[type="checkbox"]:checked');
    if (checkedCheckboxes.length > MAX_UNITS) {
        alert('You can select up to 4 units only.');
        event.preventDefault();
        event.target.checked = false;
    } else {
        updateUnits(event, checkedCheckboxes.length);
        updateSelectedUnitsOnServer(checkedCheckboxes);
        console.log(checkedCheckboxes)
        console.log(event)
    }
};

/**
 * Updates the server with the currently selected units.
 * Sends the list of selected unit IDs to the server via a POST request.
 */
function updateSelectedUnitsOnServer(checkedCheckboxes) {
    const selectedUnits = Array.from(checkedCheckboxes).map(checkbox => {
        const unitId = checkbox.id.split('-')[1];
        return { id: unitId };
    });
    fetch('/update_selected_units', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ units: selectedUnits })
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(error => console.error(error));
};

/**
 * Updates the UI based on the selected units.
 * Adds the unit information to the page if a unit is selected.
 * Removes the unit information from the page if a unit is deselected.
 */
function updateUnits(event, checkedCheckboxes) {
    let unit = unitsData[event.target.value];
        if (!unit) return;
             if (checkedCheckboxes <= 4 && event.target.checked) {
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
                    let tabContent = document.querySelector('.overlay');
                    tabContent.appendChild(unitDiv)}
                    }
                    else if (!event.target.checked) {
                        document.getElementById(`unit-${unit.id}`).remove()
                    }
                };
