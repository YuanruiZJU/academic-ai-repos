from configuration import conf
from parse import parse
import os


projects = ['ARAE', 'PN_GAN', 'generalisation-humans-DNNs', 'MADGAN', 'MSRN-PyTorch',
            'cvpr2018-shape-completion', 'Deep-Expander-Networks', 'Deep-Variational-Reinforcement-Learning',
            'label-shift', 'multimodal-vae-public', 'DSSPN', 'Person-reID_GAN', 'Fast-Slow-LSTM', 'bianan',
            'ram_person_id', 'BOP', 'mcg', 'Saliency-HDCT']

data = parse(conf.md_path)
for d in data:
    for p in projects:
        if p in d['code']:
            if not os.path.exists(os.path.join(conf.repo_path, p)):
                print(d['code'])
                print(p)
                print(d['title'])
