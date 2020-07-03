library("scoring")
library(SDMTools)


ConfusionMatrix <- function(test_data, prob, label){
	positive_label <- levels(data[,label])[2]
	obs <- as.numeric(test_data[label][,1] == positive_label)
	confusion_matrix <- confusion.matrix(obs, prob)
	tp <- confusion_matrix[2,2]
	fp <- confusion_matrix[2,1]
	fn <- confusion_matrix[1,2]
	tn <- confusion_matrix[1,1]
	return(c(tp, fp, tn, fn))
}


precision <- function(test_data, prob, label, positive){
	positive_label <- levels(data[,label])[2]
	obs <- as.numeric(test_data[label][,1] == positive_label)
	confusion_matrix <- confusion.matrix(obs, prob)
	tp <- confusion_matrix[2,2]
	fp <- confusion_matrix[2,1]
	fn <- confusion_matrix[1,2]
	tn <- confusion_matrix[1,1]
	if (positive){
		return(tp/(tp+fp))
	}
	else{
		return(tn/(tn+fn))
	}
		
}

recall <- function(test_data, prob, label, positive){
	positive_label <- levels(data[,label])[2]
	obs <- as.numeric(test_data[label][,1] == positive_label)
	confusion_matrix <- confusion.matrix(obs, prob)
	tp <- confusion_matrix[2,2]
	fp <- confusion_matrix[2,1]
	fn <- confusion_matrix[1,2]
	tn <- confusion_matrix[1,1]
	if (positive){
		return(tp/(tp+fn))
	} 
	else {
		return(tn/(tn+fp))
	}
	
}

F1 <- function(test_data, prob, label, positive){
	prec <- precision(test_data, prob, label, positive)
	rec <- recall(test_data, prob, label, positive)
	f1_value <- 2 * prec * rec / (prec + rec)
	return(f1_value)
}

accuracy <- function(test_data, prob, label){
	positive_label <- levels(data[,label])[2]
	obs <- as.numeric(test_data[label][,1] == positive_label)
	confusion_matrix <- confusion.matrix(obs, prob)
	tp <- confusion_matrix[2,2]
	tn <- confusion_matrix[1,1]
	acc <- (tp + tn) / nrow(test_data)
	return(acc)
}


# Using built-in methods in R, much faster!!!
calculate_cost_effectiveness2 <- function(ordered_data,  cut_off, var_la, var_ld, label){
	
	total_churn <- sum(ordered_data[var_la][,1], ordered_data[var_ld][,1])
	cum_loc <- cumsum(ordered_data[var_la][,1]+ordered_data[var_ld][,1])
	cum_ratio <- cum_loc / total_churn
	cut_index <- which(cum_ratio <= cut_off)
	inspected_data <- ordered_data[cut_index,]
	#print(names(inspected_data))
	inspected_buggy_index <- which(inspected_data[label][,1] == positive_label)
	all_buggy_index <- which(ordered_data[label][,1] == positive_label)
	inspected_num <- length(cut_index)
	inspected_buggy_num <- length(inspected_buggy_index)
	#all_buggy_num <- length(all_buggy_index)
	results <- c(inspected_buggy_num, inspected_num, all_buggy_index[1])
	return(results)
}

# Self implemented, TOO SLOW !!!
calculate_cost_effectiveness <- function(test_data, ordered_data, label){
	total_churn <- sum(test_data$real_la, test_data$real_ld)
	churn20p <- 0.2 * total_churn

	instance_num <- nrow(ordered_data)

	line_count <- 0
	buggy_count <- 0
	change_count <- 0
	first_buggy <- 0
	for (i in 1:instance_num){
		d <- ordered_data[i,]
		change_count <- change_count + 1
		if (d[label][,1] == positive_label){
			buggy_count <- buggy_count + 1
			if (first_buggy == 0){
				first_buggy = i
			}
		}
		line_count <- line_count + d$real_la + d$real_ld
		if (line_count > churn20p){
			break
		}
	}

	return(c(buggy_count, change_count, first_buggy))
}

BrierScore <- function(test_data, prob, label){
	truth <- as.numeric(test_data[label][,1]==positive_label)
	score_frame <- data.frame(truth, prob)
	score_form <- as.formula("truth ~ prob")
	scores <- brierscore(score_form, score_frame)
	mean_score <- mean(scores)
	return(mean_score)
}


