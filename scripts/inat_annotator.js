{
    // 1. Setup Session State
    let annotationData = [];
    let currentPage = 1;
    let currentTaxonId = null;
    let currentSpeciesName = "";

    // 2. The Search Function (Triggered by your button)
    window.checkINaturalist = async function() {
        const input = document.getElementById("speciesInput").value.trim();
        if (!input) {
            alert("Please enter a species name.");
            return;
        }

        currentPage = 1; // Reset to page 1 for new search
        
        try {
            const taxonRes = await fetch(`https://api.inaturalist.org/v1/taxa/autocomplete?q=${encodeURIComponent(input)}&per_page=1`);
            const taxonData = await taxonRes.json();
            
            if (!taxonData.results || taxonData.results.length === 0) {
                alert("Species not found. Try the scientific name.");
                return;
            }

            currentTaxonId = taxonData.results[0].id;
            currentSpeciesName = taxonData.results[0].name;
            
            fetchObservations(); // Move to the data display
        } catch (err) {
            console.error("Search Error:", err);
            alert("Could not connect to iNaturalist.");
        }
    };

    // 3. The Observation Fetcher
    async function fetchObservations() {
        const tbody = document.getElementById("resultsBody");
        const table = document.getElementById("resultsTable");
        
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;">🔍 Loading Page ${currentPage}...</td></tr>`;
        table.style.display = "table";

        try {
            const url = `https://api.inaturalist.org/v1/observations?taxon_id=${currentTaxonId}&per_page=10&page=${currentPage}&order=desc&order_by=created_at`;
            const obsRes = await fetch(url);
            const obsData = await obsRes.json();

            if (!obsData.results || obsData.results.length === 0) {
                tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;">No observations found on this page.</td></tr>`;
                return;
            }

            let html = "";
            obsData.results.forEach(obs => {
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
                        <td><button onclick="addAnnotation('${obs.id}', '${currentSpeciesName}')" 
                                    style="background-color:#0366d6; color:white; border:none; padding:5px; border-radius:4px; cursor:pointer;">
                                    Save
                            </button></td>
                    </tr>
                `;
            });
            tbody.innerHTML = html;
            table.scrollIntoView({ behavior: 'smooth', block: 'start' });

        } catch (err) {
            console.error("Fetch Error:", err);
            tbody.innerHTML = `<tr><td colspan="8">Error loading data.</td></tr>`;
        }
    }

    // 4. Page Controls
    window.changePage = function(direction) {
        if (!currentTaxonId) return;
        if (direction === 'next') currentPage++;
        else if (direction === 'prev' && currentPage > 1) currentPage--;
        fetchObservations();
    };

    // 5. Data Saving
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
        
        console.log("Saved. Total in queue:", annotationData.length);
        alert(`Saved Obs #${id}! Total annotated: ${annotationData.length}`);
    };

    // 6. CSV Export
    window.downloadCSV = function() {
        if (annotationData.length === 0) {
            alert("Nothing to export yet.");
            return;
        }
        const headers = Object.keys(annotationData[0]).join(",");
        const rows = annotationData.map(obj => Object.values(obj).map(v => `"${v}"`).join(",")).join("\n");
        const csvContent = "data:text/csv;charset=utf-8," + headers + "\n" + rows;
        const link = document.createElement("a");
        link.setAttribute("href", encodeURI(csvContent));
        link.setAttribute("download", `inat_annotations_${Date.now()}.csv`);
        link.click();
    };

} // <--- THIS is the closing bracket that was likely missing!