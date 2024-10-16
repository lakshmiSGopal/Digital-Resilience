# Project Overview
This project focuses on the development of an automated system to extract and analyze disaster-related information from news reports in near real-time. By leveraging web scraping, natural language processing (NLP), and machine learning (ML), the system is designed to assist first responders and policymakers in making informed decisions during disaster response and recovery efforts. The core of the system consists of several modules: a web crawler, scraper, data filter, and machine learning models for disaster event detection and impact analysis. The work also emphasizes a gender-inclusive approach to disaster resilience, analyzing the vulnerabilities and contributions of women during disaster events.

# Modules
##Web Crawler
The web crawler collects data from a wide range of online news sources in near real-time. It searches for and retrieves articles related to disaster events using a static disaster ontology. The crawler ensures the system remains updated with the latest reports, continuously gathering relevant news data for further processing.

### Web Scraper
The scraper extracts the textual content from news articles gathered by the crawler. It removes irrelevant content such as advertisements, sidebars, and non-text elements, focusing only on the body of the news articles. The scraper helps in ensuring that only useful information is passed on for further analysis.

### Data Filter
This module filters out irrelevant or duplicate content and refines the data for machine learning analysis. The data filter cleans the text by removing stopwords, URLs, and special characters, and compares the cleaned data with disaster-related keywords. It ensures that only relevant news reports are retained for deeper analysis.

### Disaster Event Detection Machine Learning Model
This model detects and classifies disaster events such as floods, landslides, and storms. It uses multi-label classification to predict the type of disaster and identifies related events from the news data. With an accuracy of 70%-80%, the model helps to categorize various types of disasters for rapid understanding.

### Impact and Loss Detection Machine Learning Model
This model predicts the different impacts of a disaster, such as casualties, infrastructure damage, and economic losses. It identifies the key consequences of a disaster and generates insights on how the disaster affected various aspects of life and property. This model helps to prioritize response efforts by understanding the magnitude of damage.

# Future Enhancements in upcoming releases
Future work aims to develop a dynamic ontology, increase the volume of training data for ML models, and incorporate real-time data sources like social media for improved disaster detection. This will further enhance the accuracy and relevance of the system's outputs. 
