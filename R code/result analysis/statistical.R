

repo_result <- read.csv("D://our.csv")
paper_result <- read.csv("D://topic.csv")


measures <- c("auc_scores", "precision_popular", "recall_popular", "f1_popular", "precision_unpopular", "recall_unpopular", "f1_unpopular")

for (m in measures){
	print("==============================================================")
	print(m)
	print(wilcox.test(repo_result[,m], paper_result[,m], pair=TRUE, alternative="g"))
	print(cliff.delta(repo_result[,m], paper_result[,m]))
		
}

