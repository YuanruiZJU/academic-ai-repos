# What makes a popular AI academic repository?
This repository is the accompanying repository for our paper "What Makes a popular AI Academic Repository"

Many AI researchers use GitHub repositories to share data, software code and other resources that accompany their publications. 
We refer to such GitHub repositories as AI academic repositories. 
In our paper, we collect 1,149 AI academic repositories that are published by AI researchers.
We use number of stars as the proxy for measuring popularity of AI academic repositories.
Our analysis shows that **highly cited papers are more likely to have AI academic repositories with more stars**.
Hence, in our paper, we perform an empirical analysis of the collected AI academic repositories aiming to highlight *good software engineering practices* of popular AI academic repositories for AI researchers.


## Requirements
* Python 3
* R (>=3.5)
* Several Python packages including sqlalchemy, gensim, nltk, Beautiful Soup 4, etc. 

## Data

We provide an [OneDirve url](https://zjueducn-my.sharepoint.com/:u:/g/personal/yrfan_zju_edu_cn/EX5d772FSLFPqO-obR0ux0sBpXd3xqBGBpjyiG4MLL1J7w?e=gNAk0F) for downloading all the AI academic repositories that we collected.

## Replicating our results

1. Set the `root_path` of in the R file: `R code/analyze.R`.

2. Move `all_features.csv` to the `root_path` that is set in Step 1.

3. Run `analysis.R` in [R Commander](https://socialsciences.mcmaster.ca/jfox/Misc/Rcmdr/) or [RStudio](https://rstudio.com/).

## Checklist for AI Researchers

According to our experimental results, we have the following **checklist for AI researchers when publishing their AI academic repositories**:

1. **Provide complete code.** Your code should be as detailed as possible for replicating the experiments in your publication.

2. **The code and data should be well modularized.** You need to organize published code and data well in different directories. It would be better to modularize code into different directories.

3. **Pay special attention to the used programming languages and machine learning frameworks**.
   * AI academic repositories using *MATLAB* are **less** likely to be popular.
   * Organizations' AI academic repositories that use *Tensorflow* are **less** likely to be popular.
   * [Pytorch](https://github.com/pytorch/pytorch), [Torch](https://github.com/torch/torch7), and [MXNet](https://github.com/apache/incubator-mxnet) are recommended. They are more frequently used by popular AI academic repositories.

4. **Explicitly state the used machine learning framework in the README file of the repository.**

5. **Take measures to ease the reproducibility of your paper.** You can improve your repository as follows:
   * Provide the used *dataset* (Especially for organizations' AI academic repositories).
   * Provide the *pre-trained model*. (You also need to state the provided model in the README file and let users know that you provide it.)
   * Provide *shell scripts* to ease the environment deployment and running of your experiments.
   * Create a *docker image* and provide the *Dockerfile*.

6. **Improve the quality of your documentation.** We have the following suggestions:
   * Use lists to organize the content of the README file.
   * Present more images in the README file. The images can show the running results of your code. Also, the images can show the working mechanism of your code, e.g., architecture diagrams and equations.
   * Introduce more details about your code. You can use the code block and inline code elements that can be shown with MarkDown. In MarkDown, a code block is fenced by lines with three backticks, and an inline code element is surrounded by two backticks in a natural language sentence.
   * Provide links of other relevant GitHub repositories, e.g., the repository of the used machine learning framework, third-party implementation of the paper, and repositories referenced by the AI academic repository.
   * Choose a license for your AI academic repository.
   
7. **NOTE:** number of lists in the README file, number of images in the README file, and the inclusion of a license are the most important features that distinguish popular AI academic repositories from unpopular ones.
**Please use more lists to organize the README file, use more images in the README file, and choose a license for your AI academic repository.**









