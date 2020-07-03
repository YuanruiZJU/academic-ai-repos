root_path <- "D://"
fn <- paste(root_path, "all_features201902.csv", sep="")
data <- read.csv(fn)

variables <- names(data)

topic_model_features <- paste("t", 1:20, sep="")

#topic_model_features, "conference", "from_organization", "num_root_files"
 variables <- variables[-which(variables %in% c("stars", "paper_id", "paper_title", topic_model_features, "conference", "from_organization", "year", "citation", "main_language", "framework", "num_lang"))]

#variables <- topic_model_features

correlations <- cor(data[variables], method="spearman")

for (i in 1:(length(variables)-1)){
		for (j in (i+1):length(variables)){
			corr_val <- correlations[variables[i], variables[j]]
			if (corr_val > 0.7 | corr_val < -0.7){
				print(paste(c(variables[i], variables[j], ":", as.character(corr_val), "\n"), collapse=" "))
			}
		}
	}

# "contain_data", "contain_docker", "has_video", "contain_project_page", "main_language", "contain_trained_model", "has_license", "framework"

vars <- c("main_language","framework")

#continuous_variables <- variables[-which(variables %in% vars)]

continuous_variables <- variables

for (var in vars){
	print(var)
	for (cv in continuous_variables){
		print(cv)
		form <- as.formula(paste(c("~", var, "+", cv), collapse=""))
		temp_table <- xtabs(form, data)
		print(chisq.test(temp_table))
	}
	print("=======================================================")
}