# Using built-in methods in R, MUCH FASTER!!
Popt2 <- function(ordered_data, var_la, var_ld, label){
	total_churn <- sum(ordered_data[var_la][,1], ordered_data[var_ld][,1])
	real_buggy_data <- ordered_data[which(ordered_data[label][,1] == positive_label),]
	ordered_real_buggy_data <- real_buggy_data[order(real_buggy_data[var_la][,1] + real_buggy_data[var_ld][,1]),]
	cum_results1 <- cumsum(ordered_real_buggy_data[var_la][,1] + ordered_real_buggy_data[var_ld][,1])
	cum_ratio1 <- cum_results1 / total_churn
	buggy_num <- nrow(real_buggy_data)
	buggy_counts <- 1:buggy_num
	buggy_ratio1 <- buggy_counts / buggy_num
	cum_ratio1 <- append(cum_ratio1, 1)
	buggy_ratio1 <- append(buggy_ratio1, 1)


	cum_results2 <- cumsum(ordered_data[var_la][,1] + ordered_data[var_ld][,1])
	cum_ratio2 <- cum_results2 / total_churn
	#print(paste("NA number in cum_ratio2: ", sum(is.na(cum_ratio2)), sep=""))
	buggy_label_vector <- as.numeric(ordered_data[label][,1] == positive_label)
	#print(paste("NA number in buggy_label_vector: ", sum(is.na(buggy_label_vector)), sep=""))
	buggy_counts2 <- cumsum(buggy_label_vector)
	#print(paste("NA number in buggy_counts2: ", sum(is.na(buggy_counts2)), sep=""))
	buggy_ratio2 <- buggy_counts2 / buggy_num
	#print(paste("NA number in buggy_ratio2: ", sum(is.na(buggy_ratio2)), sep=""))
   # print(paste("Buggy num: ", buggy_num, sep=""))
   # print(paste("Test_data num: ", nrow(ordered_data), sep=""))
	optimal <- trapz(cum_ratio1, buggy_ratio1)
	#print(paste("optimal: ", optimal, sep = ""))
	method_popt <- trapz(cum_ratio2, buggy_ratio2)
	#print(paste("method_popt: ", method_popt, sep = ""))
	popt_value <- 1 - (optimal - method_popt) / (2 * optimal - 1)
	return(popt_value)
}


# self implemented, TOO SLOW!!!
Popt <- function(test_data, ordered_data, label, WORST=FALSE){
	real_buggy_data <- test_data[which(test_data[label][,1] == positive_label),]
	total_churn <- sum(test_data$real_la + test_data$real_ld)
	ordered_real_buggy_data <- real_buggy_data[order(real_buggy_data$real_la + real_buggy_data$ld),]
	n_instances <- nrow(ordered_real_buggy_data)
	line_count <- 0
	Popt_ideal_data <- NULL
	buggy_count <- 0


	for(i in 1:n_instances){
		line_count <- line_count + ordered_real_buggy_data[i,]$real_la + ordered_real_buggy_data[i,]$real_ld
		churn_percentage <- line_count / total_churn
		buggy_count <- buggy_count + 1
		buggy_percentage <- buggy_count / n_instances
		if (is.null(Popt_ideal_data)){
			Popt_ideal_data <- matrix(c(churn_percentage, buggy_percentage), nrow=1)
		}
		else{
			Popt_ideal_data <- rbind(Popt_ideal_data, matrix(c(churn_percentage, buggy_percentage), nrow=1))
		}
	}

	remaining_buggy_data <- test_data[-which(test_data[label][,1] == positive_label),]
	remaining_instances <- nrow(test_data) - n_instances
	for (i in 1:remaining_instances){
		buggy_percentage <- 1
		line_count <- line_count + remaining_buggy_data[i,]$real_la + remaining_buggy_data[i,]$real_ld
		churn_percentage <- line_count / total_churn
		Popt_ideal_data <- rbind(Popt_ideal_data, matrix(c(churn_percentage, buggy_percentage), nrow=1))
	}

	if (WORST){
		ordered_worst_buggy_data <- real_buggy_data[order(real_buggy_data$real_la + real_buggy_data$ld, decreasing=TRUE),]
		Popt_worst_data <- NULL
		line_count <- 0
		buggy_count <- 0

		for (i in 1:remaining_instances){
			buggy_percentage <- 0
			line_count <- line_count + remaining_buggy_data[i,]$real_la + remaining_buggy_data[i,]$real_ld
			churn_percentage <- line_count / total_churn
			if(is.null(Popt_worst_data)){
				Popt_worst_data <- matrix(c(churn_percentage, buggy_percentage), nrow=1)
			}
			else{
				Popt_worst_data <- rbind(Popt_worst_data, matrix(c(churn_percentage, buggy_percentage), nrow=1))
			}
		}

		for(i in 1:n_instances){
			line_count <- line_count + ordered_worst_buggy_data[i,]$real_la + ordered_worst_buggy_data[i,]$real_ld
			churn_percentage <- line_count / total_churn
			buggy_count <- buggy_count + 1
			buggy_percentage <- buggy_count / n_instances
			Popt_worst_data <- rbind(Popt_worst_data, matrix(c(churn_percentage, buggy_percentage), nrow=1))
		}
	}

	n_instances <- nrow(ordered_data)
	line_count <- 0
	buggy_count <- 0
	n_buggy <- nrow(ordered_real_buggy_data)
	Popt_method_data <- NULL
	for(i in 1:n_instances){
		line_count <- line_count + ordered_data[i,]$real_la + ordered_data[i,]$real_ld
		if(ordered_data[i,][label][,1] == positive_label){
			buggy_count <- buggy_count + 1
		}
		churn_percentage <- line_count / total_churn
		buggy_percentage <- buggy_count / n_buggy
		if(is.null(Popt_method_data)){
			Popt_method_data <- matrix(c(churn_percentage, buggy_percentage), nrow=1)
		}
		else{
			Popt_method_data <- rbind(Popt_method_data, matrix(c(churn_percentage, buggy_percentage), nrow=1))
		}
	}

	Popt_data <- cbind(data.frame(Popt_ideal_data), data.frame(Popt_method_data))

	if (WORST){
		Popt_data <- cbind(Popt_data, data.frame(Popt_worst_data))
	}

	if (WORST){
		names(Popt_data) <- c("ideal_churn", "ideal_buggy", "method_churn", "method_buggy", "worst_churn", "worst_buggy")
	}
	else{
		names(Popt_data) <- c("ideal_churn", "ideal_buggy", "method_churn", "method_buggy")
	}
	return(Popt_data)
}
