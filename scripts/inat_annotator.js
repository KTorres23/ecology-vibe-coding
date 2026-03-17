{
    // --- State Management ---
    let annotationData = [];
    let blacklistedIds = new Set(); 
    let currentPage = 1;
    let currentTaxonId = null;
    let currentSpeciesName = "";

    // --- 1. CSV Upload Logic (Resume Session) ---
    window.uploadPreviousData = function(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function(e) {
            const text = e.target.result;
            const rows = text.split('\n');
            
            // Assuming 'observation_id' is the first column
            for (let i = 1; i < rows.length; i++) {
                const columns = rows[i].split(',');
                if (columns[0]) {
                    // Remove quotes and whitespace
                    const id = columns[0].replace(/"/g, "").trim();
                    if (id) blacklistedIds.add(id);
                }
            }
            
            const statusMsg = `Loaded ${blacklistedIds.size} completed IDs. These will be skipped!`;
            document.getElementById("uploadStatus").innerText = statusMsg;
            console.log("Blacklist initialized:", blacklistedIds);
        };
        reader.readAsText(file);
    };

    // --- 2. The Search Function (Must be async) ---
    window.checkINaturalist = async function() {
        const input = document.getElementById("speciesInput").value.trim();
        if (!input) {
            alert("Please enter a species name.");
            return;
        }

        currentPage = 1; 
        
        try {
            const taxonRes = await fetch(`https://api.inaturalist.org/v1/taxa/autocomplete?q=${encodeURIComponent(input)}&per_page=1`);
            const taxonData = await taxonRes.json();
            
            if (!taxonData.results || taxonData.results.length === 0) {
                alert("Species not found.");
                return;
            }

            currentTaxonId = taxonData.results[0].id;
            currentSpeciesName = taxonData.results[0].name;
            
            fetchObservations(); 
        } catch (err) {
            console.error("Search Error:", err);
        }
    };

    // --- 3. The Observation Fetcher (Must be async) ---
    async function fetchObservations() {
        const tbody = document.getElementById("resultsBody");
        const table = document.getElementById("resultsTable");
        
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;">🔍 Loading Page ${currentPage}...</td></tr>`;
        table.style.display = "table";

        try {
            const url = `https://api.inaturalist.org/v1/observations?taxon_id=${currentTaxonId}&per_page=20&page=${currentPage}&order=desc&order_by=created_at`;
            const obsRes = await fetch(url);
            const obsData = await obsRes.json();

            if (!obsData.results || obsData.results.length === 0) {
                tbody.innerHTML = `<tr><td colspan="8">No more observations found.</td></tr>`;
                return;
            }

            let html = "";
            let skippedCount = 0;

            obsData.results.forEach(obs => {
                // SKIP logic: Check if ID is in blacklist
                if (blacklistedIds.has(obs.id.toString())) {
                    skippedCount++;
                    return; 
                }

                const imgUrl = (obs.photos && obs.photos.length > 0) 
                    ? obs.photos[0].url.replace('square', 'medium') 
                    : 'https://via.placeholder.com/150?text=No+Photo';
                
                html += `
                    <tr>
                        <td><img src="${imgUrl}" width="150" style="border-radius:4px;"><br>
                            <a href="${obs.uri}" target="_blank" style="font-size:11px;">#${obs.id}</a></td>
                        <td><i>${currentSpeciesName}</i></td>
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
                        <td><input type="checkbox" id="road-${obs.id}"> Road?</td>
                        <td><button onclick="window.addAnnotation('${obs.id}', '${currentSpeciesName}')" 
                                    style="background-color:#0366d6; color:white; border:none; padding:5px; border-radius:4px; cursor:pointer;">
                                    Save
                            </button></td>
                    </tr>
                `;
            });

            if (html === "" && skippedCount > 0) {
                tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;">All observations on this page were already annotated. Click Next.</td></tr>`;
            } else {
                tbody.innerHTML = html;
            }

        } catch (err) {
            console.error("Fetch Error:", err);
            tbody.innerHTML = `<tr><td colspan="8">Error loading data.</td></tr>`;
        }
    }

    // --- 4. Controls & Export ---
    window.changePage = function(direction) {
        if (!currentTaxonId) return;
        if (direction === 'next') currentPage++;
        else if (direction === 'prev' && currentPage > 1) currentPage--;
        fetchObservations();
    };

    window.addAnnotation = function(id, species) {
        const entry = {
            observation_id: id,
            scientific_name: species,
            life_stage: document.getElementById(`stage-${id}`).value,
            status: document.getElementById(`status-${id}`).value,
            environment: document.getElementById(`road-${id}`).checked ? "Road" : "No Road",
            annotated_at: new Date().toISOString()
        };
        const idx = annotationData.findIndex(item => item.observation_id === id);
        if (idx > -1) annotationData[idx] = entry;
        else annotationData.push(entry);
        alert(`Saved #${id}. Session total: ${annotationData.length}`);
    };

    window.downloadCSV = function() {
        if (annotationData.length === 0) return alert("Nothing to export.");
        const headers = Object.keys(annotationData[0]).join(",");
        const rows = annotationData.map(obj => Object.values(obj).map(v => `"${v}"`).join(",")).join("\n");
        const link = document.createElement("a");
        link.setAttribute("href", encodeURI("data:text/csv;charset=utf-8," + headers + "\n" + rows));
        link.setAttribute("download", `inat_annotations_${Date.now()}.csv`);
        link.click();
    };
}