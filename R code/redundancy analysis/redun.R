require(caret)
require(e1071)
require(Hmisc)
require(rms)

root_path <- "D://"
fn <- paste(root_path, "all_features2019.csv", sep="")
data <- read.csv(fn)

variables <- names(data)

topic_model_features <- paste("t", 1:20, sep="")

#topic_model_features, "conference", "from_organization", "num_root_files"
# variables <- variables[-which(variables %in% c("stars", "paper_id", "paper_title", topic_model_features, "conference", "from_organization", "total_lines", "year", "citation", "main_language", "framework", "num_lang"))]

variables <- topic_model_features[-7]

form1 <- paste(variables, collapse="+")

form <- as.formula(paste("~", form1, sep=""))

redun(form, data)
