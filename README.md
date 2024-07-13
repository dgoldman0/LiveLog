# LiveLog

LiveLog is among the first voxsite platforms dedicated to authorship. LiveLog has a shared data model. Users agree to share their content to improve the voxsite, and LiveLog creates a tailored voxsite for the author, based on their own content. While there will be a web interface for now, the goal is to have the voxsite [GopherAI](https://github.com/dgoldman0/gopherAI) ready from early on.

# Technological Overview

## Enriched Synthetic Data

Synthetic data is data created artificially, such as by prompting a large language model (LLM) to create various sentences. When a corpus of material is provided as an input, and the synthetic data is filtered to align with the content provided, that synthetic data is enriched. It is this enrichment process that filters the random noise of an existing model, to create a tailored one, even when the corpus is too small to be sufficient training data itself. 

