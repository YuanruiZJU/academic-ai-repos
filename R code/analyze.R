library("pROC")
library("randomForest")
library("naivebayes")
library("reshape")
library("e1071")
library("ScottKnottESD")
library("caret")
library("pracma")
library("PRROC")

# set the path of the parent directory of $R code$ directory.
# You also need to put all_features.csv into the root directory.

root_path <- #?

source(paste(c(root_path, "R code/packages/imbalance.R"), collapse=""))
source(paste(c(root_path, "R code/packages/measures.R"), collapse=""))
source(paste(c(root_path, "R code/packages/VarImportance.R"), collapse=""))

fn <- paste(root_path, "all_features.csv", sep="")
data <- read.csv(fn)
label <- "popular"

run_name <- "our"

point1 <- ceiling(nrow(data) * 0.3)
point2 <- ceiling(nrow(data) * 0.2)
point3 <- ceiling(nrow(data) * 0.3)
star_threshold1 <- data$stars[order(data$stars, decreasing=TRUE)][point1]
star_threshold2 <- data$stars[order(data$stars, decreasing=TRUE)][point2]
star_threshold3 <- data$stars[order(data$stars, decreasing=TRUE)][point3]

variables <- names(data)
 
our_variables <- variables[-which(variables %in% c("stars", "paper_id", "paper_title", "conference", "from_organization", "total_lines", 
"year", "citation", "num_lang", "main_language", "framework"))]
variables <- our_variables

data$popular <- data$stars >= star_threshold2
data1 <- data[which(data$stars >= star_threshold2),]
data2 <- data[which(data$stars <= star_threshold1),]
data <- rbind(data1, data2)


data$popular <- as.character(data$popular)
data$popular <- factor(data$popular, order=TRUE, levels=c("FALSE", "TRUE"))

############################################################
# RQ1
############################################################

data1 <- data[which(data$popular=="TRUE"),]
data2 <- data[which(data$popular=="FALSE"),]

for (f in variables){
	print("===============================================")
	print(f)
	print(wilcox.test(data1[,f], data2[,f]))
	print(cliff.delta(data1[,f], data2[,f]))
}


#############################################################
# RQ2
#############################################################

variables_str <- paste(variables, collapse="+")
formula_str <- paste(label, variables_str, sep="~")
form <- as.formula(formula_str)
print(form)
bootstrap_times <- 1000
auc_scores <- c()
importance_matrix <- NULL

for (i in 1:bootstrap_times){
	set.seed(i); train_indices <- sample(nrow(data), replace=TRUE)
	train_data <- data[train_indices,]

	# Undersampling
	#train_data <- undersampling(train_data, label)
	
	# Resampling
	# train_data <- resampling(train_data, label)

	test_data <- data[-unique(train_indices),]

	fit <- randomForest(form, train_data, ntree=100)
	prediction <- predict(fit, test_data, type="prob")
	prob <- prediction[,2]
	# fit <- naive_bayes(form, train_data)
	# prediction <- predict(fit, test_data, type="prob")
	# prob <- prediction[,2]
	result <- roc(test_data$popular, prob)
	print(result["auc"][[1]][1])


	auc_scores <- append(auc_scores, result["auc"][[1]][1])

	importance_values <- VarImportance(fit, "random_forest", variables, test_data, label)
	#importance_values <- importance(fit, type=1)
	if (is.null(importance_matrix)){
		importance_matrix <- matrix(importance_values, nrow=1)
	}
	else{
		temp_matrix <- matrix(importance_values, nrow=1)
		importance_matrix <- rbind(importance_matrix, temp_matrix)
	}
}

importance_frame <- as.data.frame(importance_matrix)
names(importance_frame) <- variables
row.names(importance_frame) <- as.character(1:bootstrap_times)
sk <- sk_esd(importance_frame)

# print out the feature importance results
sk

print(mean(auc_scores))



