


get_log_data<-function(temp_data, log_features){
	for (feature in log_features){
		temp_vec <- temp_data[,feature]
		temp_vec[is.na(temp_vec)] <- 0
		temp_vec <- as.vector(temp_vec)
		temp_vec_num <- as.numeric(temp_vec)
		temp_vec_num[is.na(temp_vec_num)] <- 0	
		temp_vec_num[temp_vec_num>0] <- log(temp_vec_num[temp_vec_num>0]+1)
		temp_data[feature] <- temp_vec_num
		#print(feature)
	}

	return(temp_data)
}


store_result_to_frame<-function(result_frame, scores_vector){
	temp_frame <- data.frame(scores_vector)
	if (is.null(result_frame)){
		result_frame <- temp_frame
		}
	else {
		result_frame <- cbind(result_frame, temp_frame)
	}
	return(result_frame)
}

generate_factor <- function(data, co, threshold){
	return_data <- data[order(as.numeric(as.character(data[co][,1]))),]
	levels_str <- NULL
	temp <- return_data[co]
	start <- 0
	for (i in threshold){
		index <- which(threshold==i)
		end <- i		
		this_index <- which(threshold == i)
		if (this_index == length(threshold)){
			temp[which(as.numeric(temp[,1]) <= as.numeric(end) & as.numeric(temp[,1]) > as.numeric(start)),] <- paste(c(">",to_short_character(start)), collapse="")
			levels_str <- append(levels_str, paste(c(">",to_short_character(start)), collapse=""))
		}
		else{
			temp[which(as.numeric(temp[,1]) <= as.numeric(end) & as.numeric(temp[,1]) > as.numeric(start)),] <- paste(c(to_short_character(start),to_short_character(end)), collapse="-")
			levels_str <- append(levels_str, paste(c(to_short_character(start),to_short_character(end)), collapse="-"))
		}
		start <- i	
	}
	print(levels_str)
	#temp2 <- as.factor(temp[,1],order=TRUE, levels = levels_str)
	temp2 <- as.factor(temp[,1])
	temp3 <- factor(temp2, order=TRUE, levels=levels_str)
	return_data[co] <- temp3

	return(return_data)
}

to_short_character <- function(char){
	
	return_char <- char

	number <- as.numeric(char)

	if (number >= 1000){
		k <- floor(number / 1000 + 0.5)
		return_char <- paste(c(k, "K"), collapse="")
	}

	if (number < 1)
	   return_char <-  as.character(round(number,2))

    

	return(return_char)
}



generate_factor_for_category <- function(data, co, original_str, levels_str){
	#data <- data[order(as.numeric(as.character(data[co][,1]))),]
	temp <- as.character(data[co][,1])
	temp[which(temp==original_str[1])] <- levels_str[1]
	temp[which(temp==original_str[2])] <- levels_str[2]
	print(levels_str)
	#temp2 <- as.factor(temp[,1],order=TRUE, levels = levels_str)
	temp2 <- as.factor(temp)
	temp3 <- factor(temp2, order=TRUE, levels=levels_str)
	data[co] <- temp3

	return(data)
}


normalize_chi2 <- function(data, co){
	temp <- data[co][,1]
	sum <- sum(as.numeric(temp))
	temp <- as.numeric(temp)/sum

	data[co] <- temp

	return(data)
}
