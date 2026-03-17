/* inat_annotator.js
   Functionality: Fetches specific observations and handles 
   manual annotation for CSV export.
*/

let annotationData = []; // State: Stores your labels during the session

// Helper to prevent API flooding
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function checkINaturalist() {
    const input = document.getElementById("speciesInput").value.trim();
    const speciesList = input.split("\n").map(s => s.trim()).filter(s => s.length > 0);
    const table = document.getElementById("resultsTable");
    const tbody = document.getElementById("resultsBody");

    if (speciesList.length === 0) {
        alert("Please enter at least one species name.");
        return;
    }

    tbody.innerHTML = '<tr><td colspan="8">Searching for observations...</td></tr>';
    table.style.display = "table";

    let combinedRows = "";

    for (const species of speciesList) {
        try {
            // 1. Get the Taxon ID first
            const taxonRes = await fetch(`https://api.inaturalist.org/v1/taxa/autocomplete?q=${encodeURIComponent(species)}&per_page=1`);
            const taxonData = await taxonRes.json();
            
            if (taxonData.results.length === 0) {
                combinedRows += `<tr><td colspan="8">Taxon not found: ${species}</td></tr>`;
                continue;
            }

            const taxonId = taxonData.results[0].id;
            const sciName = taxonData.results[0].name;

            // 2. Get the 5 most recent observations for this taxon
            const obsRes = await fetch(`https://api.inaturalist.org/v1/observations?taxon_id=${taxonId}&per_page=5&order=desc&order_by=created_at`);
            const obsData = await obsRes.json();

            obsData.results.forEach(obs => {
                const imgUrl = obs.photos.length > 0 ? obs.photos[0].url.replace('square', 'medium') : 'https://via.placeholder.com/150';
                
                combinedRows += `
                    <tr>
                        <td><img src="${imgUrl}" width="150" style="border-radius:4px;"><br><small>Obs #${obs.id}</small></td>
                        <td><a href="${obs.uri}" target="_blank">View iNat</a></td>
                        <td><i>${sciName}</i></td>
                        <td>
                            <select id="stage-${obs.id}">
                                <option value="adult">Adult</option>
                                <option value="juvenile">Juvenile</option>
                                <option value="egg_larva">Egg/Larva</option>
                            </select>
                        </td>
                        <td>
                            <select id="status-${obs.id}">
                                <option value="alive">Alive</option>
                                <option value="dead">Dead</option>
                            </select>
                        </td>
                        <td>
                            <input type="checkbox" id="road-${obs.id}"> Road in bg?
                        </td>
                        <td>
                            <button onclick="addAnnotation('${obs.id}', '${sciName}')" style="background-color: #0366d6; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">Save</button>
                        </td>
                    </tr>
                `;
            });

        } catch (err) {
            console.error(err);
            combinedRows += `<tr><td colspan="8">Error fetching ${species}</td></tr>`;
        }
        await sleep(300); // Respect iNat's API limits
    }
    tbody.innerHTML = combinedRows;
}

// Logic to store the annotation in the session array
function addAnnotation(id, species) {
    const stage = document.getElementById(`stage-${id}`).value;
    const status = document.getElementById(`status-${id}`).value;
    const road = document.getElementById(`road-${id}`).checked ? "Road" : "No Road";

    const entry = {
        observation_id: id,
        scientific_name: species,
        life_stage: stage,
        status: status,
        environment: road,
        annotated_at: new Date().toLocaleString()
    };

    // Update if exists, otherwise push new
    const idx = annotationData.findIndex(item => item.observation_id === id);
    if (idx > -1) annotationData[idx] = entry;
    else annotationData.push(entry);

    alert(`Saved #${id} to CSV queue.`);
}

// Logic to convert array to CSV and download
function downloadCSV() {
    if (annotationData.length === 0) {
        alert("Queue is empty! Annotate some images first.");
        return;
    }

    const headers = Object.keys(annotationData[0]).join(",");
    const rows = annotationData.map(obj => Object.values(obj).map(v => `"${v}"`).join(",")).join("\n");
    const csvContent = "data:text/csv;charset=utf-8," + headers + "\n" + rows;

    const link = document.createElement("a");
    link.setAttribute("href", encodeURI(csvContent));
    link.setAttribute("download", `inat_annotations_${new Date().getTime()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}