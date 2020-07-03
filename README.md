# What makes a popular AI academic repository?
This repository is the accompanying repository for our paper "What Makes a popular Academic AI Repository"

Many AI researchers use GitHub repositories to share data, software code and other resources that accompany their publications. 
We refer to such GitHub repositories as academic AI repositories. 
In our paper, we collect 1,149 academic AI repositories that are published by AI researchers.
We use number of stars as the proxy for measuring popularity of academic AI repositories.
Our analysis shows that **highly cited papers are more likely to have AI academic repositories with more stars**.
Hence, in our paper, we perform an empirical analysis of the collected academic AI repositories aiming to highlight *good software engineering practices* of popular academic AI repositories for AI researchers.


## Requirements
* Python 3
* R (>=3.5)
* Several Python packages including sqlalchemy, gensim, nltk, Beautiful Soup 4, etc. 

## Data
1. In the `code_repos` directory, we provide all the academic AI


We provide an [OneDirve url](https://zjueducn-my.sharepoint.com/:u:/g/personal/yrfan_zju_edu_cn/EX5d772FSLFPqO-obR0ux0sBpXd3xqBGBpjyiG4MLL1J7w?e=gNAk0F) for downloading all the AI academic repositories that we collected.

## Replicating our results

1. Set the `root_path` of in the R file: `R code/analyze.R`.

2. Move `all_features.csv` to the `root_path` that is set in Step 1.

3. Run `analysis.R` in [R Commander](https://socialsciences.mcmaster.ca/jfox/Misc/Rcmdr/) or [RStudio](https://rstudio.com/).

## Checklist for AI Researchers

According to our experimental results, we have the following **checklist for AI researchers when publishing their academic AI repositories**:
