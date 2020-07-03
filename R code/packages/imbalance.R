
undersampling <- function(data, class){
	positive_label <- levels(data[,class])[2]
	positive_data <- data[which(data[class][,1] == positive_label),]
	negative_data <- data[-(which(data[class][,1] == positive_label)),]
	pos_number <- nrow(positive_data)
	neg_number <- nrow(negative_data)
	max_number <- max(pos_number, neg_number)
	min_number <- min(pos_number, neg_number)
	sampled_index <- sample(max_number, min_number)
	sampled_data <- negative_data[sampled_index,]
	ret_data <- rbind(positive_data, sampled_data)
	return(ret_data)
}

resampling <- function(data, class){
	positive_label <- levels(data[,class])[2]
	positive_data <- data[which(data[class][,1] == positive_label),]
	negative_data <- data[-(which(data[class][,1] == positive_label)),]
	pos_number <- nrow(positive_data)
	neg_number <- nrow(negative_data)
	
	all_number <- nrow(data)
	sample_pos_number <- floor(all_number/2)
	sample_neg_number <- all_number - sample_pos_number

	if (pos_number < sample_pos_number){
		sample_pos <- sample(pos_number, sample_pos_number, replace=TRUE)
	}
	else{
		sample_pos <- sample(pos_number, sample_pos_number)
	}
	if (neg_number < sample_neg_number){
		sample_neg <- sample(neg_number, sample_neg_number, replace=TRUE)
	}
	else {
		sample_neg <- sample(neg_number, sample_neg_number)
	}
	
	sample_pos_data <- positive_data[sample_pos,]
	sample_neg_data <- negative_data[sample_neg,]
	ret_data <- rbind(sample_pos_data, sample_neg_data)
	
	return(ret_data)
}