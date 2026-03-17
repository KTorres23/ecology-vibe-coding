{
    let annotationData = [];
    let blacklistedIds = new Set(); 
    let currentPage = 1;
    let currentTaxonId = null;
    let currentSpeciesName = "";
    let totalResults = 0;
    let totalPages = 0;
    const perPage = 30; // iNat default for a good balance

    window.uploadPreviousData = function(event) {
        const file = event.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = function(e) {
            const text = e.target.result;
            const rows = text.split('\n');
            for (let i = 1; i < rows.length; i++) {
                const columns = rows[i].split(',');
                if (columns[0]) {
                    const id = columns[0].replace(/"/g, "").trim();
                    if (id) blacklistedIds.add(id);
                }
            }
            document.getElementById("uploadStatus").innerText = `Skipping ${blacklistedIds.size} IDs from your CSV.`;
        };
        reader.readAsText(file);
    };

    window.checkINaturalist = async function() {
        const input = document.getElementById("speciesInput").value.trim();
        if (!input) return alert("Enter a species.");
        
        currentPage = 1; 
        try {
            const taxonRes = await fetch(`https://api.inaturalist.org/v1/taxa/autocomplete?q=${encodeURIComponent(input)}&per_page=1`);
            const taxonData = await taxonRes.json();
            if (!taxonData.results[0]) return alert("Not found.");

            currentTaxonId = taxonData.results[0].id;
            currentSpeciesName = taxonData.results[0].name;
            fetchObservations(); 
        } catch (err) { console.error(err); }
    };

   async function fetchObservations() {
        const tbody = document.getElementById("resultsBody");
        const table = document.getElementById("resultsTable");
        
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding: 20px;">🔍 Loading Page ${currentPage}...</td></tr>`;
        table.style.display = "table";

        try {
            const url = `https://api.inaturalist.org/v1/observations?taxon_id=${currentTaxonId}&per_page=${perPage}&page=${currentPage}&order=desc&order_by=created_at`;
            const obsRes = await fetch(url);
            const obsData = await obsRes.json();

            totalResults = obsData.total_results || 0;
            totalPages = Math.ceil(totalResults / perPage);
            renderPagination(); 

            if (!obsData.results || obsData.results.length === 0) {
                tbody.innerHTML = `<tr><td colspan="8" style="text-align:center;">No observations found on this page.</td></tr>`;
                return;
            }

            let html = "";
            let shownOnPage = 0;

            obsData.results.forEach(obs => {

                if (blacklistedIds.has(obs.id.toString())) return;

                // A lightweight SVG that the browser generates - no external network call needed!
                const noPhotoSVG = `data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='150' height='150' viewBox='0 0 150 150'>
                    <rect width='150' height='150' fill='%23f1f1f1'/>
                    <text x='50%25' y='45%25' dominant-baseline='middle' text-anchor='middle' font-family='sans-serif' font-size='12' fill='%23666'>No Picture</text>
                    <text x='50%25' y='60%25' dominant-baseline='middle' text-anchor='middle' font-family='sans-serif' font-size='10' fill='%23999'>(Likely audio observation)</text>
                </svg>`;
                
                let imgUrl = noPhotoSVG; 
                if (obs.photos && obs.photos.length > 0) {
                    // Only use iNaturalist URL if the photo actually exists
                    imgUrl = obs.photos[0].url.replace('square', 'medium');
                }
    
                
                if (blacklistedIds.has(obs.id.toString())) return;

                // Image logic
                //let imgUrl = "https://static.inaturalist.org/photos/745145/square.jpg"; 
                if (obs.photos && obs.photos.length > 0) {
                    imgUrl = obs.photos[0].url.replace('square', 'medium');
                }
                
                shownOnPage++;
                html += `
                    <tr>
                        <td style="text-align:center;">
                            <img src="${imgUrl}" width="150" style="border-radius:4px; border: 1px solid #eee;" 
                                 onerror="this.src='https://via.placeholder.com/150?text=No+Photo'">
                        </td>
                        <td style="text-align:center;">
                            <a href="${obs.uri}" target="_blank" style="font-weight:bold; color:#0366d6;">#${obs.id}</a>
                        </td>
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
                        <td>
                            <button onclick="window.addAnnotation('${obs.id}', '${currentSpeciesName}')" 
                                    style="background:#28a745; color:white; border:none; padding:8px 12px; border-radius:4px; cursor:pointer; font-weight:bold;">
                                    Save
                            </button>
                        </td>
                    </tr>`;
            });

            if (shownOnPage === 0) {
                tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:40px;">
                    <p>All ${obsData.results.length} results on Page ${currentPage} are already in your CSV.</p>
                    <button onclick="window.changePage('next')" style="padding:10px 20px; cursor:pointer;">Jump to Page ${currentPage + 1} →</button>
                </td></tr>`;
            } else {
                tbody.innerHTML = html;
            }

            table.scrollIntoView({ behavior: 'smooth', block: 'start' });

        } catch (err) {
            console.error("Fetch Error:", err);
            tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; color:red;">Error loading data.</td></tr>`;
        }
    }

    function renderPagination() {
        const container = document.getElementById("paginationContainer");
        const progress = document.getElementById("progressSummary");
        
        // Safety Check: If these don't exist in HTML, stop here
        if (!container || !progress) {
            console.error("Missing pagination elements in HTML! Check for IDs 'paginationContainer' and 'progressSummary'.");
            return;
        }

        container.innerHTML = "";
        progress.innerText = `Showing Page ${currentPage} of ${totalPages} (${totalResults.toLocaleString()} total observations)`;

        const addBtn = (label, targetPage, active = false) => {
            const btn = document.createElement("button");
            btn.innerText = label;
            btn.style.margin = "2px";
            btn.style.padding = "6px 12px";
            btn.style.cursor = "pointer";
            btn.style.border = "1px solid #0366d6";
            btn.style.borderRadius = "4px";
            btn.style.backgroundColor = active ? "#0366d6" : "#fff";
            btn.style.color = active ? "#fff" : "#0366d6";
            btn.onclick = () => { 
                currentPage = targetPage; 
                fetchObservations(); 
            };
            container.appendChild(btn);
        };

        // Navigation logic (Previous, Window of pages, Next)
        if (currentPage > 1) addBtn("« Prev", currentPage - 1);

        let start = Math.max(1, currentPage - 2);
        let end = Math.min(totalPages, start + 4);
        if (end - start < 4) start = Math.max(1, end - 4);

        for (let i = start; i <= end; i++) {
            addBtn(i, i, i === currentPage);
        }

        if (currentPage < totalPages) addBtn("Next »", currentPage + 1);
    }

    window.jumpToPage = function() {
        const pageInput = document.getElementById("pageJumpInput").value;
        const pageNum = parseInt(pageInput);
        if (pageNum > 0 && pageNum <= totalPages) {
            currentPage = pageNum;
            fetchObservations();
        } else {
            alert(`Please enter a page between 1 and ${totalPages}`);
        }
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
        console.log("Total Annotated:", annotationData.length);
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