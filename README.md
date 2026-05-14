# Ecology-Vibe-Coding

A goofy little repo hosted as a [webpage](https://ktorres23.github.io/ecology-vibe-coding/) to play around with vibe coding ideas in ecology!

## Projects

* [iNaturalist Query Tool](https://ktorres23.github.io/ecology-vibe-coding/pages/inat_query.html)
* [TAMU Ecology Jobs](https://ktorres23.github.io/ecology-vibe-coding/pages/jobs.html)
* [iNaturalist Annotator Tool](https://ktorres23.github.io/ecology-vibe-coding/pages/image_sorter.html)
* [Insect Map Script with Rgbif Package](scripts/gbif_downloader.R)
* [iNaturalist Secondary Data Explorer](https://ktorres23.github.io/ecology-vibe-coding/pages/secondary_explorer.html)



### [iNaturalist Query Tool](https://ktorres23.github.io/ecology-vibe-coding/pages/inat_query.html)

**Purpose**: extract basic info on taxon via iNaturalist API

Base script generated with [perplexity.ai](https://www.perplexity.ai/) and GitHub Copilot and manually fine-tuned to produce additional output parameters



### [TAMU Ecology Jobs](https://ktorres23.github.io/ecology-vibe-coding/pages/jobs.html)

**Purpose**: Revisualizes jobs from [Texas A&M Natural Resources Job Board](https://jobs.rwfm.tamu.edu/)

> [!IMPORTANT] This project must be downloaded & ran locally- it does not work on a web page



### [iNaturalist Annotator Tool](https://ktorres23.github.io/ecology-vibe-coding/pages/image_sorter.html)

**Purpose**: manually annotate iNaturalist observations with metadata information to save as a CSV

> **Main prompt**: I'd like to try and build an app that pulls observation data from the iNaturalist API and lets me manually annotate the image with custom categories like "alive"/"dead" or "juvenile"/"adult" or "road in background"/"no road", similar to the annotation functionality that already exists in iNaturalist. However, in this case, the observation ID, my annotations, and other observational metadata get added to a CSV where the classification labels I make for each image get added to a CSV file on my computer.

Additional functionalities added:

* navigation
* filtering observations
* 'blacklisting' previous observations that were annotated



### [Insect Map Script with Rgbif Package](scripts/gbif_downloader.R)

> **Main prompt**: using Rgbif, write an R script that downloads all aquatic insect species occurrence info from the GBIF API, including the taxon orders of Plecoptera, Trichoptera, and Ephemeroptera. Then make a map of the world with points highlighting occurrence data of each order in a different color.



### [iNaturalist Secondary Data Explorer](https://ktorres23.github.io/ecology-vibe-coding/pages/secondary_explorer.html)

**Purpose**: explore the use of CLIP models for exploring secondary data in iNaturalist image observations

> **Main prompt**: I want to create a web-based data explorer with GitHub pages and HTML, CSS, and javascript using data from the iNaturalist API. I want to be able to search observations of species for information within the image, like presence of a road or a species interaction or a particular sex or life stage. This information is called secondary data. It should be possible to query for a particular species and then a query for the secondary data, probably using a CLIP-style model. Create the code for this to work so I can host it on my GitHub

Additional functionalities added:

* navigation & site-wide style
* filtering observations by taxon, dates, places, user, quality grade, sample size
* image observation preview before running CLIP predictions & confidence threshold slider
* use of a higher performing CLIP model


### *More projects coming soon...*

## useful tools/projects related to iNaturalist by others:

* See my [list of cool iNat tools hosted on GitHub repos](https://github.com/stars/KTorres23/lists/cool-inat-tools)
* [iNatSpectro](https://www.inatspectro.org/development/): multi-browser extension designed to integrate high-resolution spectrograms directly into iNaturalist observation pages.


---
**Contact:** Karina Torres ([karina.torres@siu.edu](mailto:karina.torres@siu.edu))  

**Last updated:** 2026-05-14
