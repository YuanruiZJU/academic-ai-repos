from paper_analysis import get_lda_represent

if __name__ == '__main__':
    text = """
The underlying idea of multitask learning is that learning 
tasks jointly is better than learning each task individually. 
In particular, if only a few training examples are available for each task, 
sharing a jointly trained representation improves classification performance. 
In this paper, we propose a novel multitask learning method that learns a low-dimensional 
representation jointly with the corresponding classifiers, which are then able 
to profit from the latent inter-class correlations. Our method scales with respect 
to the original feature dimension and can be used with high-dimensional image 
descriptors such as the Fisher Vector. Furthermore, it consistently outperforms the current 
state of the art on the SUN397 scene classification benchmark with varying amounts of training data. """
    print(get_lda_represent(text))