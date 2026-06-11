# Ecology-Vibe-Coding

A goofy little repo hosted as a [webpage](https://ktorres23.github.io/ecology-vibe-coding/) to play around with vibe coding ideas in ecology!

## Projects

Click on the *name* of the tool below to try it out, or click on the *description* to find out more about how to run it or how it was created. 

**Web-based** (i.e., hosted as a webpage that you can use, too!)

* [iNaturalist Query Tool](https://ktorres23.github.io/ecology-vibe-coding/pages/inat_query.html); [description](#inaturalist-query-tool)
* [iNaturalist Web Annotator Tool](https://ktorres23.github.io/ecology-vibe-coding/pages/image_sorter.html); [description](#inaturalist-annotator-tool)
* [iNaturalist Secondary Data Explorer](https://ktorres23.github.io/ecology-vibe-coding/pages/secondary_explorer.html); [description](#inaturalist-secondary-data-explorer)
* [TAMU Ecology Jobs](https://ktorres23.github.io/ecology-vibe-coding/pages/jobs.html); [description](#tamu-ecology-jobs)

**Locally-hosted** (i.e., must be run on your local computer's terminal and/or software)

> [!IMPORTANT]
> Note that you may need to change some of the path directory logic for these scripts

* [Insect Map Script with Rgbif Package](scripts/gbif_downloader.R); [description](#insect-map-script-with-rgbif-package)
* [Local Image Annotator](scripts/local_image_annotator.py); [description](#local-image-annotator)
* [Local Image Cropper](local_image_cropper.py); [description](#local-image-cropper)


## Web-based Projects

### [iNaturalist Query Tool](https://ktorres23.github.io/ecology-vibe-coding/pages/inat_query.html)

**Purpose**: extract basic info on taxon via iNaturalist API

Base script generated with [perplexity.ai](https://www.perplexity.ai/) and GitHub Copilot and manually fine-tuned to produce additional output parameters


### [iNaturalist Annotator Tool](https://ktorres23.github.io/ecology-vibe-coding/pages/image_sorter.html)

**Purpose**: manually annotate iNaturalist observations with metadata information to save as a CSV

> **Main prompt**: I'd like to try and build an app that pulls observation data from the iNaturalist API and lets me manually annotate the image with custom categories like "alive"/"dead" or "juvenile"/"adult" or "road in background"/"no road", similar to the annotation functionality that already exists in iNaturalist. However, in this case, the observation ID, my annotations, and other observational metadata get added to a CSV where the classification labels I make for each image get added to a CSV file on my computer.

Additional functionalities added:

* navigation
* filtering observations
* 'blacklisting' previous observations that were annotated


### [iNaturalist Secondary Data Explorer](https://ktorres23.github.io/ecology-vibe-coding/pages/secondary_explorer.html)

**Purpose**: explore the use of CLIP models for exploring secondary data in iNaturalist image observations

> **Main prompt**: I want to create a web-based data explorer with GitHub pages and HTML, CSS, and javascript using data from the iNaturalist API. I want to be able to search observations of species for information within the image, like presence of a road or a species interaction or a particular sex or life stage. This information is called secondary data. It should be possible to query for a particular species and then a query for the secondary data, probably using a CLIP-style model. Create the code for this to work so I can host it on my GitHub

Additional functionalities added:

* navigation & site-wide style
* filtering observations by taxon, dates, places, user, quality grade, sample size
* image observation preview before running CLIP predictions & confidence threshold slider
* use of a higher performing CLIP model


## Locally-hosted Projects

### [TAMU Ecology Jobs](https://ktorres23.github.io/ecology-vibe-coding/pages/jobs.html)

**Purpose**: Revisualizes jobs from [Texas A&M Natural Resources Job Board](https://jobs.rwfm.tamu.edu/). Initial locally-hosted project was remade into a web-hosted version using a GitHub Copilot agent.

**How it works:**
* A GitHub Action automatically runs a Python scraper **twice daily** (8 AM & 4 PM UTC)
* Jobs are scraped and saved to `jobs.json` in the repository
* The webpage loads `jobs.json` and displays jobs in a beautiful dashboard
* **No backend server needed!** Works on any static web host (GitHub Pages, etc.)

**To use this project:**
* Simply visit the link above and browse available ecology jobs
* The job list updates automatically every 8 hours

**To run locally:**
* Clone this repo and open `pages/jobs.html` in your browser (or run `python -m http.server 8000` and navigate to `http://localhost:8000/pages/jobs.html`)
* The `jobs.json` file is automatically kept fresh by GitHub Actions in the cloud


### [Insect Map Script with Rgbif Package](scripts/gbif_downloader.R)

> **Main prompt**: using Rgbif, write an R script that downloads all aquatic insect species occurrence info from the GBIF API, including the taxon orders of Plecoptera, Trichoptera, and Ephemeroptera. Then make a map of the world with points highlighting occurrence data of each order in a different color.


### [Local Image Annotator](scripts/local_image_annotator.py)

**Purpose**: manually annotate images with labels that get saved to a CSV file

> **Main prompt**: I need to develop some kind of interface for me to manually curate a dataset of labels based on another dataset of images. I want to go through my images and give them labels like "Adult", "nymph", "larvae", "hand", "other" etc. Then those labels should be corresponded with the image and observartions, which is the set of images they belong to. Can you create this interface for me? Please ask questions for clarification if needed. I attached the R script I used to create the image directories and file naming conventions of the images and observations. I'd also like the interface to tell me which image and observation and species I'm on, as well as whether I've already labelled it 

### [Local Image Cropper](scripts/local_image_cropper.py)

**Purpose**: Rename images copied from my camera and allow me to quickly crop them in my web browser

> **Main prompt**: Similar to the streamlit image annotation interface we made earlier, I need an interface for processing the images that I take on my camera and upload to iNaturalist. I need to be able to:
> - take images with " - Copy" in the file name and change to "_cropped"
> - grab these crop images to be processed in an interface to let me crop them sequentially and individually and then save the image as that cropped version


## useful tools/projects related to iNaturalist by others:

* See my [list of cool iNat tools hosted on GitHub repos](https://github.com/stars/KTorres23/lists/cool-inat-tools)
* [iNatSpectro](https://www.inatspectro.org/development/): multi-browser extension designed to integrate high-resolution spectrograms directly into iNaturalist observation pages.
* [iNaturalist Metadata Tool](https://chromewebstore.google.com/detail/inaturalist-metadata-tool/kgnajdmgemhinploocjifefdcbomdfph?pli=1) ([iNat forum post](https://forum.inaturalist.org/t/official-release-of-the-inaturalist-metadata-tool/79300))

## License & Citation

---
**Contact:** Karina Torres ([karina.torres@siu.edu](mailto:karina.torres@siu.edu))  

**Last updated:** 2026-05-23

[![Creative Commons License](https://i.creativecommons.org/l/by-nc/4.0/88x31.png)](http://creativecommons.org/licenses/by-nc/4.0/)  
This work is licensed under a [Creative Commons Attribution-NonCommercial 4.0 International License](http://creativecommons.org/licenses/by-nc/4.0/).

> ### Citation Notice
> **© 2026 Karina M. Torres.** All rights reserved.  
> *If referencing any preliminary findings, code, or ideas from this repository, please cite as:*  
> Torres, KM. "Ecology Vibe Coding." GitHub Repository, May 2026. URL: `https://github.com/ktorres23/ecology-vibe-coding`
