from torch.nn import Embedding, Module
from typing import List
import torch
import copy
from collections import deque

class TokenTensorizer(Module):

    def __init__(self, num_embeddings: int, embedding_dim: int, max_len, pretrain_path: str = None):
        """

        :param num_embeddings: 规定了一个句子长度，大于该长度直接截掉
        :param embedding_dim: word embedding的维度
        :param pre_train_path: 默认为空，如果不为空则按照该路径加载预训练词向量
        """
        super(TokenTensorizer, self).__init__()
        self.num_embeddings = num_embeddings
        self.embedding_dim = embedding_dim
        self.pretrain_path = pretrain_path
        self.max_len = max_len

    def padding(self, data: {}, padding_number) -> [List]:
        """

        :param text: DataSource返回的"text"，是[List]格式
        :param pad_token: pad字符
        :return: 将每个List统一长度后的列表
        """
        text_processed = deque()
        for string in data["text"]:
            len_string = len(string)
            if len_string > self.max_len:
                processed = deque([string[i] for i in range(self.max_len)])
                text_processed.append(processed)
            elif len_string < self.max_len:
                processed = copy.deepcopy(string)
                processed.extend([padding_number] * (self.max_len - len_string))
                text_processed.append(processed)
            else:
                text_processed.append(string)

        label_processed = deque()
        for label in data["label"]:
            len_label = len(label)
            if len_string > self.max_len:
                processed = copy.deepcopy(label)[:self.max_len]
                label_processed.append(processed)
            elif len_label < self.max_len:
                processed = copy.deepcopy(label)
                processed.extend([-1] * (self.max_len - len_label))
                label_processed.append(processed)
            else:
                label_processed.append(processed)


        return text_processed, label_processed

    def forward(self, data):
        """

        :param data:  DataSource返回的数据
        :param pad_token: 使用的pad字符，在词典中未出现的字符
        :return:对应于data的wordEmbedding
        """
        if self.pretrain_path is not None:
            #定义使用预训练模型
            pass
        else:
            embedding = Embedding(num_embeddings= self.num_embeddings + 1,
                                  embedding_dim= self.embedding_dim,
                                  scale_grad_by_freq= True)

            text, label = self.padding(data, self.num_embeddings)
            text = torch.LongTensor(text)
            label = torch.LongTensor(label)

            text_embedding = embedding(text).detach_()

            return text_embedding, label

if __name__ == "__main__":
    from Source import DataSource
    from Source import text_paser
    test_data_path = {"text_filepath": "./de-en",
                 "text_filename": ["IWSLT16.TED.dev2010.de-en.en.xml"],
                 "label_filepath": "./de-en",
                 "label_filename": ["IWSLT16.TED.dev2010.de-en.de.xml"]}
    train_data_path = {"text_filepath": "./de-en",
                       "text_filename": ["train.tags.de-en.en"],
                       "label_filepath": "./de-en",
                       "label_filename": ["train.tags.de-en.de"]}
    #加载数据
    datasource = DataSource(train_data_path)
    data = datasource(text_paser)

    #得到wordEmbedding
    embedder = TokenTensorizer(num_embeddings= len(list(data["text_word_to_indexer"].keys())), embedding_dim= 100, max_len= 20, pretrain_path= None)
    embedding, label = embedder(data)
    print(embedding[0])
    print(label[0].size())
