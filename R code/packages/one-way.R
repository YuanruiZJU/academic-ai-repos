
source("C://Rwork/JITalibaba/packages/measures.R")


one_way <- function(train_data, test_data, varnames, label, type="1"){
	mean_scores <- c()
	for (var in varnames){
		ordered_data <- train_data[order(train_data[var][,1]),]
		results <- calculate_cost_effectiveness2(ordered_data, 0.2, "real_la", "real_ld",  label)

		buggy_count <- results[1]
		change_count <- results[2]		

		precision20 <- buggy_count / change_count
		recall20 <- buggy_count / length(which(test_data[label][,1]==positive_label))
		F1_score20 <- 2 * precision20 * recall20 / (precision20 + recall20)

		popt_value <- Popt2(ordered_data, "real_la", "real_ld",  label)
		if (type == "1"){
			mean_scores <- append(mean_scores, mean(c(precision20, recall20, F1_score20, popt_value)))			
		}
		if (type == "2"){
			mean_scores <- append(mean_scores, recall20)
		}
	}
	#print(mean_scores)
	best_metric <- varnames[which(max(mean_scores) == mean_scores)]
	#print(best_metric)
	auc_score <- roc(test_data[label][,1], test_data[best_metric][,1])
	auc_score <- auc_score["auc"][[1]][1]
	ordered_data <- test_data[order(test_data[best_metric][,1]),]	
	results_best_metric <- calculate_cost_effectiveness2(ordered_data, 0.2, "real_la", "real_ld",  label)
	buggy_count <- results_best_metric[1]
	change_count <- results_best_metric[2]
	first_buggy <- results_best_metric[3]

	#precision20 <- buggy_count / change_count
	#recall20 <- buggy_count / length(which(test_data[label][,1]==positive_label))
	#F1_score20 <- 2 * precision20 * recall20 / (precision20 + recall20)

	popt_value <- Popt2(ordered_data, "real_la", "real_ld",  label)

	scores <- c(buggy_count, change_count, first_buggy, popt_value, auc_score)
	return(scores)
}